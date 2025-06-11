import streamlit as st
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio

# Secret token from Streamlit secrets or input
BOT_TOKEN = st.secrets.get("BOT_TOKEN", st.text_input("Enter your Telegram Bot Token"))

# Chat log
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# Bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello from Streamlit Bot!")

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    log_entry = f"[{user.first_name}]: {text}"
    st.session_state.chat_log.append(log_entry)
    await update.message.reply_text(f"You said: {text}")

# Start bot in async loop
async def start_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    st.success("Bot is running... send messages to it!")
    await app.run_polling()

# Run bot button
if BOT_TOKEN and st.button("▶️ Start Telegram Bot"):
    asyncio.run(start_bot())

# Display chat log
st.subheader("📨 Chat Log")
for msg in st.session_state.chat_log[-10:]:
    st.markdown(f"- {msg}")

# Manual message sender
st.subheader("📤 Send Message to User")
chat_id = st.text_input("User's Chat ID")
message = st.text_area("Message to send")

if st.button("Send Message"):
    if chat_id and message:
        try:
            bot = Bot(token=BOT_TOKEN)
            bot.send_message(chat_id=chat_id, text=message)
            st.success("Message sent!")
        except Exception as e:
            st.error(f"Failed: {e}")