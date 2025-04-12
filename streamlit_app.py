import streamlit as st
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.messages import GetHistoryRequest
import asyncio
import re
import os

st.set_page_config(page_title="SearcheeBot Парсер", layout="centered")
st.title("🤖 Поиск Telegram-каналов через @SearcheeBot")
st.markdown("Загрузи `.session` файл и получи ссылки с бота [@SearcheeBot](https://t.me/SearcheeBot)")

uploaded_file = st.file_uploader("📂 Загрузите .session файл", type=["session"])

keywords = st.text_area("🗝 Ключевые слова (по одному на строку)", value="эзотерика\nнумерология\nастрология\nнейрографика\nтаро\nматрицы судьбы")
start = st.button("🚀 Начать поиск")

async def search_via_searcheebot(session_path, keyword_list):
    client = TelegramClient(session_path, api_id=12345, api_hash="0123456789abcdef0123456789abcdef")
    await client.start()

    found_links = set()
    bot = await client.get_entity("@SearcheeBot")

    for keyword in keyword_list:
        st.markdown(f"🔍 <b>Запрос:</b> <code>{keyword}</code>", unsafe_allow_html=True)
        await client.send_message(bot, keyword)
        await asyncio.sleep(4)

        messages = await client.get_messages(bot, limit=30)
        if not messages:
            st.warning("⚠️ Бот не ответил.")
            continue

        got_links = False
        for msg in messages:
            if msg.message:
                st.code(msg.message[:300], language="text")  # показываем часть текста
                links = re.findall(r'https://t\.me/[^\s\)]+', msg.message)
                if links:
                    got_links = True
                    found_links.update(links)

        if not got_links:
            st.info("ℹ️ Ответ получен, но без ссылок.")

        # Нажимаем "More" несколько раз
        for i in range(5):
            await client.send_message(bot, "More")
            await asyncio.sleep(3)
            more_messages = await client.get_messages(bot, limit=20)
            for msg in more_messages:
                if msg.message:
                    links = re.findall(r'https://t\.me/[^\s\)]+', msg.message)
                    if links:
                        found_links.update(links)

    await client.disconnect()
    return sorted(found_links)

if uploaded_file and start:
    session_name = "user_session"
    session_path = f"{session_name}.session"
    with open(session_path, "wb") as f:
        f.write(uploaded_file.read())

    with st.spinner("🔍 Ищем через @SearcheeBot..."):
        try:
            kw_list = [k.strip() for k in keywords.splitlines() if k.strip()]
            links = asyncio.run(search_via_searcheebot(session_name, kw_list))

            if links:
                result_text = "\n".join(links)
                st.success(f"✅ Найдено ссылок: {len(links)}")
                st.download_button("📥 Скачать результат", data=result_text, file_name="searchee_results.txt")
            else:
                st.info("😕 Бот ответил, но ничего не найдено.")

        except Exception as e:
            st.error(f"❌ Ошибка: {e}")

    os.remove(session_path)
