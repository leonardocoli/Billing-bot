# Dockerfile

# Use uma imagem base leve e moderna do Python
FROM python:3.10-slim

# Instala o cliente do SQLite3 dentro da imagem
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o resto do código do projeto para o contêiner
COPY . .

# Comando que será executado quando o contêiner iniciar
# Ele rodará nosso servidor web na porta 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]