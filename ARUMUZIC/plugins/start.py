import asyncio
from ARUMUZIC.clients import bot, assistant, call
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

@Client.on_message(filters.command("start"))
async def start_cmd(client, msg: Message):
    # 1. User ka command delete karne ki koshish
    try:
        await msg.delete()
    except:
        pass

    # 2. Bot info fetch karna (client use karke)
    me = await client.get_me()
    bot_name = me.first_name
    bot_username = me.username
    
    # ──────── ANIMATION START ────────
    # Phase 1: HEY
    m = await client.send_message(msg.chat.id, "<code>ʜᴇʏ...</code>")
    await asyncio.sleep(0.8)
    
    # Phase 2: HOW ARE YOU
    await m.edit_text("<code>ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ? ✨</code>")
    await asyncio.sleep(0.8)
    
    # Phase 3: STARTING...
    await m.edit_text(f"<code>ɪ ᴀᴍ {bot_name} 🎵\nsᴛᴀʀᴛɪɴɢ.....</code>")
    await asyncio.sleep(1.0)
    
    # Animation delete
    await m.delete()
    # ──────── ANIMATION END ────────

    START_IMG = "https://files.catbox.moe/uyum1c.jpg" 
    
    text = (
        "<b>╔══════════════════╗</b>\n"
        "<b>   🎵 ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ 🎵   </b>\n"
        "<b>╚══════════════════╝</b>\n\n"
        "<b>👋 ʜᴇʟʟᴏ! ɪ ᴀᴍ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ</b>\n"
        "<b>ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ.</b>\n\n"
        "✨ <b>ᴍᴀᴅᴇ ᴡɪᴛʜ ❤️ ʙʏ:</b> <a href='https://t.me/sxyaru'>sxyaru</a>"
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❓ ʜᴇʟᴘ", callback_data="help_menu"),
            InlineKeyboardButton("📂 ʀᴇᴘᴏ", callback_data="repo_menu")
        ],
        [
            InlineKeyboardButton("👤 ᴏᴡɴᴇʀ", url="https://t.me/ll_PANDA_BBY_ll"),
            InlineKeyboardButton("📢 sᴜᴘᴘᴏʀᴛ", url="https://t.me/sxyaru") # Support link sahi kar di
        ],
        [
            InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f"https://t.me/{bot_username}?startgroup=true")
        ]
    ])

    await client.send_photo(
        msg.chat.id,
        photo=START_IMG,
        caption=text,
        reply_markup=buttons
    )
