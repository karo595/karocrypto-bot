
import asyncio
import os
from telethon import TelegramClient
import anthropic
import requests
from datetime import datetime, timedelta

API_ID = 36079863
API_HASH = "e4a66a16a0179b5b4a9fa6f753130b8c"
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
BOT_TOKEN = "8651918293:AAF5FhpFoVaNVOylaKh225oQHjaXtN-vepY"
CHAT_ID = 8113123435

CHANNELS = [
    "coinnewsru",
    "okx_ru",
    "DeCenter",
    "HyperliquidLiquidations",
    "cointelegraph",
    "crypto_hd",
    "durov",
    "cryptodaily",
    "zerowallstreet",
]

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    })

async def get_messages(client, channel, hours=24):
    messages = []
    since = datetime.now() - timedelta(hours=hours)
    async for msg in client.iter_messages(channel, offset_date=since, reverse=True):
        if msg.text:
            messages.append(msg.text)
    return messages

def summarize(texts, channel_name):
    if not texts:
        return f"📭 {channel_name}: Նոր հաղորդագրություն չկա"
    
    claude = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    combined = "\n---\n".join(texts[:50])
    
    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"Հետևյալ crypto Telegram channel-ի հաղորդագրությունները summarize արա հայերեն, կարևոր նորությունները և market signals-ը կարճ ու հստակ:\n\n{combined}"
        }]
    )
    return f"📊 *{channel_name}*\n{response.content[0].text}"

async def main():
    client = TelegramClient("session", API_ID, API_HASH)
    await client.start()
    
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    send_telegram(f"🚀 *Crypto Summary — {now}*\nՎերլուծում եմ {len(CHANNELS)} channels...")
    
    for channel in CHANNELS:
        try:
            messages = await get_messages(client, channel)
            summary = summarize(messages, channel)
            send_telegram(summary)
        except Exception as e:
            send_telegram(f"❌ {channel}: {e}")
    
    send_telegram("✅ *Ավարտ։ Բոլոր channels-ը վերլուծված են։*")
    await client.disconnect()

asyncio.run(main())
