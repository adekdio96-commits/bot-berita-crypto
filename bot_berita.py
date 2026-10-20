import time
import requests
import ccxt
import feedparser
from google import genai

TELEGRAM_BOT_TOKEN = "8861452733:AAE23GvpGESTI_q9ZX66W-xWMQ0WfsZBRvk"
TELEGRAM_CHAT_ID = "-1004483380706"
GEMINI_API_KEY = "AQ.Ab8RN6IgGahwgKY2AuQV6jKdvUUNKohpooUWrnPFgJpnd1ckCQ"

client = genai.Client(api_key=GEMINI_API_KEY)
exchange = ccxt.binance()
seen_news_titles = set()

def get_btc_price():
    try:
        return exchange.fetch_ticker('BTC/USDT')['last']
    except Exception:
        return 0

def create_news_summary(title, summary_text):
    btc_price = get_btc_price()
    price_info = f"${btc_price:,.2f}" if btc_price > 0 else "Memuat..."
    prompt = f"Terjemahkan dan buat ringkasan berita kripto berikut ke Bahasa Indonesia:\n\nTitle: {title}\nSummary: {summary_text}\nBTC Price: {price_info}"
    res = client.models.generate_content(model='gemini-3.8-flash', contents=prompt)
    return res.text

def check_rss_news():
    feed = feedparser.parse("https://cointelegraph.com/rss")
    for entry in reversed(feed.entries[:3]):
        title = entry.title
        if title not in seen_news_titles:
            print(f"[BERITA BARU]: {title}")
            msg = create_news_summary(title, entry.get('summary', title))
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
            print("--> BERHASIL DIKIRIM KE TELEGRAM!")
            seen_news_titles.add(title)

print("Bot Berita Otomatis Aktif...")
while True:
    try:
        check_rss_news()
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(120)
