import asyncio 
import aiohttp
import time
from urllib.parse import quote
from pyrogram.enums import ChatMemberStatus
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls.types import AudioPiped, HighQualityAudio
from pytgcalls import PyTgCalls
from ARUMUZIC.clients import bot, assistant, call 
import config

# --- Configuration for Queues ---
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
        try:
            await call.change_stream(chat_id, AudioPiped(stream_url, HighQualityAudio()))
        except:
            await call.join_group_call(chat_id, AudioPiped(stream_url, HighQualityAudio()))
        
        text = (
            f"<blockquote><b>❍ ɴᴇxᴛ sᴏɴɢ sᴛʀᴇᴀᴍ sᴛᴀʀᴛᴇᴅ |</b>\n\n"
            f"<b>‣ Tɪᴛʟᴇ :</b> <a href='{stream_url}'>{title}</a>\n"
            f"<b>‣ Rᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> `{user_name}`</blockquote>"
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

@call.on_stream_end()
async def stream_end_handler(client, update):
    chat_id = update.chat_id
    
    # Check karo agar queue mein aur gaane hain (Current ko chhod kar)
    if chat_id in config.queues and len(config.queues[chat_id]) > 1:
        # Agla gaana bajao
        await play_next(chat_id)
    else:
        # Agar koi gaana nahi bacha, toh sab saaf karo
        try:
            config.queues[chat_id] = [] # Queue reset
            await call.leave_group_call(chat_id)
        except:
            pass


async def update_timer(chat_id, message_id, duration):
    start_time = time.time()
    while True:
        await asyncio.sleep(15) 
        if chat_id not in config.queues or not config.queues[chat_id]: break
        elapsed_time = min(duration, int(time.time() - start_time))
        if elapsed_time >= duration: break 
        try:
            await bot.edit_message_reply_markup(chat_id, message_id,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text=gen_btn_progressbar(duration, elapsed_time), callback_data="prog_update")],
                    [InlineKeyboardButton("▷", "resume_cb"), InlineKeyboardButton("Ⅱ", "pause_cb"), InlineKeyboardButton("⏭", "skip_cb"), InlineKeyboardButton("▢", "stop_cb")]
                ]))
        except: break

# --- MAIN PLAY COMMAND ---
@Client.on_message(filters.command("play") & filters.group)
async def play_cmd(client, msg: Message):
    try: await msg.delete()
    except: pass
    
    chat_id = msg.chat.id
    user_name = msg.from_user.first_name if msg.from_user else "User"
    if len(msg.command) < 2: return await msg.reply("❌ **ɢɪᴠᴇ ᴀ ǫᴜᴇʀʏ!**")
    
    query = msg.text.split(None, 1)[1].strip()
    m = await msg.reply("<blockquote>🔎 <b>sᴇᴀʀᴄʜɪɴɢ...</b></blockquote>")

    # --- SMART ASSISTANT CHECK ---
    ast_id = (await assistant.get_me()).id
    is_joined = False
    
    try:
        ast_member = await client.get_chat_member(chat_id, ast_id)
        if ast_member.status == ChatMemberStatus.BANNED:
            await client.unban_chat_member(chat_id, ast_id)
            await m.edit("✅ **Assistant unbanned! Joining...**")
            invitelink = await client.export_chat_invite_link(chat_id)
            await assistant.join_chat(invitelink)
        is_joined = True
    except:
        # Assistant group mein nahi hai
        await m.edit("☎️ **Assistant joining group...**")
        try:
            if msg.chat.username:
                await assistant.join_chat(msg.chat.username)
                is_joined = True
            else:
                invitelink = await client.export_chat_invite_link(chat_id)
                await assistant.join_chat(invitelink)
                is_joined = True
        except:
            return await m.edit("❌ **Mujhe Admin banao aur 'Invite Users' permission do!**")

    # --- API SEARCH ---
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://jio-saa-van.vercel.app/result/?query={quote(query)}", timeout=15) as r:
                data = await r.json()
    except: return await m.edit("❌ **Search Error!**")

    if not data: return await m.edit("❌ **No results!**")
    
    track = data[0]
    title, duration = track.get("song"), int(track.get("duration", 0))
    stream_url = track.get("media_url") or track.get("download_url")
    song_data = {"title": title, "url": stream_url, "duration": duration, "by": user_name}

    if chat_id not in config.queues: config.queues[chat_id] = []

    # --- QUEUE LOGIC ---
    if len(config.queues[chat_id]) > 0:
        config.queues[chat_id].append(song_data)
        return await m.edit(f"<b>✅ ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ (#{len(config.queues[chat_id])-1})</b>\n🎵 **ᴛɪᴛʟᴇ:** {title}", 
                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("▷ ᴘʟᴀʏ ɴᴏᴡ", callback_data="skip_cb")]]))

    config.queues[chat_id].append(song_data)
    await m.delete()

    try:
        await call.join_group_call(chat_id, AudioPiped(stream_url, HighQualityAudio()))
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=gen_btn_progressbar(duration, 0), callback_data="prog_update")],
            [InlineKeyboardButton("▷", "resume_cb"), InlineKeyboardButton("Ⅱ", "pause_cb"), InlineKeyboardButton("⏭", "skip_cb"), InlineKeyboardButton("▢", "stop_cb")],
            [InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/ll_PANDA_BBY_ll"), InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url="https://t.me/sxyaru")]
        ])
        pmp = await client.send_photo(chat_id, photo="https://files.catbox.moe/cu442f.jpg", 
            caption=f"<blockquote><b>❍ Sᴛᴀʀᴛᴇᴅ Sᴛʀᴇᴀᴍɪɴɢ |</b>\n\n<b>‣ Tɪᴛʟᴇ :</b> {title}\n<b>‣ Rᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> `{user_name}`</blockquote>", 
            reply_markup=buttons)
        asyncio.create_task(update_timer(chat_id, pmp.id, duration))
    except Exception as e:
        if "No active group call" in str(e):
            return await client.send_message(chat_id, "❌ **Pehle Voice Chat start karo bhaya!**")
        config.queues[chat_id] = []
        await client.send_message(chat_id, f"❌ **Error:** {e}")

