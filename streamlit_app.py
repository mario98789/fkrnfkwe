import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="TGStat Парсер", layout="centered")
st.title("🔍 Парсер Telegram-каналов по ключевым словам (через TGStat API)")

api_token = st.text_input("🔑 Введите ваш TGStat API токен:", type="password")
keywords_input = st.text_area("📝 Введите ключевые слова (по одному на строку):", value="эзотерика\nастрология\nнумерология\nтаро\nматрицы судьбы")
limit = st.slider("📄 Количество каналов на каждый запрос:", min_value=1, max_value=100, value=20)
start = st.button("🚀 Начать поиск")

def search_channels(keyword, token, limit):
    url = "https://api.tgstat.ru/channels/search"
    params = {
        "token": token,
        "q": keyword,
        "limit": limit,
        "language": "russian"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "ok":
            return data["response"]["items"]
        else:
            st.error(f"Ошибка от API: {data.get('error', 'Неизвестная ошибка')}")
            return []
    else:
        st.error(f"HTTP ошибка: {response.status_code}")
        return []

if start:
    if not api_token:
        st.warning("⚠️ Пожалуйста, введите ваш TGStat API токен.")
    elif not keywords_input.strip():
        st.warning("⚠️ Введите хотя бы одно ключевое слово.")
    else:
        all_channels = []
        keywords = [k.strip() for k in keywords_input.splitlines() if k.strip()]
        with st.spinner("🔍 Поиск каналов..."):
            for kw in keywords:
                st.text(f"🔎 Поиск по ключевому слову: {kw}")
                channels = search_channels(kw, api_token, limit)
                for ch in channels:
                    all_channels.append({
                        "Ключевое слово": kw,
                        "Название": ch.get("title", ""),
                        "Username": ch.get("username", ""),
                        "Ссылка": f"https://{ch.get('link', '')}",
                        "Описание": ch.get("about", ""),
                        "Подписчики": ch.get("participants_count", 0)
                    })

        if all_channels:
            df = pd.DataFrame(all_channels)
            st.success(f"✅ Найдено каналов: {len(df)}")
            st.dataframe(df)
            csv = df.to_csv(index=False)
            st.download_button("📥 Скачать CSV", data=csv, file_name="tgstat_channels.csv", mime="text/csv")
        else:
            st.info("😕 Ничего не найдено.")
