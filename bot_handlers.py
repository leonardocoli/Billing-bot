# bot_handlers.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from payment_handler import create_payment_link

# Nossos planos definidos
PLANOS = {
    "Plano Ouro": {"price": 99.90, "emoji": "💎"},
    "Plano Prata": {"price": 59.90, "emoji": "🥈"},
    "Plano Bronze": {"price": 29.90, "emoji": "🥉"}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envia a mensagem inicial com os planos."""
    keyboard = []
    for name, data in PLANOS.items():
        button = InlineKeyboardButton(
            f"{data['emoji']} {name} - R$ {data['price']:.2f}",
            callback_data=name
        )
        keyboard.append([button])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Olá! Sou seu assistente de assinaturas. Escolha um dos nossos planos:",
        reply_markup=reply_markup
    )

async def plan_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa a escolha do plano e gera o link de pagamento."""
    query = update.callback_query
    await query.answer()

    plan_name = query.data
    plan_info = PLANOS.get(plan_name)

    if not plan_info:
        await query.edit_message_text("Plano inválido. Por favor, use /start para tentar novamente.")
        return

    user_id = query.from_user.id
    price = plan_info["price"]

    await query.edit_message_text(f"Gerando seu link de pagamento para o {plan_name}...")

    payment_link = create_payment_link(plan_name, price, user_id)

    if payment_link:
        keyboard = [[InlineKeyboardButton("✅ Pagar Agora com Segurança", url=payment_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"Excelente escolha! Para assinar o {plan_name}, clique no botão abaixo:",
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text(
            "Desculpe, não consegui gerar seu link de pagamento. Tente novamente em alguns instantes."
        )