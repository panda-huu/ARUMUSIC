import asyncio
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from ARUMUZIC.clients import bot, assistant, call
import config

# --- IMPORTANT: play_next ko yahan import karna zaroori hai skip ke liye ---
from ARUMUZIC.plugins.play import play_next 

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
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
        bot_me = await client.get_me() 
        text = (
        "<b>╔══════════════════╗</b>\n"
        "<b>   🎵 ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ 🎵   </b>\n"
        "<b>╚══════════════════╝</b>\n\n"
        "<b>👋 ʜᴇʟʟᴏ! ɪ ᴀᴍ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ</b>\n"
        "<b>ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ.</b>\n\n"
        "✨ <b>ᴍᴀᴅᴇ ᴡɪᴛʜ ❤️ ʙʏ:</b> <a href='https://t.me/sxyaru'>sxyaru</a>"
    )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("❓ ʜᴇʟᴘ", callback_data="help_menu"), InlineKeyboardButton("📂 ʀᴇᴘᴏ", callback_data="repo_menu")],
            [InlineKeyboardButton("👤 ᴏᴡɴᴇʀ", url="https://t.me/sxyaru"), InlineKeyboardButton("📢 sᴜᴘᴘᴏʀᴛ", url="https://t.me/sxyaru")],
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
            if chat_id in config.queues and len(config.queues[chat_id]) > 0:
                # Current gana hatao
                config.queues[chat_id].pop(0)
                # Agla gana play karo
                await play_next(chat_id)
                await query.answer("Skipped ⏭")
                await query.message.delete() # Purana menu delete
            else:
                await query.answer("Queue is empty!", show_alert=True)
        except Exception as e:
            await query.answer(f"Error: {e}", show_alert=True)

    elif data == "stop_cb":
        try:
            await call.leave_group_call(chat_id)
            if chat_id in config.queues:
                config.queues.pop(chat_id)
            await query.message.delete()
            await query.answer("Stopped & Left VC ⏹")
        except:
            await query.answer("Assistant not in VC!", show_alert=True)

    # --- Seek Logic (Bonus for Background) ---
    elif data == "seek_forward":
        try:
            await call.seek_stream(chat_id, 20) # 20s forward
            await query.answer("Seeking +20s... ⏭")
        except:
            await query.answer("Seek failed!", show_alert=True)

    elif data == "seek_back":
        try:
            # Note: Negative value seek back ke liye hoti hai
            await call.seek_stream(chat_id, -20) 
            await query.answer("Seeking -20s... ⏮")
        except:
            await query.answer("Seek failed!", show_alert=True)
            
    elif data == "prog_update":
        await query.answer("Updating progress...", show_alert=False)
