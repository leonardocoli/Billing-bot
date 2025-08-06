# payment_handler.py
import requests
import os
import json

# Usaremos apenas o endpoint de "Preferência de Pagamento" para todos os planos
MP_API_URL_PREFERENCES = "https://api.mercadopago.com/checkout/preferences"

# Carrega as variáveis de ambiente
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def create_payment_link(plan_name: str, price: float, user_id: int):
    """
    Cria uma preferência de pagamento dinamicamente para um item
    e associa ao usuário através do external_reference.
    """
    # IMPORTANTE: Garanta que este é o seu username correto, em minúsculas.
    bot_username = "meugerenciadoreassinaturas_bot" 

    headers = {
        "Authorization": f"Bearer {MP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    # Payload que cria o item de pagamento "na hora"
    payload = {
        "items": [
            {
                "title": plan_name,
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": price
            }
        ],
        "external_reference": str(user_id),
        "notification_url": f"{WEBHOOK_URL}/webhook/mp",
        "back_urls": {
            "success": f"https://t.me/{bot_username}",
            "failure": f"https://t.me/{bot_username}",
            "pending": f"https://t.me/{bot_username}"
        },
        "auto_return": "approved",
    }

    try:
        print(f"Enviando para API do MP ({MP_API_URL_PREFERENCES}): {json.dumps(payload, indent=2)}")
        response = requests.post(MP_API_URL_PREFERENCES, data=json.dumps(payload), headers=headers)
        response.raise_for_status() # Lança um erro se a resposta for 4xx ou 5xx
        data = response.json()
        
        payment_link = data.get("init_point", data.get("sandbox_init_point"))
        return payment_link

    except requests.exceptions.RequestException as e:
        print(f"\n--- ERRO DETECTADO AO CHAMAR A API DO MERCADO PAGO ---")
        print(f"Erro genérico: {e}")
        
        if e.response is not None:
            print(f"Status Code da Resposta: {e.response.status_code}")
            print(f"Resposta em formato TEXTO: {e.response.text}")
            try:
                print(f"Resposta em formato JSON: {e.response.json()}")
            except ValueError:
                print("AVISO: A resposta da API não é um JSON válido.")
        else:
            print("Não houve resposta do servidor (pode ser um erro de conexão/DNS).")
        
        print(f"--- FIM DO LOG DE ERRO ---\n")
        return None