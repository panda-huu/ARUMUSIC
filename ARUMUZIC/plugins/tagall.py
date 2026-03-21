import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

@Client.on_message(filters.command(["tagall", "utag"], prefixes=["/", "!", ""]))
async def tag_test(client: Client, message: Message):
    # Sirf ye check karne ke liye ki bot active hai
    print(f"Command received in: {message.chat.title}") 
    
    chat_id = message.chat.id
    
    # 1. Simple Reply Test
    m = await message.reply("⚡ **ᴛᴀɢɢɪɴɢ sᴛᴀʀᴛᴇᴅ...**")
    
    # 2. Members fetch logic
    try:
        count = 0
        usertxt = ""
        
        # Limit 50 rakha hai test ke liye
        async for member in client.get_chat_members(chat_id, limit=50):
            if member.user.is_bot or member.user.is_deleted:
                continue
            
            usertxt += f"[{member.user.first_name}](tg://user?id={member.user.id}) "
            count += 1
            
            if count % 5 == 0:
                await client.send_message(chat_id, f"📢 **ᴡᴀᴋᴇ ᴜᴘ!**\n\n{usertxt}")
                await asyncio.sleep(2)
                usertxt = ""
        
        await message.reply(f"✅ **ᴅᴏɴᴇ!** ᴛᴀɢɢᴇᴅ: `{count}`")
        
    except Exception as e:
        await message.reply(f"❌ **ᴇʀʀᴏʀ:** `{e}`\n\n*Make sure I am Admin!*")
