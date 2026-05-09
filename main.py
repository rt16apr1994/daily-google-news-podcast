import os
from datetime import datetime
from gnews import GNews
from google import genai
import requests

# Configuration - Using .strip() to remove any accidental hidden spaces from GitHub Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

client = genai.Client(api_key=GEMINI_API_KEY)

def fetch_and_format_news():
    print("Step 1: Fetching Hindi News...")
    google_news = GNews(language='hi', country='IN', period='24h')
    news = google_news.get_top_news()
    
    if not news:
        return "आज के लिए कोई नई खबर नहीं मिली।"

    raw_content = "\n".join([f"Title: {n['title']}\nDescription: {n['description']}" for n in news[:10]])

    print("Step 2: Formatting with Gemini 2.0 Flash...")
    today_date = datetime.now().strftime('%d %B %Y')
    
    prompt = f"""
    You are a professional Hindi news editor. Format these headlines for a Telegram bulletin:
    📅 मुख्य समाचार - {today_date}
    
    - Use bullet points.
    - Bold the titles.
    - Summarize descriptions clearly.
    
    News Data:
    {raw_content}
    """

    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text

def send_to_telegram(text):
    # REMOVED the 'bot' prefix from the URL here to see if your Secret already has it
    # OR ensured it is formatted exactly as Telegram expects.
    
    clean_token = TELEGRAM_TOKEN
    if clean_token.startswith("bot"):
        # If your secret is "bot1234...", we use it as is
        api_url = f"https://api.telegram.org/{clean_token}/sendMessage"
    else:
        # If your secret is "1234...", we add "bot"
        api_url = f"https://api.telegram.org/bot{clean_token}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    print(f"Step 3: Sending to Telegram...")
    # Timeout added to prevent the job from hanging
    r = requests.post(api_url, data=payload, timeout=30)
    
    if r.status_code == 200:
        print("✅ Success! Check your Telegram.")
    else:
        print(f"❌ Failed! Status: {r.status_code}")
        print(f"Response from Telegram: {r.text}")
        # DEBUG: This will show us what the URL looked like without revealing the full token
        print(f"URL attempted: https://api.telegram.org/bot{clean_token[:5]}.../sendMessage")

if __name__ == "__main__":
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing Environment Variables! Check GitHub Secrets.")
    else:
        content = fetch_and_format_news()
        send_to_telegram(content)
