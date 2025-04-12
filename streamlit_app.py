import streamlit as st
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import InputPeerUser, PeerUser, PeerChannel
from telethon.tl.functions.messages import GetHistoryRequest, GetBotCallbackAnswerRequest
import asyncio
import os
import re

st.set_page_config(page_title="Парсер @SearcheeBot", layout="centered")
st.title("🤖 Авто-парсер Telegram-каналов через @SearcheeBot")
st.markdown("Загрузи `.session` файл — и получи все каналы по кнопке **«Поиск по всем категориям»**")

uploaded_file = st.file_uploader("📂 Загрузите .session файл", type=["session"])
start = st.button("🚀 Начать выгрузку")

async def parse_searcheebot(session_path):
    client = TelegramClient(session_path, api_id=12345, api_hash="0123456789abcdef0123456789abcdef")
    await client.start()
    bot = await client.get_entity("@SearcheeBot")

    await client.send_message(bot, "/start")
    await asyncio.sleep(2)

    # Получаем первое сообщение с кнопками
    msg = await client.get_messages(bot, limit=1)
    if not msg or not msg[0].buttons:
        return []

    # Ищем кнопку "🔍 Поиск по всем категориям"
    for row in msg[0].buttons:
        for button in row:
            if "Поиск по всем категориям" in button.text:
                await client(GetBotCallbackAnswerRequest(
                    peer=bot,
                    msg_id=msg[0].id,
                    data=button.data
                ))
                break

    await asyncio.sleep(3)

    found_links = set()
    while True:
        messages = await client.get_messages(bot, limit=20)
        new_links = set()
        for m in messages:
            if m.message:
                links = re.findall(r'https://t\.me/[^\s\)]+', m.message)
                new_links.update(links)

        # Прекращаем, если новых ссылок больше не приходит
        if not new_links.difference(found_links):
            break

        found_links.update(new_links)

        # Жмём "More"
        try:
            for m in messages:
                if m.buttons:
                    for row in m.buttons:
                        for button in row:
                            if "More" in button.text:
                                await client(GetBotCallbackAnswerRequest(
                                    peer=bot,
                                    msg_id=m.id,
                                    data=button.data
                                ))
                                await asyncio.sleep(3)
                                raise Exception("clicked")  # Выход из вложенных циклов
        except Exception:
            continue
        else:
            break  # если нет кнопки More — выходим

    await client.disconnect()
    return sorted(found_links)

if uploaded_file and start:
    session_path = "user_session.session"
    with open(session_path, "wb") as f:
        f.write(uploaded_file.read())

    with st.spinner("⏳ Парсим через @SearcheeBot..."):
        try:
            results = asyncio.run(parse_searcheebot(session_path))

            if results:
                result_text = "\n".join(results)
                st.success(f"✅ Найдено {len(results)} ссылок.")
                st.download_button("📥 Скачать .txt", result_text, file_name="searchee_links.txt")
            else:
                st.info("😕 Ссылок не найдено.")

        except Exception as e:
            st.error(f"❌ Ошибка: {e}")

    os.remove(session_path)
