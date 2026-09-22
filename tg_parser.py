# tg_parser.py — парсер Telegram-каналов через веб-версию
import requests
import time
from bs4 import BeautifulSoup
from keywords import WORK_WORDS, MONEY_WORDS, STOP_WORDS, CATEGORIES, TG_CHANNELS

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Mobile Safari/537.36"
}

def categorize(text):
    for cat, words in CATEGORIES.items():
        if any(w in text.lower() for w in words):
            return cat
    return "разное"

def check_post(text):
    if not text or len(text) < 40:
        return False
    if any(w.lower() in text.lower() for w in STOP_WORDS):
        return False
    has_work = any(w.lower() in text.lower() for w in WORK_WORDS)
    has_money = any(w.lower() in text.lower() for w in MONEY_WORDS)
    return has_work and has_money

def parse_channel(channel):
    url = f"https://t.me/s/{channel}"
    print(f"Читаем: {channel}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        messages = soup.find_all("div", class_="tgme_widget_message_text")
        found = []
        for msg in messages:
            text = msg.get_text(strip=True)
            if check_post(text):
                found.append({
                    "category": categorize(text),
                    "text": text,
                    "source": f"t.me/{channel}",
                })
        return found
    except Exception:
        return []

def parse_all():
    all_found = []
    for channel in TG_CHANNELS:
        results = parse_channel(channel)
        all_found.extend(results)
        time.sleep(2)
    return all_found

if __name__ == "__main__":
    print("Парсим Telegram...")
    results = parse_all()
    with open("zakazy.txt", "a", encoding="utf-8") as f:
        for r in results:
            f.write(f"НОВЫЙ ЗАКАЗ [{r['category']}]\n")
            f.write(f"{r['text'][:500]}\n")
            f.write(f"Источник: {r['source']}\n")
            f.write("=" * 40 + "\n")
    print(f"Всего найдено: {len(results)}")
