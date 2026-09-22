# trudvsem_parser.py — парсер вакансий с портала «Работа России»
import requests
from config import WORK_WORDS, MONEY_WORDS, STOP_WORDS, CATEGORIES

URL = "https://opendata.trudvsem.ru/api/v1/vacancies/region/46"

def categorize(text):
    for cat, words in CATEGORIES.items():
        if any(w in text.lower() for w in words):
            return cat
    return "разное"

def check_post(text):
    if not text or len(text) < 20:
        return False
    if any(w.lower() in text.lower() for w in STOP_WORDS):
        return False
    has_work = any(w.lower() in text.lower() for w in WORK_WORDS)
    has_money = any(w.lower() in text.lower() for w in MONEY_WORDS)
    return has_work and has_money

def parse():
    print("Ищем вакансии на Trudvsem...")
    try:
        response = requests.get(URL, timeout=120)
        if response.status_code != 200:
            print(f"Ошибка доступа: {response.status_code}")
            return []
        data = response.json()
        vacancies = data.get("results", {}).get("vacancies", [])
        print(f"Всего вакансий: {len(vacancies)}")
        found = []
        for item in vacancies:
            vac = item.get("vacancy", {})
            name = vac.get("job-name", "")
            company = vac.get("company", {}).get("name", "Не указана")
            salary_min = vac.get("salary_min")
            salary_max = vac.get("salary_max")
            link = vac.get("vac_url", "")
            region = vac.get("region", {}).get("name", "")
            text = f"{name} {company}"
            if salary_min:
                text += f" от {salary_min} руб"
            if salary_max:
                text += f" до {salary_max} руб"
            if check_post(text):
                found.append({
                    "text": text,
                    "category": categorize(text),
                    "link": link,
                    "region": region,
                })
        print(f"Подходящих вакансий: {len(found)}")
        return found
    except requests.exceptions.Timeout:
        print("Интернет медленный, не успел загрузить.")
        return []
    except Exception as e:
        print(f"Ошибка: {e}")
        return []

if __name__ == "__main__":
    results = parse()
    with open("zakazy.txt", "a", encoding="utf-8") as f:
        for r in results:
            f.write(f"НОВЫЙ ЗАКАЗ [{r['category']}]\n")
            f.write(f"{r['text']}\n")
            f.write(f"Регион: {r['region']}\n")
            f.write(f"Ссылка: {r['link']}\n")
            f.write("=" * 40 + "\n")
    print("Результаты сохранены в zakazy.txt")
