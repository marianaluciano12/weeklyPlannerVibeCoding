import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from main import process_assistant_message

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID")


def is_authorized(update: Update) -> bool:
    if not ALLOWED_USER_ID:
        return True

    if not update.effective_user:
        return False

    return str(update.effective_user.id) == ALLOWED_USER_ID


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not is_authorized(update):
        await update.message.reply_text(
            "Não tens autorização para usar este assistente."
        )
        return

    await update.message.reply_text(
        "Olá! Sou o teu assistente de calendário.\n\n"
        "Podes escrever, por exemplo:\n"
        "• Tenho dentista amanhã às 10:00\n"
        "• Quero praticar piano todos os dias esta semana\n"
        "• Quero ir ao ginásio 3 vezes esta semana"
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await update.message.reply_text(
        "Envia uma mensagem com o que queres agendar.\n\n"
        "Exemplo:\n"
        "Tenho cinema com amigos na sexta das 21:00 às 23:00"
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message or not update.message.text:
        return

    if not is_authorized(update):
        await update.message.reply_text(
            "Não tens autorização para usar este assistente."
        )
        return

    message = update.message.text

    await update.message.reply_text(
        "A analisar o teu pedido..."
    )

    try:
        result = process_assistant_message(
            message=message,
            preferences=None
        )

        response_message = result.get(
            "message",
            "O pedido foi processado."
        )

        await update.message.reply_text(response_message)

    except Exception as error:
        print("Telegram bot error:", error)

        await update.message.reply_text(
            "Ocorreu um erro ao processar o pedido."
        )


def main() -> None:
    application = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start_command)
    )

    application.add_handler(
        CommandHandler("help", help_command)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("Telegram bot is running...")

    application.run_polling()


if __name__ == "__main__":
    main()