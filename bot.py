# bot.py
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import storage

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    storage.users.add(user_id)
    await update.message.reply_text("👋 Hello! I'm your assistant bot.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text
    storage.users.add(user_id)
    storage.messages.append((user_id, message))
    await update.message.reply_text(f"✅ Got your message: {message}")

async def broadcast_message(message: str):
    if not storage.application:
        return
    for user in storage.users:
        try:
            await storage.application.bot.send_message(chat_id=user, text=message)
        except Exception as e:
            print(f"Failed to message user {user}: {e}")

def run_bot():
    application = ApplicationBuilder().token(TOKEN).build()
    storage.application = application
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    storage.bot_running = True
    asyncio.run(application.run_polling())
