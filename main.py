import os
import asyncio
from datetime import datetime
from gnews import GNews
import google.generativeai as genai # Note: If you want to use the new 'google-genai', the syntax changes slightly
import edge_tts
import requests

# Set Gemini to ignore the EOL warnings in logs
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

genai.configure(api_key=GEMINI_API_KEY)

def get_hindi_news():
    # Fetching Hindi news directly for better context
    google_news = GNews(language='hi', country='IN', period='24h')
    news = google_news.get_top_news()
    content = ""
    for i, item in enumerate(news[:10]):
        content += f"{i+1}. {item['title']}\n{item['description']}\n\n"
    return content

async def generate_podcast():
    news_data = get_hindi_news()
    
    # Prompting Gemini to expand content for 20 minutes
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
    You are a professional Hindi podcast host. Based on these news headlines:
    {news_data}
    
    Write a 2-minute long, engaging podcast script in Hindi (written in Devanagari script).
    Structure:
    1. Intro: Welcome to 'Daily Samachar Podcast'.
    2. Deep Dive: Discuss each news item in detail. Add background info and possible impacts.
    3. Commentary: Keep the tone conversational, friendly, and informative.
    4. Outro: Summary and sign-off.
    
    Note: The script must be exactly 2 minutes duration (approx 150 words) to fill 5 minutes.
    """
    
    response = model.generate_content(prompt)
    script = response.text
    
    # Text-to-Speech (Hindi Female Voice)
    communicate = edge_tts.Communicate(script, "hi-IN-SwaraNeural")
    await communicate.save("podcast.mp3")

def send_to_telegram():
    if not os.path.exists("podcast.mp3"):
        print("Error: podcast.mp3 was never created!")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendAudio"
    print(f"Attempting to send to Chat ID: {TELEGRAM_CHAT_ID}")
    
    with open("podcast.mp3", "rb") as audio:
        payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": f"आज का पॉडकास्ट: {datetime.now().strftime('%d %b %Y')}"}
        files = {"audio": audio}
        
        response = requests.post(url, data=payload, files=files)
        
        if response.status_code == 200:
            print("Successfully sent to Telegram!")
        else:
            print(f"Failed to send. Status Code: {response.status_code}")
            print(f"Response: {response.text}") # This will tell us the exact Telegram error

if __name__ == "__main__":
    asyncio.run(generate_podcast())
    send_to_telegram()
