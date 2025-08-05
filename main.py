# main.py
import os
import uvicorn
import json
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from fastapi import FastAPI, Request

import bot_handlers

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando o bot do Telegram...")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    bot_builder = Application.builder().token(TELEGRAM_TOKEN)
    bot_app = bot_builder.build()

    bot_app.add_handler(CommandHandler("start", bot_handlers.start))
    bot_app.add_handler(CallbackQueryHandler(bot_handlers.plan_selection))

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
    data = await request.json()
    print("--- Webhook do Mercado Pago Recebido ---")
    print(json.dumps(data, indent=2))
    
    user_id = data.get("external_reference")
    if user_id:
        bot_app = request.app.state.bot_app
        try:
            await bot_app.bot.send_message(
                chat_id=int(user_id),
                text="Seu pagamento foi confirmado! ✅"
            )
        except Exception as e:
            print(f"Erro ao enviar mensagem de confirmação: {e}")
    
    return {"status": "ok"}

if __name__ == "__main__":
    print("Iniciando o servidor Uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=8000)