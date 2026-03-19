import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus, ChatAction
import config # Owner ID nikalne ke liye

# --- Configuration ---
CHAT_ENABLED = [] 
BOT_NAME = "ARU" # Aapka bot name
BOT_USERNAME = "sxyaru" # Aapka bot username (without @)

# Owner ke liye alag prompt aur Normal users ke liye alag
OWNER_PROMPT = "You are ARU MUSIC BOT. The user talking to you is your OWNER and CREATOR. Be very respectful, loyal, and call him 'Sir' or 'Boss'. Use Hinglish."
USER_PROMPT = f"You are {BOT_NAME}, a helpful and witty AI assistant. Respond in a friendly way. Sometimes use Hinglish."

@Client.on_message(filters.command(["chaton"]) & filters.group)
async def chat_on(client, message: Message):
    user = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await message.reply("❌ **Only Admins can enable Chatbot!**")
    
    if message.chat.id not in CHAT_ENABLED:
        CHAT_ENABLED.append(message.chat.id)
        await message.reply(f"✅ **{BOT_NAME} Chatbot Enabled!** Mention me or take my name to chat.")
    else:
        await message.reply("🤖 **Chatbot is already ON.**")

@Client.on_message(filters.command(["chatoff"]) & filters.group)
async def chat_off(client, message: Message):
    user = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await message.reply("❌ **Only Admins can disable Chatbot!**")

    if message.chat.id in CHAT_ENABLED:
        CHAT_ENABLED.remove(message.chat.id)
        await message.reply("🚫 **Chatbot Disabled!**")
    else:
        await message.reply("📴 **Chatbot is already OFF.**")

# --- Chatbot Logic ---
@Client.on_message((filters.group | filters.private) & ~filters.bot)
async def chatbot_reply(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text
    
    if not text:
        return

    # 1. Private Chat: Hamesha reply karega
    # 2. Group Chat: Sirf tab reply karega jab /chaton ho AND (Tag kiya ho ya Name liya ho)
    is_mentioned = (
        message.reply_to_message and message.reply_to_message.from_user.id == (await client.get_me()).id
    ) or (BOT_NAME.lower() in text.lower()) or (BOT_USERNAME.lower() in text.lower())

    if message.chat.type != "private":
        if chat_id not in CHAT_ENABLED or not is_mentioned:
            return

    # Typing Action
    try: await client.send_chat_action(chat_id, ChatAction.TYPING)
    except: pass

    # Owner Check (Assuming OWNER_ID is in config.py)
    is_owner = user_id == config.OWNER_ID 
    prompt = OWNER_PROMPT if is_owner else USER_PROMPT

    try:
        full_query = f"{prompt}\n\nUser: {text}"
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://sxyaru.vercel.app/api/asked?query={full_query}") as r:
                data = await r.json()
                response = data.get("response") or data.get("reply") or data.get("message")

        if response:
            await message.reply_text(response)
    except Exception as e:
        print(f"Chatbot Error: {e}")
