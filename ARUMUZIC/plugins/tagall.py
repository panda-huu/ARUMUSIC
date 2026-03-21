import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from ARUMUZIC.clients import bot # Yeh sabse zaroori line hai

@bot.on_message(filters.command(["tagall", "utag"]) & filters.group)
async def tag_all_members(client, message: Message):
    chat_id = message.chat.id
    
    # Sabse pehle ek simple reply check karne ke liye
    try:
        m = await message.reply("⚡ **ᴛᴀɢɢɪɴɢ sᴛᴀʀᴛᴇᴅ...**")
    except Exception as e:
        print(f"Error sending message: {e}")
        return

    count = 0
    usertxt = ""
    
    try:
        async for member in client.get_chat_members(chat_id):
            if member.user.is_bot or member.user.is_deleted:
                continue
            
            usertxt += f"[{member.user.first_name}](tg://user?id={member.user.id}) "
            count += 1
            
            if count % 5 == 0:
                await client.send_message(chat_id, f"📢 **ᴡᴀᴋᴇ ᴜᴘ!**\n\n{usertxt}")
                await asyncio.sleep(2)
                usertxt = ""
        
        await m.edit(f"✅ **ᴅᴏɴᴇ!** ᴛᴀɢɢᴇᴅ: `{count}`")
    except Exception as e:
        await message.reply(f"❌ **Error:** `{e}`")
