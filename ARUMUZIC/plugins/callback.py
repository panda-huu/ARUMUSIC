from ARUMUZIC.clients import bot, assistant, call
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# IMPORTANT: Inhe mangwana padega varna error aayega
from main import call  
import config 
# Agar play_next doosri file mein hai toh use import karein:
# from ARUMUZIC.plugins.play import play_next 

@Client.on_callback_query() # 👈 Yahan @bot ki jagah @Client hoga
async def cb_handler(client, query: CallbackQuery): # 👈 '_' ki jagah 'client' likho
    chat_id = query.message.chat.id
    data = query.data

    # --- Start & Help Menus ---
    if data == "help_menu":
        help_text = (
            "<b> ʙᴏᴛ ʜᴇʟᴘ ᴍᴇɴᴜ</b>\n\n"
            "<b>/play</b> [ꜱᴏɴɢ ɴᴀᴍᴇ]\n"  
            "<b>/ping</b> - Stats check"
        )
        await query.message.edit_caption(
            caption=help_text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="back_to_start")]])
        )

    elif data == "repo_menu":
        repo_text = (
            "<b> ʀᴇᴘᴏ ᴋʏᴀ ʟᴇɢᴀ ᴍᴀᴅᴀʀᴄʜᴏᴅ\nᴘᴀɴᴅᴀ ᴋᴀ ʟᴀɴᴅ ʟᴇʟᴇ ʙᴏʟ ʟᴇɢᴀ 😂🖕??</b>"
        )
        await query.message.edit_caption(
            caption=repo_text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="back_to_start")]])
        )

    elif data == "back_to_start":
        # bot_me nikalne ka sahi tareeka plugin mein:
        bot_me = await client.get_me() 
        text = (
            "<b>╔══════════════════╗</b>\n"
            "<b>   🎵 ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ 🎵   </b>\n"
            "<b>╚══════════════════╝</b>\n\n"
            "<b>👋 ʜᴇʟʟᴏ! ɪ ᴀᴍ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ</b>\n"
            "<b>ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ.</b>"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("❓ ʜᴇʟᴘ", callback_data="help_menu"), InlineKeyboardButton("📂 ʀᴇᴘᴏ", callback_data="repo_menu")],
            [InlineKeyboardButton("👤 ᴏᴡɴᴇʀ", url="https://t.me/sxyaru"), InlineKeyboardButton("📢 sᴜᴘᴘᴏʀᴛ", url="https://t.me/your_channel")],
            [InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f"https://t.me/{bot_me.username}?startgroup=true")]
        ])
        await query.message.edit_caption(caption=text, reply_markup=buttons)

    # --- Play Music Controls ---
    elif data == "pause_cb":
        try:
            await call.pause_stream(chat_id)
            await query.answer("Paused ⏸")
        except:
            await query.answer("Nothing playing!", show_alert=True)

    elif data == "resume_cb":
        try:
            await call.resume_stream(chat_id)
            await query.answer("Resumed ▶️")
        except:
            await query.answer("Nothing playing!", show_alert=True)

    elif data == "skip_cb":
        try:
            if chat_id in config.queues: # 👈 config.queues use karein
                config.queues[chat_id].pop(0)
            # await play_next(chat_id) # Iske liye play_next import hona chahiye upar
            await query.answer("Skipped ⏭")
        except:
            await query.answer("Nothing to skip!", show_alert=True)

    elif data == "stop_cb":
        try:
            await call.leave_group_call(chat_id)
            config.queues.pop(chat_id, None)
            await query.message.delete()
            await query.answer("Stopped & Left VC ⏹")
        except:
            await query.answer("Assistant not in VC!", show_alert=True)

    # --- Seek Logic ---
    elif data == "seek_forward":
        await query.answer("Seeking +20s... ⏭")

    elif data == "seek_back":
        await query.answer("Seeking -20s... ⏮")
