import asyncio
import logging
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

from assistant_service import process_assistant_message
from models import PlanningPreferences


load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID")

DEFAULT_PREFERENCES = PlanningPreferences().model_dump()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


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
    if not update.message:
        return

    if not is_authorized(update):
        await update.message.reply_text(
            "Não tens autorização para usar este assistente."
        )
        return

    await update.message.reply_text(
        "Olá! Sou o teu assistente de calendário.\n\n"
        "Exemplos:\n"
        "• Tenho dentista amanhã às 10:00\n"
        "• Quero praticar piano hoje às 22h00\n"
        "• Quero ir ao ginásio 3 vezes esta semana"
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message:
        return

    await update.message.reply_text(
        "Envia uma mensagem com o que queres agendar.\n\n"
        "Exemplo:\n"
        "Tenho cinema com amigos na sexta das 21:00 às 23:00"
    )


async def id_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message or not update.effective_user:
        return

    await update.message.reply_text(
        f"O teu Telegram User ID é: {update.effective_user.id}"
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

    message = update.message.text.strip()

    await update.message.reply_text("A analisar o teu pedido...")

    try:
        result = await asyncio.to_thread(
            process_assistant_message,
            message,
            DEFAULT_PREFERENCES,
        )

        response_message = result.get(
            "message",
            "O pedido foi processado.",
        )

        await update.message.reply_text(
            response_message,
            disable_web_page_preview=True,
        )

    except Exception as error:
        logger.exception("Erro ao processar mensagem do Telegram")

        await update.message.reply_text(
            f"Ocorreu um erro ao processar o pedido: {error}"
        )


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    logger.exception(
        "Erro não tratado no bot",
        exc_info=context.error,
    )


def main() -> None:
    application = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("id", id_command))
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    application.add_error_handler(error_handler)

    print("Telegram bot is running...")

    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
