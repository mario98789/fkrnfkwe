import streamlit as st
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import InputPeerUser, PeerUser, PeerChannel
from telethon.tl.functions.messages import GetHistoryRequest, GetBotCallbackAnswerRequest
import asyncio
import os
import re

st.set_page_config(page_title="Парсер @SearcheeBot", layout="centered")
st.title("🤖 Парсер Telegram-каналов через @SearcheeBot")
st.markdown("Полностью автоматическая выгрузка каналов через кнопку **🔍 Поиск по всем категориям**")

uploaded_file = st.file_uploader("📂 Загрузите .session файл", type=["session"])
filter_keyword = st.text_input("🔍 Фильтр по слову (например: астрология, эзотерика) [необязательно]")
start = st.button("🚀 Начать выгрузку")

async def parse_searcheebot(session_path, filter_keyword=None):
    client = TelegramClient(session_path, api_id=12345, api_hash="0123456789abcdef0123456789abcdef")
    await client.start()
    bot = await client.get_entity("@SearcheeBot")

    await client.send_message(bot, "/start")
    await asyncio.sleep(2)

    msg = await client.get_messages(bot, limit=1)
    if not msg or not msg[0].buttons:
        return []

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
    more_clicks = 0
    while True:
        messages = await client.get_messages(bot, limit=20)
        new_links = set()

        for m in messages:
            if m.message:
                links = re.findall(r'https://t\.me/[^\s\)]+', m.message)
                if links:
                    for l in links:
                        if filter_keyword:
                            if filter_keyword.lower() in m.message.lower():
                                new_links.add(l)
                        else:
                            new_links.add(l)

        # Показываем новые найденные
        if new_links:
            st.text(f"🔗 Найдено новых ссылок: {len(new_links - found_links)}")

        # Прекращаем, если новых нет
        if not new_links.difference(found_links):
            st.text("⛔ Больше новых ссылок не найдено.")
            break

        found_links.update(new_links)

        # Ищем кнопку "More"
        more_pressed = False
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
                            more_clicks += 1
                            st.text(f"➡️ Нажали 'More' {more_clicks} раз")
                            more_pressed = True
                            break
        if not more_pressed:
            st.text("✅ Кнопка 'More' больше не найдена.")
            break

    await client.disconnect()
    return sorted(found_links)

if uploaded_file and start:
    session_path = "user_session.session"
    with open(session_path, "wb") as f:
        f.write(uploaded_file.read())

    with st.spinner("⏳ Подключаемся и начинаем парсить..."):
        try:
            results = asyncio.run(parse_searcheebot(session_path, filter_keyword))

            if results:
                result_text = "\n".join(results)
                st.success(f"✅ Всего найдено: {len(results)} ссылок.")
                st.download_button("📥 Скачать .txt", result_text, file_name="searchee_links.txt")
            else:
                st.info("😕 Ничего не найдено.")

        except Exception as e:
            st.error(f"❌ Ошибка: {e}")

    os.remove(session_path)
