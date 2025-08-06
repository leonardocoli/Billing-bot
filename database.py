# database.py
import sqlite3
import datetime
import os # Importa a biblioteca 'os' para manipulação de diretórios

# Garante que o diretório de dados exista antes de qualquer operação.
# Se a pasta 'data' não existir, este comando a criará.
os.makedirs("data", exist_ok=True)

# O nome do banco agora inclui o caminho para a pasta 'data', que está mapeada pelo Docker.
DB_NAME = "data/bot_database.db"

def init_db():
    """Cria as tabelas do banco de dados se elas não existirem."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Criar tabela de usuários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER UNIQUE NOT NULL,
        first_name TEXT,
        username TEXT,
        join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Criar tabela de assinaturas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        plan_name TEXT NOT NULL,
        purchase_date TIMESTAMP NOT NULL,
        expiration_date TIMESTAMP,
        status TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    conn.commit()
    conn.close()
    print("Banco de dados inicializado.")

def add_user(chat_id, first_name, username):
    """Adiciona um novo usuário ou atualiza o nome/username se ele já existir."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Insere o usuário se o chat_id não existir na tabela
    cursor.execute("INSERT OR IGNORE INTO users (chat_id, first_name, username) VALUES (?, ?, ?)", 
                   (chat_id, first_name, username))
    
    # Atualiza o nome e username caso tenham mudado em uma visita futura
    cursor.execute("UPDATE users SET first_name = ?, username = ? WHERE chat_id = ?", 
                   (first_name, username, chat_id))

    conn.commit()
    conn.close()

def create_subscription(chat_id, plan_name):
    """Cria um novo registro de assinatura para um usuário, desativando as antigas."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Pega o ID interno do usuário a partir do chat_id
    cursor.execute("SELECT id FROM users WHERE chat_id = ?", (chat_id,))
    user = cursor.fetchone()
    if not user:
        print(f"ERRO: Usuário com chat_id {chat_id} não encontrado no banco de dados.")
        conn.close()
        return

    user_id = user[0]
    purchase_date = datetime.datetime.now()
    expiration_date = None
    status = "active"

    # Define a data de expiração com base no nome do plano
    if "Mensal" in plan_name:
        expiration_date = purchase_date + datetime.timedelta(days=30)
    elif "Semestral" in plan_name:
        expiration_date = purchase_date + datetime.timedelta(days=182) # Aprox. 6 meses
    elif "Anual" in plan_name:
        expiration_date = purchase_date + datetime.timedelta(days=365)
    # Para o plano "Vitalício", expiration_date permanece None (nunca expira)

    # Garante que assinaturas antigas do mesmo usuário sejam marcadas como 'expired'
    cursor.execute("UPDATE subscriptions SET status = 'expired' WHERE user_id = ? AND status = 'active'", (user_id,))

    # Insere a nova assinatura ativa
    cursor.execute("""
    INSERT INTO subscriptions (user_id, plan_name, purchase_date, expiration_date, status)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, plan_name, purchase_date, expiration_date, status))
    
    conn.commit()
    conn.close()
    print(f"Assinatura '{plan_name}' criada com sucesso para o usuário {chat_id}.")