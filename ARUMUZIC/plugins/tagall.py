import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

# Global dictionary to track stop status
TAG_STOP = {}

# Command filters mein '/' aur '!' dono allow kar diye
@Client.on_message(filters.command(["tagall", "utag"], prefixes=["/", "!", ""]) & filters.group)
async def tag_all_members(client: Client, message: Message):
    chat_id = message.chat.id
    
    # Check if bot is Admin (Zaroori hai members list ke liye)
    bot_obj = await client.get_chat_member(chat_id, "me")
    if bot_obj.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await message.reply("❌ **ʙᴏᴛ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴛᴀɢ ᴍᴇᴍʙᴇʀs!**")

    # Tag message
    tag_text = "ʜᴇʏ, ᴡᴀᴋᴇ ᴜᴘ!"
    if len(message.command) > 1:
        tag_text = message.text.split(None, 1)[1]

    TAG_STOP[chat_id] = False
    await message.reply(f"✨ **ᴛᴀɢɢɪɴɢ sᴛᴀʀᴛᴇᴅ...**\n`Use /cancel to stop.`")
    
    usertxt = ""
    count = 0

    try:
        async for member in client.get_chat_members(chat_id):
            if TAG_STOP.get(chat_id):
                break
            
            if member.user.is_bot or member.user.is_deleted:
                continue

            # Har member ka link banaya
            usertxt += f"[{member.user.first_name}](tg://user?id={member.user.id}) "
            count += 1

            # Har 5 members par message bhejo
            if count % 5 == 0:
                await client.send_message(chat_id, f"📢 **{tag_text}**\n\n{usertxt}")
                await asyncio.sleep(3) # Flood wait se bachne ke liye gap
                usertxt = ""

        # Last batch agar 5 se kam members bache hon toh
        if usertxt and not TAG_STOP.get(chat_id):
            await client.send_message(chat_id, f"📢 **{tag_text}**\n\n{usertxt}")

    except Exception as e:
        await message.reply(f"❌ **Error:** `{e}`")

    TAG_STOP[chat_id] = False

@Client.on_message(filters.command(["cancel", "stopall"], prefixes=["/", "!", ""]) & filters.group)
async def stop_tagging(client, message: Message):
    TAG_STOP[message.chat.id] = True
    await message.reply("⏳ **sᴛᴏᴘᴘɪɴɢ...**")
