import requests
from bs4 import BeautifulSoup
import os
import time

# --- Configuration ---
JANG_LATEST_URL = "https://jang.com.pk/category/latest-news"

# ⚠️ Replace these with your actual UltraMsg credentials
INSTANCE_ID = "instance168787"
TOKEN = "fposw4le00f7yreu"
PHONE = "923342894427"

# Log file
LOG_FILE = "bot.log"
LAST_FILE = "last.txt"

# --- Helper Functions ---

def log(message):
    """Append message with timestamp to bot.log and print it."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_message + "\n")

def fetch_latest_headline():
    """Scrapes the latest headline and URL from Jang News."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(JANG_LATEST_URL, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        headline_tag = soup.find('h2')
        if not headline_tag:
            log("❌ No headlines found.")
            return None, None

        title = headline_tag.get_text(strip=True)
        link_tag = headline_tag.find_parent('a') or headline_tag.find('a')
        if not link_tag:
            link_tag = headline_tag.find_previous('a') or headline_tag.find_next('a')

        story_url = ""
        if link_tag and link_tag.get('href'):
            story_url = link_tag.get('href')
            if not story_url.startswith('http'):
                story_url = f"https://jang.com.pk/{story_url.lstrip('/')}"
        return title, story_url
    except Exception as e:
        log(f"❌ Error fetching news: {e}")
        return None, None

def get_last_seen_headline():
    """Reads the last sent headline from last.txt"""
    if not os.path.exists(LAST_FILE):
        return ""
    try:
        with open(LAST_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        log(f"❌ Error reading last.txt: {e}")
        return ""

def update_last_seen_headline(title):
    """Saves the latest headline title to last.txt"""
    try:
        with open(LAST_FILE, "w", encoding="utf-8") as f:
            f.write(title)
    except Exception as e:
        log(f"❌ Error writing last.txt: {e}")

def send_to_whatsapp(title, link):
    """Sends the news headline via UltraMsg WhatsApp API"""
    api_url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"
    message = f"📰 *Jang Breaking News:*\n\n{title}"
    if link:
        message += f"\n\n🔗 *Read Full Story:*\n{link}"

    payload = {"token": TOKEN, "to": PHONE, "body": message}
    try:
        response = requests.post(api_url, data=payload, timeout=15)
        if response.status_code == 200:
            log("✅ WhatsApp message sent successfully!")
        else:
            log(f"⚠️ WhatsApp API returned error: {response.text}")
    except Exception as e:
        log(f"❌ Error sending WhatsApp: {e}")

# --- Main Logic ---
def main():
    log("🔍 Checking for new Jang headlines...")
    title, link = fetch_latest_headline()
    if not title:
        log("⏭️ Skipping update (Fetch failed).")
        return
    last_title = get_last_seen_headline()
    if title != last_title:
        log(f"🆕 New Headline: {title}")
        send_to_whatsapp(title, link)
        update_last_seen_headline(title)
    else:
        log("😴 No new updates found.")

# --- Continuous Loop ---
def main_loop():
    while True:
        try:
            main()
        except Exception as e:
            log(f"❌ Error in main loop: {e}")
        log("⏳ Waiting 10 seconds before next check...")
        time.sleep(10)  # Change to 600 for 10-minute interval

if __name__ == "__main__":
    # Make sure last.txt exists
    if not os.path.exists(LAST_FILE):
        open(LAST_FILE, "w").close()
    main_loop()
