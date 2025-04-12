import streamlit as st
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.contacts import SearchRequest
import os

st.set_page_config(page_title="Telegram Канал Парсер", layout="centered")
st.title("🔮 Поиск Telegram-каналов по ключевикам")
st.markdown("Загрузи `.session` файл и получи список каналов с t.me-ссылками")

# Загрузка .session файла
uploaded_file = st.file_uploader("📂 Загрузите .session файл", type=["session"])

# Ключевые слова по умолчанию
keywords = st.text_area("🗝 Ключевые слова (по одному на строку)", value="""эзотерика
нумерология
астрология
нейрографика
таро
матрицы судьбы""")

start = st.button("🚀 Начать поиск")

if uploaded_file and start:
    with st.spinner("🔌 Подключаемся к Telegram..."):

        session_data = uploaded_file.read()
        session_name = "user_session"
        session_path = f"{session_name}.session"

        # Сохраняем файл
        with open(session_path, "wb") as f:
            f.write(session_data)

        try:
            # Минимально допустимые fake api_id/api_hash для обхода
            client = TelegramClient(session_name, api_id=12345, api_hash="0123456789abcdef0123456789abcdef")
            client.connect()

            if not client.is_user_authorized():
                st.error("❌ Сессия не авторизована. Создайте валидный .session файл.")
            else:
                st.success("✅ Авторизация успешна!")

                found_links = set()
                kw_list = [k.strip() for k in keywords.splitlines() if k.strip()]

                for keyword in kw_list:
                    st.write(f"🔍 Ищем по ключевику: **{keyword}**")
                    try:
                        result = client(SearchRequest(q=keyword, limit=100, offset=0))
                        for user in result.users:
                            if user.username:
                                found_links.add(f"https://t.me/{user.username}")
                    except Exception as e:
                        st.warning(f"⚠️ Ошибка при поиске по '{keyword}': {e}")

                if found_links:
                    result_text = "\n".join(sorted(found_links))
                    st.markdown(f"### ✅ Найдено ссылок: {len(found_links)}")
                    st.download_button("📥 Скачать .txt", result_text, file_name="channels.txt")
                else:
                    st.info("😕 По запросам ничего не найдено.")

        except Exception as e:
            st.error(f"Ошибка подключения: {e}")

        finally:
            client.disconnect()
            if os.path.exists(session_path):
                os.remove(session_path)
