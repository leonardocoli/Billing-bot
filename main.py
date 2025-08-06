# main.py
import os
import uvicorn
import json
import asyncio
import requests
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import Bot
from fastapi import FastAPI, Request

import bot_handlers
import database

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()


async def send_onboarding_sequence(chat_id: int, bot: Bot):
    """
    Envia uma sequência de mensagens de boas-vindas em segundo plano.
    """
    try:
        # Espera 24 horas (86400 segundos) para a primeira dica
        await asyncio.sleep(86400) 
        
        # MENSAGEM 2 (MELHORADA)
        onboarding_message_1 = (
            "👋 Olá! Passando para dar uma dica rápida para você aproveitar ao máximo seu PlexTower:\n\n"
            "**Crie Coleções Inteligentes!** Você pode agrupar seus filmes por ator, diretor ou até mesmo por uma década específica. "
            "Vá na sua biblioteca, filtre como desejar e clique em 'Salvar como Coleção Inteligente'. É uma ótima forma de organizar seu conteúdo!"
        )
        await bot.send_message(chat_id=chat_id, text=onboarding_message_1)
        
        # Espera mais 48 horas para a segunda mensagem
        await asyncio.sleep(172800) 

        # MENSAGEM 3 (AGORA FUNCIONAL COM O /suporte)
        onboarding_message_2 = "🚀 Esperamos que esteja gostando! Se tiver qualquer dúvida, é só usar o comando /suporte. Estamos aqui para ajudar!"
        await bot.send_message(chat_id=chat_id, text=onboarding_message_2)

    except Exception as e:
        print(f"Erro ao enviar mensagem de onboarding para {chat_id}: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação. Inicia o bot do Telegram
    e o banco de dados quando o servidor sobe, e os finaliza quando o servidor desce.
    """
    print("Inicializando o banco de dados...")
    database.init_db()
    
    print("Iniciando o bot do Telegram...")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    bot_builder = Application.builder().token(TELEGRAM_TOKEN)
    bot_app = bot_builder.build()

    # Adiciona os handlers de comando
    bot_app.add_handler(CommandHandler("start", bot_handlers.start))
    bot_app.add_handler(CallbackQueryHandler(bot_handlers.plan_selection))
    bot_app.add_handler(CommandHandler("suporte", bot_handlers.support)) # <-- NOVO HANDLER DE SUPORTE

    await bot_app.initialize()
    await bot_app.updater.start_polling()
    await bot_app.start()
    
    app.state.bot_app = bot_app
    
    yield
    
    print("Finalizando o bot do Telegram...")
    await bot_app.updater.stop()
    await bot_app.stop()
    await bot_app.shutdown()


app = FastAPI(lifespan=lifespan)


@app.post("/webhook/mp")
async def receive_mp_webhook(request: Request):
    """
    Recebe, verifica, processa as notificações de pagamento e notifica o administrador.
    """
    data = await request.json()
    print("--- Webhook Inicial Recebido ---")
    print(json.dumps(data, indent=2))

    if data.get("type") == "payment":
        payment_id = data.get("data", {}).get("id")
        if not payment_id:
            return {"status": "ignorado", "motivo": "sem ID de pagamento"}

        MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
        headers = {"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}
        
        response = requests.get(f"https://api.mercadopago.com/v1/payments/{payment_id}", headers=headers)
        
        if response.status_code != 200:
            return {"status": "erro", "motivo": "falha ao consultar API"}
            
        payment_details = response.json()
        print("--- Detalhes Completos do Pagamento Recebidos ---")
        print(json.dumps(payment_details, indent=2))

        if payment_details.get("status") == "approved":
            external_reference = payment_details.get("external_reference")
            plan_name = payment_details.get("description")
            payer_email = payment_details.get("payer", {}).get("email")
            
            if not external_reference or not plan_name:
                return {"status": "erro", "motivo": "dados faltando na API"}

            chat_id = int(external_reference)
            database.create_subscription(chat_id=chat_id, plan_name=plan_name)
            
            bot_app = request.app.state.bot_app
            ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

            # MENSAGEM PARA O CLIENTE (ATUALIZADA)
            await bot_app.bot.send_message(
                chat_id=chat_id,
                text=f"Pagamento para o plano {plan_name} confirmado com sucesso! ✅\n\nSeja muito bem-vindo(a)! Seu link de acesso exclusivo será enviado em breve pelo administrador."
            )

            # MENSAGEM PARA O ADMINISTRADOR (NOVA)
            admin_message = (
                f"🔔 **Nova Venda Realizada!** 🔔\n\n"
                f"**Plano:** {plan_name}\n"
                f"**Email do Pagador:** {payer_email}\n"
                f"**Telegram User ID:** `{chat_id}`\n\n"
                f"**AÇÃO NECESSÁRIA:** Por favor, gere e envie o link de acesso para este usuário."
            )
            if ADMIN_CHAT_ID:
                await bot_app.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message, parse_mode="Markdown")

            asyncio.create_task(send_onboarding_sequence(chat_id=chat_id, bot=bot_app.bot))
            
            return {"status": "processado com sucesso"}

    return {"status": "evento não processado"}


if __name__ == "__main__":
    print("Iniciando o servidor Uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=8000)