import asyncio 
import aiohttp
import time
from urllib.parse import quote
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls.types import AudioPiped, HighQualityAudio
from pytgcalls import PyTgCalls # Import this for decorator
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

# --- Play Next Function (Core) ---
async def play_next(chat_id: int):
    if chat_id not in config.queues or len(config.queues[chat_id]) <= 1:
        config.queues[chat_id] = []
        try: await call.leave_group_call(chat_id)
        except: pass
        return

    config.queues[chat_id].pop(0) # Purana gana remove
    song = config.queues[chat_id][0] # Naya gana pick
    
    title, stream_url, duration, user_name = song["title"], song["url"], song["duration"], song["by"]

    try:
        try:
            await call.change_stream(chat_id, AudioPiped(stream_url, HighQualityAudio()))
        except:
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
    except Exception as e:
        print(f"Error in play_next: {e}")
        await play_next(chat_id)

# --- AUTO PLAY HANDLER (Magic Line) ---
@call.on_stream_end()
async def stream_end_handler(client, update):
    chat_id = update.chat_id
    await play_next(chat_id)

# --- Timer Logic ---
async def update_timer(chat_id, message_id, duration):
    start_time = time.time()
    while True:
        await asyncio.sleep(15) 
        if chat_id not in config.queues or not config.queues[chat_id]:
            break
        elapsed_time = min(duration, int(time.time() - start_time))
        if elapsed_time >= duration: break 
        
        try:
            await bot.edit_message_reply_markup(
                chat_id, message_id,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text=gen_btn_progressbar(duration, elapsed_time), callback_data="prog_update")],
                    [InlineKeyboardButton("▷", "resume_cb"), InlineKeyboardButton("Ⅱ", "pause_cb"), InlineKeyboardButton("⏭", "skip_cb"), InlineKeyboardButton("▢", "stop_cb")],
                    [InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/ll_PANDA_BBY_ll"), InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url="https://t.me/sxyaru")]
                ])
            )
        except: break

@Client.on_message(filters.command("play") & filters.group)
async def play_cmd(client, msg: Message):
    chat_id = msg.chat.id
    user_name = msg.from_user.first_name if msg.from_user else "User"

    if len(msg.command) < 2: return await msg.reply("❌ **ɢɪᴠᴇ ᴀ ǫᴜᴇʀʏ!**")
    query = msg.text.split(None, 1)[1].strip()
    m = await msg.reply("<blockquote>🔎 <b>sᴇᴀʀᴄʜɪɴɢ...</b></blockquote>")

    # --- ADVANCED ASSISTANT JOIN/UNBAN LOGIC ---
    try:
        assistant_id = (await assistant.get_me()).id
        try:
            # Check agar assistant group mein hai
            get_ast = await client.get_chat_member(chat_id, assistant_id)
            if get_ast.status == ChatMemberStatus.BANNED:
                # Agar Banned hai toh Unban karo
                await client.unban_chat_member(chat_id, assistant_id)
                await m.edit("✅ **Assistant unbanned! Joining now...**")
        except:
            # Agar assistant group mein nahi hai
            await m.edit("☎️ **Assistant joining group...**")
            try:
                # Private group ke liye invite link
                invitelink = await client.export_chat_invite_link(chat_id)
                await assistant.join_chat(invitelink)
            except:
                # Public group ke liye username se join
                if msg.chat.username:
                    await assistant.join_chat(msg.chat.username)
                else:
                    return await m.edit("❌ **Mujhe Admin banao aur 'Invite Users' permission do taaki assistant join ho sake!**")
    except Exception as e:
        return await m.edit(f"❌ **Assistant Join Error:** `{e}`")

    # --- API Search ---
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://jio-saa-van.vercel.app/result/?query={quote(query)}", timeout=15) as r:
                data = await r.json()
    except Exception as e:
        return await m.edit(f"❌ **sᴇᴀʀᴄʜ ᴇʀʀᴏʀ:** `{e}`")

    if not data: return await m.edit("❌ **ɴᴏ ʀᴇsᴜʟᴛs ғᴏᴜɴᴅ!**")
    
    # ... (Baaki ka Queue aur Play logic same rahega jo pehle diya tha) ...

    
    track = data[0]
    title, duration = track.get("song"), int(track.get("duration", 0))
    stream_url = track.get("media_url") or track.get("download_url")
    song_data = {"title": title, "url": stream_url, "duration": duration, "by": user_name}

    if chat_id not in config.queues: config.queues[chat_id] = []

    if len(config.queues[chat_id]) > 0:
        config.queues[chat_id].append(song_data)
        btn_queue = InlineKeyboardMarkup([[InlineKeyboardButton("▷ ᴘʟᴀʏ ɴᴏᴡ", callback_data="skip_cb")]])
        return await m.edit(f"<b>✅ ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ (#{len(config.queues[chat_id])-1})</b>\n🎵 **ᴛɪᴛʟᴇ:** {title}", reply_markup=btn_queue)

    config.queues[chat_id].append(song_data)
    await m.delete()

    try:
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
