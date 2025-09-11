
from telegram import ReplyKeyboardMarkup
from telegram.ext import MessageHandler, filters
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_markup = ReplyKeyboardMarkup([['Help', 'Info']], resize_keyboard=True)
    await update.message.reply_text(
        "Hello ! I am your bot. How can I Help You ?",
        reply_markup=reply_markup
    )
    chat_id = update.effective_chat.id
    logging.info(f"Chat ID: {chat_id}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"{update.message.text}")

if __name__ == "__main__":
        

    load_dotenv()
    application = Application.builder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(CommandHandler("info", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.run_polling(allowed_updates=Update.ALL_TYPES)
 

#####  the bot respond to  message   ###########



async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"{update.message.text}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_markup = ReplyKeyboardMarkup([['Help', 'Info']], resize_keyboard=True)
    await update.message.reply_text(
        "Hello! I am your bot. How can I Help You ?",
        reply_markup=reply_markup
    )
    chat_id = update.effective_chat.id
    logging.info(f"Chat ID: {chat_id}")



application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

