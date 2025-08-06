# bot_handlers.py
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database
from payment_handler import create_payment_link

# Usaremos a versão do `payment_handler` que gera o link dinamicamente
# Se for usar a versão com IDs pré-criados, este dicionário e a função plan_selection
# devem ser ajustados.

PLANOS = {
    "mensal": {"name": "Mensal", "price": 17.90, "emoji": "🪙"},
    "semestral": {"name": "Semestral", "price": 97.90, "emoji": "🥉"},
    "anual": {"name": "Anual", "price": 157.90, "emoji": "🥈"},
    "vitalicio": {"name": "Vitalício", "price": 297.00, "emoji": "🥇"}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com o comando /start, registra o usuário e envia a descrição dos planos."""
    user = update.effective_user
    database.add_user(chat_id=user.id, first_name=user.first_name, username=user.username)

    text = """Olá! 👋 Fico feliz em te ajudar a escolher o melhor plano de acesso ao PlexTower.

Trabalhamos com flexibilidade e economia para você. Veja as opções que oferecemos:
---
🪙 **Plano Mensal**
Ideal para experimentar ou para quem prefere a liberdade de um compromisso curto.
▸ **Valor:** R$ 17,90 por mês.
---
🥉 **Plano Semestral**
Uma ótima opção para economizar no médio prazo.
▸ **Valor:** R$ 97,90 a cada 6 meses.
*Isso equivale a R$ 16,31 por mês, um **desconto de 9%**!*
---
🥈 **Plano Anual (O mais popular)**
Nosso melhor custo-benefício! Perfeito para quem já conhece e adora o serviço.
▸ **Valor:** R$ 157,90 por ano.
*Sai por apenas R$ 13,16 por mês, o que representa um **desconto de 26%**!*
---
🥇 **Plano Vitalício (Acesso para sempre!)**
A tranquilidade definitiva. Pague uma única vez e não se preocupe nunca mais com renovações.
▸ **Valor:** Pagamento único de R$ 297,00.
*É o equivalente a menos de 17 meses do plano mensal para ter acesso ilimitado para sempre!*"""
    
    await update.message.reply_text(text)

    keyboard = [
        [InlineKeyboardButton(f"{data['emoji']} {data['name']}", callback_data=key)]
        for key, data in PLANOS.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Agora, qual dessas opções faz mais sentido para você?", reply_markup=reply_markup)

async def plan_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa a escolha do plano e gera o link de pagamento."""
    query = update.callback_query
    await query.answer()

    plan_key = query.data
    plan_info = PLANOS.get(plan_key)

    if not plan_info:
        await query.edit_message_text("Plano inválido. Por favor, use /start para tentar novamente.")
        return

    user_id = query.from_user.id
    plan_name = plan_info["name"]
    price = plan_info["price"]
    
    await query.edit_message_text(f"Gerando seu link de pagamento para o plano {plan_name}...")

    # Usando a versão simplificada do `create_payment_link` com 3 argumentos
    payment_link = create_payment_link(plan_name, price, user_id)

    if payment_link:
        keyboard = [[InlineKeyboardButton("✅ Pagar Agora com Segurança", url=payment_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"Excelente escolha! Para assinar o plano {plan_name}, clique no botão abaixo:",
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text(
            "Desculpe, não consegui gerar seu link de pagamento. Tente novamente em alguns instantes."
        )

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com o comando /suporte e notifica o administrador."""
    user = update.effective_user
    ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
    
    # Mensagem para o usuário
    user_message = (
        "Você solicitou suporte. Um administrador foi notificado e entrará em contato com você em breve através do Telegram.\n\n"
        "Se desejar, pode adiantar o assunto descrevendo seu problema ou dúvida na próxima mensagem."
    )
    await update.message.reply_text(user_message)
    
    # Mensagem de notificação para o administrador
    if ADMIN_CHAT_ID:
        admin_message = (
            f"⚠️ **Pedido de Suporte Recebido** ⚠️\n\n"
            f"**Usuário:** {user.first_name} (Username: @{user.username})\n"
            f"**User ID:** `{user.id}`\n\n"
            f"**AÇÃO NECESSÁRIA:** Por favor, entre em contato com este usuário para atendê-lo."
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message, parse_mode="Markdown")