import streamlit as st
import asyncio
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === Telegram Bot Logic (Async) ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm a Telegram bot running inside Streamlit.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send /start to get a greeting!")

# === Bot Runner ===
def run_telegram_bot():
    async def main():
        app = ApplicationBuilder().token("7240504796:AAGQ3kpkT9cjtRvG_gwt7VCKPD5eoqfwLxM").build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        await app.run_polling()

    asyncio.run(main())

# === Start bot only once ===
if 'bot_started' not in st.session_state:
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    st.session_state.bot_started = True

# === Streamlit Web Interface ===
st.title("Telegram Bot Running with Streamlit")
st.success("Bot is running! Try sending /start to your Telegram bot.")
st.info("You can also add more bot commands or UI components here.")