import arxiv  # ArXiv akademik makale arama kütüphanesi
import feedparser  # RSS kaynaklarından haber çekmek için kullanılır
import requests  # HTTP istekleri yapmak için kullanılır
from bs4 import BeautifulSoup  # Web kazıma (scraping) için HTML ayrıştırıcı
from datetime import datetime  # Tarih bilgisi almak için

# ----------- 1. Fetch Academic Papers from arXiv -----------
# ArXiv'den verilen konuya uygun akademik makaleleri getirir
def fetch_arxiv_papers(query="hydrogen energy", max_results=3):
    search = arxiv.Search(
        query=query,  # Arama yapılacak konu başlığı
        max_results=max_results,  # Kaç sonuç getirileceği
        sort_by=arxiv.SortCriterion.SubmittedDate  # En yeni tarihe göre sırala
    )
    papers = []
    for result in search.results():  # Sonuçları dön
        papers.append({
            "title": result.title.strip(),  # Makale başlığı
            "summary": result.summary.strip(),  # Makale özeti
            "url": result.entry_id  # Makale bağlantısı
        })
    return papers

# ----------- 2. Fetch News from Google News RSS -----------
# Google News üzerinden ilgili konudaki haberleri çeker
def fetch_google_news(query="hydrogen energy", max_articles=3):
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)  # RSS verisini parse et
    news_items = []
    for entry in feed.entries[:max_articles]:  # Belirtilen sayıda haber al
        news_items.append({
            "title": entry.title.strip(),  # Haber başlığı
            "summary": entry.summary.strip(),  # Haber özeti
            "link": entry.link  # Haber bağlantısı
        })
    return news_items

# ----------- 3. Scrape Company News from Plug Power -----------
# Plug Power şirketinin web sitesinden haberleri kazır
def scrape_plug_power_news(max_articles=3):
    url = "https://www.plugpower.com/news/"  # Haberlerin bulunduğu sayfa
    response = requests.get(url)  # HTTP isteği gönder
    soup = BeautifulSoup(response.text, "html.parser")  # HTML verisini ayrıştır
    articles = soup.select("div.news-list-item")  # Haber kartlarını seç
    news_items = []
    for article in articles[:max_articles]:  # İlk belirlenen sayıyı al
        title = article.select_one("h3").get_text(strip=True)
        summary = article.select_one("p").get_text(strip=True)
        link = article.find("a")["href"]
        news_items.append({
            "title": title,
            "summary": summary,
            "link": link
        })
    return news_items

# ----------- 4. Summarize using OpenRouter model -----------
# Toplanan verileri OpenRouter API kullanarak özetletir
def summarize_items_openrouter(items, section_title, api_key):
    # Gelen tüm başlık + özet metnini tek prompt’a dönüştürüyoruz
    combined_text = "\n\n".join([f"Title: {item['title']}\nSummary: {item['summary']}" for item in items])

    # OpenRouter modeline gönderilecek mesaj
    prompt = f"""You're an energy analyst. Summarize the following {section_title.lower()} into 3–5 concise bullet points:\n\n{combined_text}"""

    # API'ye özetleme isteği gönderiyoruz
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        json={
            "model": "qwen/qwen2.5-vl-32b-instruct:free",  # Kullanılan model
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        },
        headers={
            "Authorization": f"Bearer {api_key}"  # API anahtarını gönderiyoruz
        }
    )

    # Gelen cevaptan özet metni çıkar
    result = response.json()
    return result["choices"][0]["message"]["content"].strip()

# ----------- 5. Build the Daily Report -----------
# Tüm bölümleri toplayıp günlük bir rapor oluşturur
def build_daily_report(api_key):
    today = datetime.today().strftime('%Y-%m-%d')  # Bugünün tarihi
    report = f"# 🔋 Daily Hydrogen Energy Report ({today})\n\n"  # Rapor başlığı

    print("Fetching academic papers from arXiv...")
    arxiv_data = fetch_arxiv_papers()

    print("Fetching news from Google News...")
    google_news_data = fetch_google_news()

    print("Scraping Plug Power company news...")
    plug_news_data = scrape_plug_power_news()

    print("Summarizing arXiv papers with OpenRouter...")
    arxiv_summary = summarize_items_openrouter(arxiv_data, "Academic Papers", api_key)
    report += "## 📘 Academic Papers (arXiv)\n" + arxiv_summary + "\n\n"

    print("Summarizing news articles with OpenRouter...")
    news_summary = summarize_items_openrouter(google_news_data, "News Articles", api_key)
    report += "## 🗞 News Articles (Google News)\n" + news_summary + "\n\n"

    print("Summarizing Plug Power news with OpenRouter...")
    company_summary = summarize_items_openrouter(plug_news_data, "Company News", api_key)
    report += "## 🏭 Company Update: Plug Power\n" + company_summary + "\n\n"

    return report

# ----------- 6. Run It! -----------
if __name__ == "__main__":
    # ❌ Güvenlik uyarısı: API anahtarını kod içinde bırakma!
    API_KEY = "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"
    # Ana raporu üret
    final_report = build_daily_report(API_KEY)
    print(final_report)
