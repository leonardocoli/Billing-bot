# test_connection.py
import requests

print("--- INICIANDO TESTE DE CONEXÃO ---")

print("\n[1] Tentando se conectar ao Google...")
try:
    response_google = requests.get("https://www.google.com", timeout=10)
    print(f"--> SUCESSO! Google respondeu com status: {response_google.status_code}")
except Exception as e:
    print(f"--> FALHA ao conectar com o Google: {e}\n")

print("\n[2] Tentando se conectar à API do Telegram...")
try:
    url_telegram = "https://api.telegram.org"
    response_telegram = requests.get(url_telegram, timeout=10)
    print(f"--> SUCESSO! Telegram respondeu com status: {response_telegram.status_code}")
except Exception as e:
    print(f"--> FALHA ao conectar com o Telegram: {e}\n")

print("\n--- TESTE DE CONEXÃO FINALIZADO ---")