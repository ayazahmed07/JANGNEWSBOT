import requests
from bs4 import BeautifulSoup
import os

# --- Configuration ---
# 🔹 News Source: Daily Jang (Urdu)
JANG_LATEST_URL = "https://jang.com.pk/category/latest-news"

# 🔹 WhatsApp API Settings (UltraMsg)
INSTANCE_ID = os.getenv("WHATSAPP_INSTANCE_ID")
TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE = os.getenv("WHATSAPP_PHONE")

if not all([INSTANCE_ID, TOKEN, PHONE]):
    print("❌ Error: Missing WhatsApp API credentials in environment variables.")
    exit(1)

# --- News Fetching Logic ---

def fetch_latest_headline():
    """
    Scrapes the latest headline and its full link from Jang News.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(JANG_LATEST_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Jang headlines are usually in <h2> tags. We look for the first one.
        headline_tag = soup.find('h2')
        
        if not headline_tag:
            print("❌ No headlines found on the page.")
            return None, None

        # Extract the headline text
        title = headline_tag.get_text(strip=True)
        
        # Find the parent link (<a>) to get the full story URL
        link_tag = headline_tag.find_parent('a') or headline_tag.find('a')
        
        # If the headline itself isn't a link, look for the closest link
        if not link_tag:
            link_tag = headline_tag.find_previous('a') or headline_tag.find_next('a')

        story_url = ""
        if link_tag and link_tag.get('href'):
            story_url = link_tag.get('href')
            # Ensure the URL is absolute
            if not story_url.startswith('http'):
                story_url = f"https://jang.com.pk/{story_url.lstrip('/')}"
        
        return title, story_url

    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return None, None

# --- Helper Functions ---

def get_last_seen_headline():
    """Reads the last sent headline from last.txt to avoid duplicates."""
    if not os.path.exists("last.txt"):
        return ""
    try:
        with open("last.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""

def update_last_seen_headline(title):
    """Saves the latest headline title to last.txt."""
    with open("last.txt", "w", encoding="utf-8") as f:
        f.write(title)

def send_to_whatsapp(title, link):
    """Sends the news headline and link via UltraMsg WhatsApp API."""
    api_url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"
    
    # Format the message
    message = f"📰 *Jang Breaking News:*\n\n{title}"
    if link:
        message += f"\n\n🔗 *Read Full Story:*\n{link}"

    payload = {
        "token": TOKEN,
        "to": PHONE,
        "body": message
    }
    
    try:
        response = requests.post(api_url, data=payload, timeout=15)
        if response.status_code == 200:
            print("✅ WhatsApp message sent successfully!")
        else:
            print(f"⚠️ WhatsApp API returned error: {response.text}")
    except Exception as e:
        print(f"❌ Error sending WhatsApp: {e}")

# --- Main Logic ---

def main():
    print("🔍 Checking for new Jang headlines...")
    
    title, link = fetch_latest_headline()
    
    if not title:
        print("⏭️ Skipping update (Fetch failed).")
        return

    last_title = get_last_seen_headline()

    if title != last_title:
        print(f"🆕 New Headline: {title}")
        send_to_whatsapp(title, link)
        update_last_seen_headline(title)
    else:
        print("😴 No new updates found.")

if __name__ == "__main__":
    main()
