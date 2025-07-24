import asyncio
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
from telegram.error import Conflict
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = ApplicationBuilder().token(Config.TELEGRAM_BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Received /start from user {update.effective_user.id}")
    await update.message.reply_text("Hello! The bot is running with Flask and threading.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Received /help from user {update.effective_user.id}")
    await update.message.reply_text("This is the help command. Use /start to begin.")

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Received /hello from user {update.effective_user.id}")
    await update.message.reply_text("ក្លាហាន")

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("help", help_command))

def run_telegram_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Delete webhook before polling
        loop.run_until_complete(app.bot.delete_webhook())
        logger.info("Webhook deleted, starting polling...")
        loop.run_until_complete(app.run_polling(stop_signals=None))
    except Conflict:
        logger.error("Conflict error: Another bot instance is running. Please stop other instances.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        loop.close()

