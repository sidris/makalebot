import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

BOT_TOKEN = "7653096512:AAFDM04Ei8P5sLw9uPmWb3P0B7jZGuQhe1o"
CHAT_ID = "896831703"
CHECK_INTERVAL = 300

URLS = {
    "Erdal Sağlam": "https://www.sozcu.com.tr/erdal-saglam-a2293",
    "Alaattin Aktaş": "https://www.ekonomim.com/amp/yazar/alaattin-aktas/30",
    "Fatih Özatay": "https://www.ekonomim.com/amp/yazar/fatih-ozatay/85"
}

STATE_FILE = "last_articles.json"

def load_last_articles():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_last_articles(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)

def send_telegram(title, url, author):
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    message = f"📝 *{author} yeni bir yazı yayınladı!*
\n📌 *{title}*
🕒 {timestamp}
🔗 [Haberi Oku]({url})"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    requests.post(url, data=data)

def check_erdal_saglam():
    r = requests.get(URLS["Erdal Sağlam"], timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    article = soup.find("div", class_="content-title")
    if article:
        title = article.text.strip()
        link = article.find_parent("a")["href"]
        return title, link
    return None, None

def check_ekonomim(url):
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    h3 = soup.find("h3")
    if h3:
        title = h3.text.strip()
        link = "https://www.ekonomim.com" + h3.find("a")["href"]
        return title, link
    return None, None

def main_loop():
    last_data = load_last_articles()
    while True:
        print("Kontrol ediliyor...")
        try:
            title, link = check_erdal_saglam()
            if title and last_data.get("Erdal Sağlam") != title:
                send_telegram(title, link, "Erdal Sağlam")
                last_data["Erdal Sağlam"] = title

            title, link = check_ekonomim(URLS["Alaattin Aktaş"])
            if title and last_data.get("Alaattin Aktaş") != title:
                send_telegram(title, link, "Alaattin Aktaş")
                last_data["Alaattin Aktaş"] = title

            title, link = check_ekonomim(URLS["Fatih Özatay"])
            if title and last_data.get("Fatih Özatay") != title:
                send_telegram(title, link, "Fatih Özatay")
                last_data["Fatih Özatay"] = title

            save_last_articles(last_data)

        except Exception as e:
            print("Hata:", e)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main_loop()
