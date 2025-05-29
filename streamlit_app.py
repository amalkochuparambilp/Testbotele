import streamlit as st
import threading
from telegram.ext import Updater, CommandHandler

# === Telegram Bot ===
def start(update, context):
    update.message.reply_text("Hello! I'm running inside Streamlit!")

def run_bot():
    TOKEN = "7240504796:AAGQ3kpkT9cjtRvG_gwt7VCKPD5eoqfwLxM"
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

# === Start Bot in Background Thread ===
if 'bot_started' not in st.session_state:
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    st.session_state.bot_started = True

# === Streamlit UI ===
st.title("Telegram Bot Running in Streamlit")
st.success("Bot is running in the background! Send /start to your bot.")
