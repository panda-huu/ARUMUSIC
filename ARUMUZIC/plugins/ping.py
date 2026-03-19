import time
import psutil
from ARUMUZIC.clients import bot, assistant, call
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import config # 👈 Isse BOT_START_TIME milega

@Client.on_message(filters.command("ping")) # 👈 @bot nahi, @Client
async def ping_cmd(client, msg: Message):
    # 1. User ka command delete karo
    try:
        await msg.delete()
    except:
        pass

    start_time = time.time()
    
    # 2. 'Pinging...' message bhejo
    m = await client.send_message(msg.chat.id, "<code>ᴘɪɴɢɪɴɢ..</code>")
    
    # Latency & Stats logic
    end_time = time.time()
    latency = round((end_time - start_time) * 1000, 2)
    
    # config.BOT_START_TIME use karo
    uptime_sec = (datetime.now() - config.BOT_START_TIME).total_seconds()
    uptime = str(timedelta(seconds=int(uptime_sec)))
    
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    text = (
        "<b>🏓 ᴘᴏɴɢ! sᴛᴀᴛs ᴀʀᴇ ʜᴇʀᴇ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 <b>ʟᴀᴛᴇɴᴄʏ:</b> <code>{latency} ms</code>\n"
        f"🆙 <b>ᴜᴘᴛɪᴍᴇ:</b> <code>{uptime}</code>\n"
        f"💻 <b>ᴄᴘᴜ:</b> <code>{cpu}%</code>\n"
        f"📊 <b>ʀᴀᴍ:</b> <code>{ram}%</code>\n"
        f"💾 <b>ᴅɪsᴋ:</b> <code>{disk}%</code>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👤 <b>ᴏᴡɴᴇʀ:</b> <a href='https://t.me/sxyaru'>ᴀʀᴜ × ᴀᴘɪ [ʙᴏᴛs]</a>"
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url="https://t.me/sxyaru"),
            InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/ll_PANDA_BBY_ll")
        ]
    ])

    # 3. Pinging delete karke photo bhejo
    await m.delete()
    
    PING_IMG = "https://files.catbox.moe/nacfzm.jpg" 
    
    await client.send_photo(
        msg.chat.id,
        photo=PING_IMG,
        caption=text,
        reply_markup=buttons
    )
