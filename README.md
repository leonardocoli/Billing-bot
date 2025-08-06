# Bot de Pagamentos PlexTower - Instruções de Implantação

Este documento descreve como configurar e executar o bot de pagamentos em um servidor de produção usando Docker.

### 1. Pré-requisitos

O servidor deve ter os seguintes softwares instalados:
* **Docker**
* **Docker Compose**

### 2. Configuração

1.  **Estrutura de Arquivos:** Descompacte o arquivo `.zip` em um diretório apropriado no servidor (ex: `/opt/plextower-bot`).

2.  **Variáveis de Ambiente:**
    * Abra o arquivo `.env` com um editor de texto e preencha todas as variáveis com as chaves de produção:
        * `TELEGRAM_TOKEN`: Token do bot do Telegram. 
        * `MP_ACCESS_TOKEN`: **Access Token de PRODUÇÃO** do Mercado Pago.
        * `WEBHOOK_URL`: A URL pública e permanente deste servidor (sem barra `/` no final).
        * `ADMIN_CHAT_ID`: O ID de usuário do Telegram do administrador que receberá as notificações.

### 3. Configuração do Webhook no Mercado Pago

Antes de iniciar o bot, é necessário configurar o endpoint do webhook no painel do Mercado Pago.

* Acesse a aplicação correspondente no painel de desenvolvedor.
* Na seção **Webhooks**, configure a **URL de Produção** para:
    `[SUA_WEBHOOK_URL_DO_ARQUIVO_.ENV]/webhook/mp`
* Garanta que o evento **"Pagamentos"** está ativado.

### 4. Execução

Todos os comandos devem ser executados de dentro do diretório do projeto.

1.  **Build da Imagem Docker:**
    Este comando lê o `Dockerfile` e constrói a imagem da aplicação.
    ```bash
    docker-compose build
    ```

2.  **Iniciar a Aplicação:**
    Este comando inicia o container em modo "detached" (em segundo plano). Graças à política `restart: always` no `docker-compose.yml`, o bot será reiniciado automaticamente em caso de falha ou se o servidor for reiniciado.
    ```bash
    docker-compose up -d
    ```

### 5. Verificação e Manutenção

* **Verificar se o container está rodando:**
    ```bash
    docker ps
    ```
    *Você deve ver um container com o nome `billing-bot` na lista.*

* **Verificar os logs em tempo real:**
    ```bash
    docker-compose logs -f
    ```

* **Parar a aplicação:**
    ```bash
    docker-compose down
    ```


### 6. Acessando o Banco de Dados (SQLite)

O banco de dados do bot é um arquivo chamado `bot_database.db`, localizado na subpasta `data/`. Graças ao Docker Volume, este arquivo fica salvo de forma segura no servidor. Existem duas maneiras de consultá-lo:

---
#### **Método A: Acesso Direto no Servidor (Recomendado)**

Este método acessa o arquivo do banco de dados diretamente no sistema de arquivos do servidor. É mais simples e direto.

**Pré-requisito:** O utilitário `sqlite3` precisa estar instalado no servidor.
```bash
sudo apt-get update && sudo apt-get install -y sqlite3
```

**Passos:**
1.  No terminal do servidor, navegue até o diretório do projeto (ex: `cd /opt/plextower-bot`).
2.  Execute o cliente do SQLite apontando para o arquivo do banco de dados:
    ```bash
    sqlite3 data/bot_database.db
    ```
3.  O prompt mudará para `sqlite>`. Para formatar a saída e consultar os dados, use os comandos:
    ```sql
    .headers on
    .mode column
    SELECT * FROM users;
    SELECT * FROM subscriptions;
    ```
4.  Para sair, digite `.exit`.

* **Vantagens:** Simples, rápido, não interfere com o container em execução.
* **Desvantagens:** Requer a instalação de um pacote (`sqlite3`) no servidor.

---
#### **Método B: Acesso Dentro do Container Docker**

Este método permite acessar o banco de dados "dentro" do container do bot, sem precisar instalar nada extra no servidor.

**Pré-requisito:** O container do bot (`billing-bot`) precisa estar em execução.

**Passos:**
1.  Abra um terminal interativo dentro do container em execução:
    ```bash
    docker exec -it billing-bot /bin/sh
    ```
2.  O prompt de comando irá mudar. Você agora está dentro do container. O utilitário `sqlite3` já está instalado na imagem. Execute-o:
    ```sh
    sqlite3 data/bot_database.db
    ```
3.  O prompt mudará para `sqlite>`. Use os mesmos comandos SQL para consultar os dados:
    ```sql
    .headers on
    .mode column
    SELECT * FROM users;
    ```
4.  Para sair, digite `.exit` (para fechar o SQLite), e depois `exit` novamente (para fechar a sessão do container).

* **Vantagens:** Não requer instalação de pacotes no servidor. Usa as ferramentas já contidas na imagem Docker.
* **Desvantagens:** Um pouco mais complexo (requer o comando `docker exec`).
