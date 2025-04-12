import requests
from bs4 import BeautifulSoup
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

BASE_URL = "https://tgstat.ru/channels/search"

KEYWORDS = [
    "эзотерика",
    "астрология",
    "нумерология",
    "нейрографика",
    "таро",
    "матрицы судьбы"
]

def parse_tgstat(keyword, pages=5):
    links = set()
    for page in range(1, pages + 1):
        params = {
            "q": keyword,
            "sort": "subscribers",
            "page": page
        }
        res = requests.get(BASE_URL, params=params, headers=HEADERS)
        if res.status_code != 200:
            print(f"❌ Ошибка запроса для {keyword} (страница {page})")
            continue

        soup = BeautifulSoup(res.text, "html.parser")
        results = soup.select("a.channel-info")

        for result in results:
            href = result.get("href", "")
            if "t.me/" in href:
                links.add(href.strip())

        print(f"✅ {keyword} | Страница {page} | Найдено: {len(links)}")
        time.sleep(1)

    return links

def main():
    all_links = set()
    for kw in KEYWORDS:
        links = parse_tgstat(kw, pages=5)
        all_links.update(links)

    with open("tgstat_channels.txt", "w", encoding="utf-8") as f:
        for link in sorted(all_links):
            f.write(link + "\n")

    print(f"\n🔗 Всего найдено: {len(all_links)} ссылок")

if __name__ == "__main__":
    main()
