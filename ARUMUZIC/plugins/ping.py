import time
import psutil
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ARUMUZIC.clients import bot # Import the specific bot instance
import config

# Global startup time
START_TIME = datetime.now()

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time

# Yahan @bot use karo kyunki main.py mein bot.plugins set kiya hai
@bot.on_message(filters.command("ping") & ~filters.bot)
async def ping_cmd(client, message: Message):
    start_time = time.time()
    
    # Initial reply
    m = await message.reply_text("<code>ᴘɪɴɢɪɴɢ..</code>")
    
    # Latency & Uptime logic
    end_time = time.time()
    ping_ms = round((end_time - start_time) * 1000, 2)
    
    # Safe Uptime check from config or local START_TIME
    bot_uptime = getattr(config, "BOT_START_TIME", START_TIME)
    uptime = get_readable_time(int((datetime.now() - bot_uptime).total_seconds()))
    
    # System stats
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    
    caption = (
        "<b>🏓 ᴘᴏɴɢ! sᴛᴀᴛs ᴀʀᴇ ʜᴇʀᴇ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 <b>ʟᴀᴛᴇɴᴄʏ:</b> <code>{ping_ms} ms</code>\n"
        f"🆙 <b>ᴜᴘᴛɪᴍᴇ:</b> <code>{uptime}</code>\n"
        f"💻 <b>ᴄᴘᴜ:</b> <code>{cpu}%</code>\n"
        f"📊 <b>ʀᴀᴍ:</b> <code>{ram}%</code>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👤 <b>ᴏᴡɴᴇʀ:</b> <a href='https://t.me/sxyaru'>ᴀʀᴜ × ᴀᴘɪ [ʙᴏᴛs]</a>"
    )
    
    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url="https://t.me/sxyaru"),
        InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/ll_PANDA_BBY_ll")
    ]])

    try:
        await client.send_photo(
            message.chat.id,
            photo="https://files.catbox.moe/nacfzm.jpg",
            caption=caption,
            reply_markup=buttons
        )
        await m.delete()
    except Exception as e:
        print(f"Ping Error: {e}")
        await m.edit(caption, reply_markup=buttons)
