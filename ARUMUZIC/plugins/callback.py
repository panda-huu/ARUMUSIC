import asyncio
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from ARUMUZIC.clients import bot, assistant, call
import config

# Note: Agar circular import error aaye toh is line ko skip_cb ke andar move kar dena
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
            "<b>/ping</b> - ᴘɪɴɢɪɴɢ\n\n"
            "<b>/chaton</b> - ᴄʜᴀᴛʙᴏᴛ ᴏɴ\n"
            "<b>/chatoff</b> - ᴄʜᴀᴛʙᴏᴛ ᴏғғ"
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

    elif data == "skip_cb": # <-- Yahan Indentation fix kar di
        try:
            if chat_id in config.queues and len(config.queues[chat_id]) > 1:
                await play_next(chat_id)
                await query.answer("Playing next song... ⏭")
                try: await query.message.delete()
                except: pass
            else:
                try:
                    await call.leave_group_call(chat_id)
                    if chat_id in config.queues:
                        config.queues.pop(chat_id)
                    await query.message.delete()
                    await query.answer("Queue empty! Left VC. ⏹", show_alert=True)
                except:
                    await query.answer("Nothing to skip!", show_alert=True)
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

    elif data == "seek_forward":
        try:
            await call.seek_stream(chat_id, 20)
            await query.answer("Seeking +20s... ⏭")
        except:
            await query.answer("Seek failed!", show_alert=True)

    elif data == "seek_back":
        try:
            await call.seek_stream(chat_id, -20) 
            await query.answer("Seeking -20s... ⏮")
        except:
            await query.answer("Seek failed!", show_alert=True)
            
    elif data == "prog_update":
        await query.answer("Updating progress...", show_alert=False)
