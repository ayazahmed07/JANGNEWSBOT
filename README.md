# PSXBOT (Jang News Scraper to WhatsApp)

A simple Python bot that scrapes the latest headlines from Daily Jang (Urdu) and sends them to a WhatsApp number via the UltraMsg API.

## Features
- **Scrapes Latest News:** Fetches the most recent headline from Daily Jang.
- **WhatsApp Notifications:** Sends the headline and a link to the full story to your WhatsApp.
- **Duplicate Prevention:** Uses `last.txt` to ensure you only get notified once per new headline.
- **GitHub Actions Automation:** Runs automatically every 30 minutes.

## Setup Instructions

### 1. Prerequisites
- A WhatsApp account.
- An UltraMsg account (Instance ID and Token).

### 2. GitHub Secrets
To run this bot via GitHub Actions, you need to add the following secrets to your GitHub repository:
1. Go to **Settings > Secrets and variables > Actions**.
2. Add the following **Repository secrets**:
   - `WHATSAPP_INSTANCE_ID`: Your UltraMsg Instance ID (e.g., `instance12345`).
   - `WHATSAPP_TOKEN`: Your UltraMsg Token.
   - `WHATSAPP_PHONE`: The recipient's phone number in international format (e.g., `923322894427`).

### 3. Local Setup
To run the bot locally, set the following environment variables:
```bash
export WHATSAPP_INSTANCE_ID="your_instance_id"
export WHATSAPP_TOKEN="your_token"
export WHATSAPP_PHONE="your_phone_number"
```
Install dependencies:
```bash
pip install -r requirements.txt
```
Run the bot:
```bash
python bot.py
```

## How it Works
The bot uses `requests` and `BeautifulSoup4` to fetch the first headline from the Daily Jang website. It compares the headline with the one stored in `last.txt`. If it's a new headline, it sends it via the UltraMsg API and updates `last.txt`.
The GitHub Action workflow runs `bot.py` and then commits any changes to `last.txt` back to the repository to maintain state.
