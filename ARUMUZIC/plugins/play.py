import asyncio 
import aiohttp
import time
from urllib.parse import quote
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls.types import AudioPiped, HighQualityAudio
from ARUMUZIC.clients import bot, assistant, call 
import config

# --- Configuration for Queues (Ensure this exists in config.py or here) ---
if not hasattr(config, "queues"):
    config.queues = {}

# --- Utils ---
def fmt_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}" if hours > 0 else f"{minutes:02}:{seconds:02}"

def gen_btn_progressbar(total_sec, current_sec):
    bar_length = 10 
    if total_sec <= 0: total_sec = 1
    percentage = min(100, max(0, (current_sec / total_sec) * 100))
    filled_blocks = int(percentage / (100 / bar_length))
    bar = "▰" * filled_blocks + "▱" * (bar_length - filled_blocks)
    return f"{fmt_time(current_sec)} {bar} {fmt_time(total_sec)}"

# --- Timer Logic ---
async def update_timer(chat_id, message_id, duration):
    start_time = time.time()
    while True:
        await asyncio.sleep(12) # Interval thoda badhaya taaki Telegram limit na kare
        if chat_id not in config.queues or not config.queues[chat_id]:
            break
        
        elapsed_time = min(duration, int(time.time() - start_time))
        new_prog = gen_btn_progressbar(duration, elapsed_time)
        
        try:
            await bot.edit_message_reply_markup(
                chat_id, message_id,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text=new_prog, callback_data="prog_update")],
                    [
                        InlineKeyboardButton("▷", callback_data="resume_cb"),
                        InlineKeyboardButton("Ⅱ", callback_data="pause_cb"),
                        InlineKeyboardButton("⏭", callback_data="skip_cb"),
                        InlineKeyboardButton("▢", callback_data="stop_cb")
                    ],
                    [
                        InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/ll_PANDA_BBY_ll"),
                        InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url="https://t.me/sxyaru")
                    ]
                ])
            )
        except: break
        
        if elapsed_time >= duration:
            break # Loop end, automation handle karega next song

# --- Play Next Function ---
async def play_next(chat_id: int):
    if chat_id not in config.queues or len(config.queues[chat_id]) <= 1:
        config.queues[chat_id] = []
        try: await call.leave_group_call(chat_id)
        except: pass
        return

    config.queues[chat_id].pop(0) 
    song = config.queues[chat_id][0] 
    title, stream_url, duration, user_name = song["title"], song["url"], song["duration"], song["by"]

    try:
        # Phele change karne ki koshish karo
        try:
            await call.change_stream(chat_id, AudioPiped(stream_url, HighQualityAudio()))
        except:
            # Agar change fail ho (call active na ho), toh join karo
            await call.join_group_call(chat_id, AudioPiped(stream_url, HighQualityAudio()))
        text = (
            f"<blockquote>"
            f"<b>❍ ɴᴇxᴛ sᴏɴɢ sᴛʀᴇᴀᴍ sᴛᴀʀᴛᴇᴅ |</b>\n\n"
            f"<b>‣ Tɪᴛʟᴇ :</b> <a href='{stream_url}'>{title}</a>\n"
            f"<b>‣ Dᴜʀᴀᴛɪᴏɴ :</b> <code>{fmt_time(duration)}</code>\n"
            f"<b>‣ Rᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> `{user_name}`\n"
            f"</blockquote>"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=gen_btn_progressbar(duration, 0), callback_data="prog_update")],
            [InlineKeyboardButton("▷", "resume_cb"), InlineKeyboardButton("Ⅱ", "pause_cb"), InlineKeyboardButton("⏭", "skip_cb"), InlineKeyboardButton("▢", "stop_cb")],
            [InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/ll_PANDA_BBY_ll"), InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url="https://t.me/sxyaru")]
        ])
        pmp = await bot.send_photo(chat_id, photo="https://files.catbox.moe/uyum1c.jpg", caption=text, reply_markup=buttons)
        asyncio.create_task(update_timer(chat_id, pmp.id, duration))
    except:
        await play_next(chat_id)

@Client.on_message(filters.command("play") & filters.group)
async def play_cmd(client, msg: Message):
    chat_id = msg.chat.id
    user_name = msg.from_user.first_name if msg.from_user else "User"

    if len(msg.command) < 2: return await msg.reply("❌ **ɢɪᴠᴇ ᴀ ǫᴜᴇʀʏ!**")
    query = msg.text.split(None, 1)[1].strip()
    m = await msg.reply("<blockquote>🔎 <b>sᴇᴀʀᴄʜɪɴɢ...</b></blockquote>")

    # API Search
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://jio-saa-van.vercel.app/result/?query={quote(query)}", timeout=15) as r:
                data = await r.json()
    except Exception as e:
        return await m.edit(f"❌ **sᴇᴀʀᴄʜ ᴇʀʀᴏʀ:** `{e}`")

    if not data: return await m.edit("❌ **ɴᴏ ʀᴇsᴜʟᴛs ғᴏᴜɴᴅ!**")
    
    track = data[0]
    title, duration = track.get("song"), int(track.get("duration", 0))
    stream_url = track.get("media_url") or track.get("download_url")
    song_data = {"title": title, "url": stream_url, "duration": duration, "by": user_name}

    if chat_id not in config.queues:
        config.queues[chat_id] = []

    # --- QUEUE CHECK ---
    # Agar queue khali nahi hai, iska matlab gaana chal raha hai
    if len(config.queues[chat_id]) > 0:
        config.queues[chat_id].append(song_data)
        # Yahan callback_data="skip_cb" rakha hai jo turant agla gaana bajayega
        btn_queue = InlineKeyboardMarkup([[InlineKeyboardButton("▷ ᴘʟᴀʏ ɴᴏᴡ", callback_data="skip_cb")]])
        return await m.edit(
            f"<b>✅ ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ (ᴘᴏsɪᴛɪᴏɴ #{len(config.queues[chat_id])-1})</b>\n"
            f"🎵 <b>ᴛɪᴛʟᴇ:</b> {title}", 
            reply_markup=btn_queue
        )

    # Naya gaana add karo aur bajao
    config.queues[chat_id].append(song_data)
    await m.delete()

    try:
        # Join and Play
        await call.join_group_call(chat_id, AudioPiped(stream_url, HighQualityAudio()))
        
        text = (
            f"<blockquote>"
            f"<b>❍ Sᴛᴀʀᴛᴇᴅ Sᴛʀᴇᴀᴍɪɴɢ |</b>\n\n"
            f"<b>‣ Tɪᴛʟᴇ :</b> <a href='{stream_url}'>{title}</a>\n"
            f"<b>‣ Dᴜʀᴀᴛɪᴏɴ :</b> <code>{fmt_time(duration)}</code>\n"
            f"<b>‣ Rᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> `{user_name}`\n"
            f"</blockquote>"
        )

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=gen_btn_progressbar(duration, 0), callback_data="prog_update")],
            [InlineKeyboardButton("▷", "resume_cb"), InlineKeyboardButton("Ⅱ", "pause_cb"), InlineKeyboardButton("⏭", "skip_cb"), InlineKeyboardButton("▢", "stop_cb")],
            [InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/ll_PANDA_BBY_ll"), InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url="https://t.me/sxyaru")]
        ])
        pmp = await client.send_photo(chat_id, photo="https://files.catbox.moe/cu442f.jpg", caption=text, reply_markup=buttons)
        asyncio.create_task(update_timer(chat_id, pmp.id, duration))
        
    except Exception as e:
        config.queues[chat_id] = []
        await client.send_message(chat_id, f"❌ **ᴇʀʀᴏʀ:** {e}")
