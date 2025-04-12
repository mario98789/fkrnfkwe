import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import re

st.set_page_config(page_title="TGStat Парсер", layout="centered")
st.title("🔍 Парсер Telegram-каналов по тематикам (TGStat.ru)")

keywords_input = st.text_area("🔑 Введите ключевые слова (по одному на строку):", value="эзотерика\nастрология\nнумерология\nтаро\nматрицы судьбы")
pages = st.slider("📄 Сколько страниц парсить на каждый запрос?", min_value=1, max_value=10, value=3)
start = st.button("🚀 Начать поиск")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}
BASE_URL = "https://tgstat.ru/channels/search"

def parse_tgstat(keyword, pages):
    links = set()
    for page in range(1, pages + 1):
        params = {
            "q": keyword,
            "sort": "subscribers",
            "page": page
        }
        res = requests.get(BASE_URL, params=params, headers=HEADERS)
        if res.status_code != 200:
            st.warning(f"⚠️ Ошибка запроса для: {keyword} (стр. {page})")
            continue

        soup = BeautifulSoup(res.text, "html.parser")
        results = soup.select("a.channel-info")

        for result in results:
            href = result.get("href", "")
            if "t.me/" in href:
                links.add(href.strip())

        time.sleep(1)
    return links

if start:
    if not keywords_input.strip():
        st.warning("⚠️ Введите хотя бы одно ключевое слово.")
    else:
        all_links = set()
        keywords = [k.strip() for k in keywords_input.splitlines() if k.strip()]
        with st.spinner("🔍 Парсим каналы..."):
            for kw in keywords:
                st.text(f"🔎 {kw}")
                links = parse_tgstat(kw, pages)
                all_links.update(links)

        if all_links:
            result_text = "\n".join(sorted(all_links))
            st.success(f"✅ Найдено ссылок: {len(all_links)}")
            st.download_button("📥 Скачать .txt", data=result_text, file_name="tgstat_links.txt")
        else:
            st.info("😕 Ничего не найдено.")
