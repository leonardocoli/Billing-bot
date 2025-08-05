# payment_handler.py
import requests
import os
import json

MP_API_URL = "https://api.mercadopago.com/checkout/preferences"
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def create_payment_link(plan_name: str, price: float, user_id: int):
    """Cria uma preferência de pagamento no Mercado Pago e retorna o link."""
    
    headers = {
        "Authorization": f"Bearer {MP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    # username do bot no telegram
    bot_username = "meugerenciadordeassinaturas_bot"

    payload = {
        "items": [
            {
                "title": plan_name,
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": price
            }
        ],
        "back_urls": {
            "success": f"https://t.me/{bot_username}",
            "failure": f"https://t.me/{bot_username}",
            "pending": f"https://t.me/{bot_username}"
        },
        "auto_return": "approved",
        "notification_url": f"{WEBHOOK_URL}/webhook/mp",
        "external_reference": str(user_id)
    }

    try:
        response = requests.post(MP_API_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        data = response.json()
        payment_link = data.get("sandbox_init_point", data.get("init_point"))
        return payment_link
    except requests.exceptions.RequestException as e:
        print(f"Erro ao criar link de pagamento: {e}")
        # A LINHA MAIS IMPORTANTE PARA O DIAGNÓSTICO É ESTA ABAIXO:
        if e.response:
            print(f"Detalhes do erro da API: {e.response.json()}")
        return None