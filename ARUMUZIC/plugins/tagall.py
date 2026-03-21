import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

# Global dictionary to track stop status
TAG_STOP = {}

@Client.on_message(filters.command(["tagall", "utag"]) & filters.group)
async def tag_all_members(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # --- ADMIN CHECK ---
    try:
        user = await client.get_chat_member(chat_id, user_id)
        if user.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply("❌ **ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!**")
    except Exception:
        return # Agar bot admin list fetch na kar paye

    # --- TAG TEXT ---
    tag_text = "ʜᴇʏ, ᴡᴀᴋᴇ ᴜᴘ!"
    if len(message.command) > 1:
        tag_text = message.text.split(None, 1)[1]

    # Set stop status for this chat to False
    TAG_STOP[chat_id] = False

    await message.reply(f"✨ **ᴛᴀɢɢɪɴɢ sᴛᴀʀᴛᴇᴅ...**\n`Query: {tag_text}`\n`Use /cancel to stop.`")
    
    # --- TAGGING LOGIC (REAL-TIME) ---
    usertxt = ""
    count = 0

    async for member in client.get_chat_members(chat_id):
        # Stop check
        if TAG_STOP.get(chat_id):
            break
        
        # Bots aur Deleted accounts ko skip karo
        if member.user.is_bot or member.user.is_deleted:
            continue

        # Tag format
        usertxt += f"[{member.user.first_name}](tg://user?id={member.user.id}) "
        count += 1

        # 5 members hote hi message send karo
        if count % 5 == 0:
            try:
                await client.send_message(chat_id, f"📢 **{tag_text}**\n\n{usertxt}")
                await asyncio.sleep(2) # Flood wait safety
                usertxt = "" # Text reset for next batch
            except Exception:
                pass

    # Cleanup
    if TAG_STOP.get(chat_id):
        await message.reply(f"🚫 **ᴛᴀɢɢɪɴɢ sᴛᴏᴘᴘᴇᴅ!**\nᴛᴏᴛᴀʟ ᴛᴀɢɢᴇᴅ: `{count}`")
    else:
        await message.reply(f"✅ **ᴀʟʟ ᴍᴇᴍʙᴇʀs ᴛᴀɢɢᴇᴅ!**\nᴛᴏᴛᴀʟ: `{count}`")
    
    TAG_STOP[chat_id] = False

@Client.on_message(filters.command(["cancel", "stopall"]) & filters.group)
async def stop_tagging(client, message: Message):
    chat_id = message.chat.id
    # Admin check for cancel
    user = await client.get_chat_member(chat_id, message.from_user.id)
    if user.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return
        
    TAG_STOP[chat_id] = True
    await message.reply("⏳ **sᴛᴏᴘᴘɪɴɢ ᴛᴀɢɢᴀʟʟ...**")
