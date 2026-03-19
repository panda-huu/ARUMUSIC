#import asyncio
import aiohttp
import time
from urllib.parse import quote
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from pytgcalls.types import AudioPiped, HighQualityAudio

# IMPORTANT: Inhe mangwana padega main aur config se
from main import bot, assistant, call 
import config

# --- Utils (Timer functions) ---
def fmt_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    return f"{minutes:02}:{seconds:02}"

def gen_btn_progressbar(total_sec, current_sec):
    # Pehle bar_length 12-15 thi, ab 6-8 karke dekho
    bar_length = 8 
    
    if total_sec == 0: total_sec = 1
    percentage = (current_sec / total_sec) * 100
    percentage = min(100, max(0, percentage))
    
    filled_blocks = int(percentage / (100 / bar_length))
    
    # Dot wala style (Image match)
    bar = "▬" * filled_blocks + "●" + "▬" * (bar_length - filled_blocks)
    
    return f"{fmt_time(current_sec)} {bar} {fmt_time(total_sec)}"

#UPDATE TIMER
async def update_timer(chat_id, message_id, duration):
    start_time = time.time() 
    while True:
        await asyncio.sleep(10)
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
                        InlineKeyboardButton("ᴏᴡɴᴇʀ↗", url="https://t.me/ll_PANDA_BBY_ll"),
                        InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ ↗", url="https://t.me/sxyaru")
                    ]
                ])
            )
            if elapsed_time >= duration: break
        except: break

# --- Core Functions ---

async def play_next(chat_id: int):
    if chat_id not in config.queues or not config.queues[chat_id]:
        return False
    song = config.queues[chat_id][0]
    url = song["url"]
    try:
        try:
            await call.join_group_call(chat_id, AudioPiped(url, HighQualityAudio()))
        except:
            await call.change_stream(chat_id, AudioPiped(url, HighQualityAudio()))
        return True
    except Exception as e:
        print(f"Assistant Join Error: {e}")
        if chat_id in config.queues: config.queues[chat_id].pop(0)
        return False

@Client.on_message(filters.command("play") & filters.group)
async def play_cmd(client, msg: Message):
    try: await msg.delete()
    except: pass
    
    chat_id = msg.chat.id
    user_name = msg.from_user.first_name if msg.from_user else "User"

    # 1. Admin/Assistant Check
    try:
        ast_info = await assistant.get_me()
        try:
            ast_member = await client.get_chat_member(chat_id, ast_info.id)
            if ast_member.status == ChatMemberStatus.BANNED:
                return await msg.reply("❌ Assistant is banned!")
        except:
            invitelink = await client.export_chat_invite_link(chat_id)
            await assistant.join_chat(invitelink)
    except Exception as e:
        return await msg.reply(f"❌ Error: {e}")

    # 2. Search
    if len(msg.command) < 2:
        return await msg.reply("❌ **ɢɪᴠᴇ ǫᴜᴇʀʏ!**")
    
    query = msg.text.split(None, 1)[1].strip()
    m = await msg.reply("🔎 <b>sᴇᴀʀᴄʜɪɴɢ...</b>")

    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://jio-saa-van.vercel.app/result/?query={quote(query)}"
            async with session.get(url, timeout=12) as r:
                data = await r.json()
    except: return await m.edit("❌ API Error!")

    if not data: return await m.edit("❌ No results found.")

    track = data[0]
    title, duration = track.get("song"), int(track.get("duration", 0))
    stream_url = track.get("media_url") or track.get("download_url")
    
    # 3. Queue & Play
    song_data = {"title": title, "url": stream_url, "duration": duration, "by": user_name}
    config.queues.setdefault(chat_id, []).append(song_data)

    join_status = await play_next(chat_id)
    if not join_status:
        await m.delete()
        return

    # 4. UI
    btn_prog = gen_btn_progressbar(duration, 0)
    text = f"<b>❍ Sᴛᴀʀᴛᴇᴅ Sᴛʀᴇᴀᴍɪɴɢ |</b>\n\n<b>‣ Tɪᴛʟᴇ :</b> {title}\n<b>‣ Rᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> {user_name}"
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=btn_prog, callback_data="prog_update")],
        [
            InlineKeyboardButton("▷", callback_data="resume_cb"),
            InlineKeyboardButton("Ⅱ", callback_data="pause_cb"),
            InlineKeyboardButton("⏭", callback_data="skip_cb"),
            InlineKeyboardButton("▢", callback_data="stop_cb")
        ]
    ])

    await m.delete()
    pmp = await client.send_photo(chat_id, photo="https://files.catbox.moe/uyum1c.jpg", caption=text, reply_markup=buttons)
    asyncio.create_task(update_timer(chat_id, pmp.id, duration))
