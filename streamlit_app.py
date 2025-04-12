import streamlit as st
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.contacts import SearchRequest
import asyncio
import os

st.set_page_config(page_title="Telegram Парсер", layout="centered")
st.title("🔮 Поиск Telegram-каналов по ключевикам")
st.markdown("Загрузи `.session` файл и получи t.me-ссылки")

uploaded_file = st.file_uploader("📂 Загрузите .session", type=["session"])
keywords = st.text_area("🔑 Ключевые слова:", value="эзотерика\nастрология\nтаро\nнумерология\nматрицы судьбы\nнейрографика")
start = st.button("🚀 Начать")

async def run_parser(session_path, keyword_list):
    client = TelegramClient(session_path, api_id=12345, api_hash="fake_hash")
    await client.start()

    found_links = set()
    for keyword in keyword_list:
        try:
            result = await client(SearchRequest(q=keyword, limit=100, offset=0))
            for user in result.users:
                if user.username:
                    found_links.add(f"https://t.me/{user.username}")
        except Exception:
            continue

    await client.disconnect()
    return found_links

if uploaded_file and start:
    session_name = "user_session"
    session_path = f"{session_name}.session"
    with open(session_path, "wb") as f:
        f.write(uploaded_file.read())

    with st.spinner("🔎 Ищем каналы..."):
        kw_list = [k.strip() for k in keywords.splitlines() if k.strip()]
        links = asyncio.run(run_parser(session_name, kw_list))

    if links:
        result_text = "\n".join(sorted(links))
        st.success(f"✅ Найдено ссылок: {len(links)}")
        st.download_button("📥 Скачать результат", data=result_text, file_name="channels.txt")
    else:
        st.info("Ничего не найдено.")
    
    os.remove(session_path)
