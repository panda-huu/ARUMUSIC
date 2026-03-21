import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from ARUMUZIC.clients import bot # Yahan dhyan dein: client ka naam 'bot' hi hona chahiye

# Global dictionary to track stop status
TAG_STOP = {}

@bot.on_message(filters.command(["tagall", "utag", "all"]) & filters.group)
async def tag_all_members(client: Client, message: Message):
    chat_id = message.chat.id
    
    # --- ADMIN CHECK ---
    try:
        user = await client.get_chat_member(chat_id, message.from_user.id)
        if user.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply("❌ **Only Admins can use this!**")
    except Exception:
        return 

    # --- TAG TEXT ---
    tag_text = "ʜᴇʏ, ᴡᴀᴋᴇ ᴜᴘ!"
    if len(message.command) > 1:
        tag_text = message.text.split(None, 1)[1]

    TAG_STOP[chat_id] = False
    
    # Pehla reply check karne ke liye ki bot zinda hai
    m = await message.reply("⚡ **ᴛᴀɢɢɪɴɢ sᴛᴀʀᴛᴇᴅ...**")
    
    count = 0
    usertxt = ""

    try:
        # Real-time tagging (No memory load)
        async for member in client.get_chat_members(chat_id):
            if TAG_STOP.get(chat_id):
                break
            
            if member.user.is_bot or member.user.is_deleted:
                continue

            # Mention format
            usertxt += f"[{member.user.first_name}](tg://user?id={member.user.id}) "
            count += 1

            # Har 5 members par message bhejo
            if count % 5 == 0:
                await client.send_message(chat_id, f"📢 **{tag_text}**\n\n{usertxt}")
                await asyncio.sleep(2) # Flood wait safety
                usertxt = ""

        # Last batch
        if usertxt and not TAG_STOP.get(chat_id):
            await client.send_message(chat_id, f"📢 **{tag_text}**\n\n{usertxt}")

    except Exception as e:
        await message.reply(f"❌ **Error:** `{e}`")

    await m.edit(f"✅ **ᴛᴀɢɢɪɴɢ ᴅᴏɴᴇ!**\nᴛᴏᴛᴀʟ: `{count}`")
    TAG_STOP[chat_id] = False

@bot.on_message(filters.command(["cancel", "stopall"]) & filters.group)
async def stop_tagging(client, message: Message):
    TAG_STOP[message.chat.id] = True
    await message.reply("⏳ **sᴛᴏᴘᴘɪɴɢ...**")
