# streamlit_app.py
import streamlit as st
import threading
import storage
import bot
import asyncio

st.set_page_config(page_title="Admin Panel", page_icon="🔧")

st.title("🤖 Telegram Bot Admin Panel")

# Start the bot
if not storage.bot_running:
    if st.button("▶️ Start Bot"):
        thread = threading.Thread(target=bot.run_bot)
        thread.start()
        st.success("Bot started.")

# Display messages
st.subheader("📩 Messages Received")
if storage.messages:
    for user_id, msg in reversed(storage.messages[-10:]):
        st.write(f"👤 {user_id}: {msg}")
else:
    st.info("No messages yet.")

# Broadcast message
st.subheader("📢 Broadcast Message")
message = st.text_area("Type your message to send to all users:")

if st.button("Send Broadcast"):
    if not message.strip():
        st.warning("Message cannot be empty.")
    else:
        asyncio.run(bot.broadcast_message(message))
        st.success("Broadcast sent!")
