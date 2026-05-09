import os
from datetime import datetime
from gnews import GNews
from google import genai
import requests

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Initialize Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

def fetch_and_format_news():
    # 1. Fetch Hindi News
    print("Fetching news...")
    google_news = GNews(language='hi', country='IN', period='24h')
    news = google_news.get_top_news()
    
    if not news:
        return "आज के लिए कोई नई खबर नहीं मिली।"

    raw_content = "\n".join([f"Title: {n['title']}\nDescription: {n['description']}" for n in news[:10]])

    # 2. Format with Gemini
    print("Formatting news with AI...")
    today_date = datetime.now().strftime('%d %B %Y')
    
    prompt = f"""
    You are a professional news editor. Below are news headlines for {today_date}.
    Please format them into a clean, easy-to-read Hindi news bulletin for Telegram.
    
    Structure:
    - Heading: 📅 मुख्य समाचार - {today_date}
    - For each news: Use a bullet point, bold the title, and give a 2-line simple description.
    - End with a positive 'आज का विचार' (Thought of the day).
    
    News Data:
    {raw_content}
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    
    return response.text

def send_to_telegram(text):
    # Fixed URL structure to prevent 404
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown" # Allows bold text and clean formatting
    }
    
    print(f"Sending message to Telegram...")
    r = requests.post(url, data=payload)
    
    if r.status_code == 200:
        print("Success: Message sent!")
    else:
        print(f"Error {r.status_code}: {r.text}")

if __name__ == "__main__":
    try:
        final_news = fetch_and_format_news()
        send_to_telegram(final_news)
    except Exception as e:
        print(f"Script failed: {e}")
