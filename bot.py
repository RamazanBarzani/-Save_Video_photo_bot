import os
from pyrogram import Client, filters
import yt_dlp

# زانیارییەکان لە سێرڤەرەوە وەردەگرێت بۆ پارێزراوی
API_ID = int(os.environ.get("API_ID", "12345678"))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")

app = Client("video_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "سڵاو! لینکی ڤیدیۆکەم بۆ بنێرە تا بۆت دابەزێنم و بینێرمەوە."
    )

@app.on_message(filters.text & ~filters.command(["start"]))
async def download_video(client, message):
    url = message.text
    status_msg = await message.reply_text("⏳ چاوەڕوان بە، سەرقاڵی داونلۆدکردنی ڤیدیۆکەم...")

    output_template = "downloads/%(id)s.%(ext)s"
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_template,
        'max_filesize': 50 * 1024 * 1024, # سنوردارکردنی قەبارە بۆ 50 مێگابایت بۆ خێرایی
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        await status_msg.edit_text("📤 سەرقاڵی ناردنی ڤیدیۆکەم بۆ تێلێگرام...")
        
        await message.reply_video(video=file_path, caption="✅ ڤیدیۆکە سەرکەوتووانە داگرت!")
        
        # سڕینەوەی فایلەکە لە سێرڤەر دوای ناردن
        if os.path.exists(file_path):
            os.remove(file_path)
            
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ هەڵەیەک ڕوودا لە داونلۆدکردندا:\n`{str(e)}`")

print(
app.run()
