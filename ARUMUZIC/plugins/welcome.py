import random
import asyncio
from ARUMUZIC.clients import bot 
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# --- Random Welcome Images ---
WELCOME_IMAGES = [
    "https://files.catbox.moe/nacfzm.jpg",
    "https://files.catbox.moe/x4lzbx.jpg",
    "https://files.catbox.moe/g6cmb2.jpg",
    "https://files.catbox.moe/3hxb96.jpg",
    "https://files.catbox.moe/3h3vqz.jpg",
    "https://files.catbox.moe/yah7a9.jpg"
]

WELCOME_TEXT = """🌸✨ ──────────────────── ✨🌸  
🎊 <b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴏᴜʀ ɢʀᴏᴜᴘ</b> 🎊  
  
🌹 <b>ɴᴀᴍᴇ</b> ➤ {name}  
🆔 <b>ᴜsᴇʀ ɪᴅ</b> ➤ <code>{user_id}</code>  
🏠 <b>ɢʀᴏᴜᴘ</b> ➤ {chat_title}  
  
💕 <b>ᴡᴇ'ʀᴇ sᴏ ʜᴀᴘᴘʏ ᴛᴏ ʜᴀᴠᴇ ʏᴏᴜ ʜᴇʀᴇ!</b>  
✨ <b>ғᴇᴇʟ ғʀᴇᴇ ᴛᴏ sʜᴀʀᴇ ᴀɴᴅ ᴇɴᴊᴏʏ!</b>  
⚡ <b>ᴇɴᴊᴏʏ ʏᴏᴜʀ ᴇxᴘᴇʀɪᴇɴᴄᴇ ᴡɪᴛʜ ᴛʜɪs ʙᴏᴛ</b>  
  
💝 <b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ ➤</b> <a href="https://t.me/sxyaru">˹ᴀʀᴜ × ᴀᴘɪ˼ × [ʙᴏᴛs]</a>  
🌸✨ ──────────────────── ✨🌸  
"""

@bot.on_message(filters.new_chat_members & filters.group, group=10) # group=10 dala taaki dusre filters se clash na ho
async def welcome_user(client, msg: Message):
    # DEBUG PRINT: Terminal mein dekho ye line aa rahi hai ya nahi
    print(f"--- DEBUG: New Member Event in {msg.chat.title} ---")

    for user in msg.new_chat_members:
        if user.is_self:
            continue
            
        try:
            name = user.first_name or "User"
            user_id = user.id
            chat_title = msg.chat.title
            
            photo = random.choice(WELCOME_IMAGES)
            
            caption = WELCOME_TEXT.format(
                name=name, 
                user_id=user_id, 
                chat_title=chat_title
            )

            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("• ᴄʜᴀɴɴᴇʟ •", url="https://t.me/sxyaru"),
                    InlineKeyboardButton("• ᴏᴡɴᴇʀ •", url="https://t.me/ll_PANDA_BBY_ll")
                ]
            ])

            wel_msg = await bot.send_photo( # Yahan 'bot' use kiya direct
                chat_id=msg.chat.id,
                photo=photo,
                caption=caption,
                reply_markup=buttons
            )

            await asyncio.sleep(60)
            try:
                await wel_msg.delete()
            except:
                pass

        except Exception as e:
            print(f"[WELCOME ERROR] {e}")
