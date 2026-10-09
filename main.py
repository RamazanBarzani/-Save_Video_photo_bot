import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# وەرگرتنی زانیارییەکان لە ژینگەی سێرڤەر (Render)
API_ID = int(os.environ.get("API_ID", "1234567"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# سێشنی ئەکاونتی کەسی بۆ داونلۆدی میدیای ڕێستراکتکراو
STRING_SESSION = os.environ.get("STRING_SESSION", "")

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ئەگەر String Session هەبوو، یوزەر-بۆتیش چالاک دەکات
user_app = None
if STRING_SESSION:
    user_app = Client("user_sess", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "👋 سڵاو! لینکی ئەو پەیام یان ڤیدیۆیەی ڕێستریکتی لەسەرە بۆم بنێرە تا بۆت دابەزێنم.\n\n"
        "نموونەی لینک:\n`https://t.me/c/123456789/100`"
    )

@app.on_message(filters.text & filters.private)
async def download_restricted(client, message: Message):
    text = message.text.strip()
    
    if not ("t.me/" in text):
        return

    status = await message.reply_text("⏳ لە هەوڵی داونلۆدکردنی فایلی ڕێستراکتکراودام...")

    try:
        # شیکردنەوەی لینکی تێلێگرام
        parts = text.split("/")
        message_id = int(parts[-1])
        
        if "t.me/c/" in text:
            # کەناڵ یان گرووپی تایبەت (Private Channel)
            chat_id = int("-100" + parts[-2])
        else:
            # کەناڵی گشتی (Public Channel)
            chat_id = parts[-2]

        client_to_use = user_app if user_app else app

        if user_app and not user_app.is_connected:
            await user_app.start()

        # وەرگرتنی پەیامەکە لە تێلێگرام
        target_msg = await client_to_use.get_messages(chat_id, message_id)

        if not target_msg.media:
            await status.edit_text("❌ هیچ میدیایەک (ڤیدیۆ/وێنە) لەم لینکەدا نەدۆزرایەوە.")
            return

        await status.edit_text("📥 فایلەکە دادەبەزێت بۆ سێرڤەر...")
        file_path = await client_to_use.download_media(target_msg)

        await status.edit_text("📤 بۆت دەنێردرێتەوە...")
        await message.reply_document(document=file_path, caption="✅ فایلی ڕێستراکتکراو بە سەرکەوتوویی نێردرا.")

        if os.path.exists(file_path):
            os.remove(file_path)

        await status.delete()

    except Exception as e:
        await status.edit_text(f"❌ هەڵەیەک ڕوویدا:\n`{str(e)}`\n\nدڵنیابەرەوە کە ئەکاونتەکەت لەو کەناڵەدا ئەندامە.")

app.run()
