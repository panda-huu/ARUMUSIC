import asyncio 
import aiohttp
import time
from urllib.parse import quote
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from pytgcalls.types import AudioPiped, HighQualityAudio
from ARUMUZIC.clients import bot, assistant, call 
import config

# --- Utils ---
def fmt_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}" if hours > 0 else f"{minutes:02}:{seconds:02}"

def gen_btn_progressbar(total_sec, current_sec):
    bar_length = 10  # 10 blocks se loading bar ekdum professional dikhti hai
    if total_sec <= 0: total_sec = 1
    
    percentage = min(100, max(0, (current_sec / total_sec) * 100))
    filled_blocks = int(percentage / (100 / bar_length))
    
    # Aapka naya sexy style implement kar diya:
    bar = "▰" * filled_blocks + "▱" * (bar_length - filled_blocks)
    
    return f"{fmt_time(current_sec)} {bar} {fmt_time(total_sec)}"


# --- Timer Logic ---
async def update_timer(chat_id, message_id, duration):
    start_time = time.time()
    while True:
        await asyncio.sleep(10)
        
        # Check if song was skipped or stopped
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
            # Jab gaana khatam ho jaye - AUTO PLAY NEXT
            if elapsed_time >= duration:
                if chat_id in config.queues and len(config.queues[chat_id]) > 0:
                    config.queues[chat_id].pop(0) # Purana gana remove
                await play_next(chat_id)
                break
        except Exception:
            break

# --- Core Functions ---
async def play_next(chat_id: int):
    if chat_id not in config.queues or not config.queues[chat_id]:
        try: await call.leave_group_call(chat_id)
        except: pass
        return

    song = config.queues[chat_id][0]
    title, url, duration, user = song["title"], song["url"], song["duration"], song["by"]
    
    try:
        await call.change_stream(chat_id, AudioPiped(url, HighQualityAudio()))
        
        text = (
            f"<b>❍ Nᴇxᴛ Sᴏɴɢ Sᴛᴀʀᴛᴇᴅ |</b>\n\n"
            f"<b>‣ Tɪᴛʟᴇ :</b> <a href='{url}'>{title}</a>\n"
            f"<b>‣ Dᴜʀᴀᴛɪᴏɴ :</b> <code>{fmt_time(duration)}</code>\n"
            f"<b>‣ Rᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> `{user}`"
        )
        btn_prog = gen_btn_progressbar(duration, 0)
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=btn_prog, callback_data="prog_update")],
            [InlineKeyboardButton("▷", "resume_cb"), InlineKeyboardButton("Ⅱ", "pause_cb"), InlineKeyboardButton("⏭", "skip_cb"), InlineKeyboardButton("▢", "stop_cb")],
            [InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/ll_PANDA_BBY_ll"), InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url="https://t.me/sxyaru")]
        ])
        
        pmp = await bot.send_photo(chat_id, photo="https://files.catbox.moe/uyum1c.jpg", caption=text, reply_markup=buttons)
        asyncio.create_task(update_timer(chat_id, pmp.id, duration))
    except Exception as e:
        print(f"Error in play_next: {e}")
        if chat_id in config.queues:
            config.queues[chat_id].pop(0)
            await play_next(chat_id)

@Client.on_message(filters.command("play") & filters.group)
async def play_cmd(client, msg: Message):
    try: await msg.delete()
    except: pass
    
    chat_id = msg.chat.id
    user_name = msg.from_user.first_name if msg.from_user else "User"

    # Assistant Check
    try:
        ast_info = await assistant.get_me()
        try:
            await client.get_chat_member(chat_id, ast_info.id)
        except:
            link = await client.export_chat_invite_link(chat_id)
            await assistant.join_chat(link)
    except: pass

    if len(msg.command) < 2: return await msg.reply("❌ **ɢɪᴠᴇ ᴀ ǫᴜᴇʀʏ!**")
    query = msg.text.split(None, 1)[1].strip()
    m = await msg.reply("🔎 <b>sᴇᴀʀᴄʜɪɴɢ...</b>")

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://jio-saa-van.vercel.app/result/?query={quote(query)}") as r:
            data = await r.json()

    if not data: return await m.edit("❌ **ɴᴏ ʀᴇsᴜʟᴛs ғᴏᴜɴᴅ!**")
    track = data[0]
    title, duration = track.get("song"), int(track.get("duration", 0))
    stream_url = track.get("media_url") or track.get("download_url")

    song_data = {"title": title, "url": stream_url, "duration": duration, "by": user_name}
    
    # Check if assistant is actually in VC
    if not await call.is_connected(chat_id):
        config.queues.pop(chat_id, None)

    # Queue Management
    if chat_id in config.queues and len(config.queues[chat_id]) > 0:
        config.queues[chat_id].append(song_data)
        # Added 'Play Now' button in Queue message as requested
        btn_queue = InlineKeyboardMarkup([[InlineKeyboardButton("▷ ᴘʟᴀʏ ɴᴏᴡ", callback_data="skip_cb")]])
        return await m.edit(f"✅ **ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ (ᴘᴏsɪᴛɪᴏɴ #{len(config.queues[chat_id])-1})**\n🎵 **ᴛɪᴛʟᴇ:** {title}", reply_markup=btn_queue)

    config.queues[chat_id] = [song_data]
    await m.delete()

    # Play Initial Song
    try:
        await call.join_group_call(chat_id, AudioPiped(stream_url, HighQualityAudio()))
        
        text = (
            f"<b>❍ Sᴛᴀʀᴛᴇᴅ Sᴛʀᴇᴀᴍɪɴɢ |</b>\n\n"
            f"<b>‣ Tɪᴛʟᴇ :</b> <a href='{stream_url}'>{title}</a>\n"
            f"<b>‣ Dᴜʀᴀᴛɪᴏɴ :</b> <code>{fmt_time(duration)}</code>\n"
            f"<b>‣ Rᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> `{user_name}`"
        )
        btn_prog = gen_btn_progressbar(duration, 0)
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=btn_prog, callback_data="prog_update")],
            [InlineKeyboardButton("▷", "resume_cb"), InlineKeyboardButton("Ⅱ", "pause_cb"), InlineKeyboardButton("⏭", "skip_cb"), InlineKeyboardButton("▢", "stop_cb")],
            [InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/ll_PANDA_BBY_ll"), InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url="https://t.me/sxyaru")]
        ])

        pmp = await client.send_photo(chat_id, photo="https://files.catbox.moe/cu442f.jpg", caption=text, reply_markup=buttons)
        asyncio.create_task(update_timer(chat_id, pmp.id, duration))
    except Exception as e:
        await client.send_message(chat_id, f"❌ **ᴇʀʀᴏʀ:** {e}")
