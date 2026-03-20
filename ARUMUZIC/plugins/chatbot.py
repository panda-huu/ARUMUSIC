import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus, ChatAction
from urllib.parse import quote # Iski wajah se error aa raha tha
import config 

# --- Configuration ---
CHAT_ENABLED = [] 
BOT_NAME = "ARU" 
BOT_USERNAME = "ARU_xOPUSERBOT" 

# Safe Owner ID check
OWNER_ID = 8566803656

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

    # Trigger Logic (Check if mentioned or replied to)
    bot_me = await client.get_me()
    is_mentioned = (
        (message.reply_to_message and message.reply_to_message.from_user.id == bot_me.id) or 
        (BOT_NAME.lower() in text.lower()) or 
        (BOT_USERNAME.lower() in text.lower())
    )

    # Group mein tabhi jab ON ho aur Mentioned ho
    if message.chat.type != "private":
        if chat_id not in CHAT_ENABLED or not is_mentioned:
            return

    # Typing Action
    try: await client.send_chat_action(chat_id, ChatAction.TYPING)
    except: pass

    # Owner Check
    is_owner = (user_id == OWNER_ID)
    prompt = OWNER_PROMPT if is_owner else USER_PROMPT

    try:
        # User query ko safely encode kar rahe hain
        encoded_query = quote(f"{prompt}\n\nUser: {text}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://sxyanu.vercel.app/api/asked?query={encoded_query}") as r:
                data = await r.json()
                # Try multiple keys because some APIs change them
                response = data.get("response") or data.get("reply") or data.get("message")

        if response:
            await message.reply_text(response)
    except Exception as e:
        print(f"Chatbot Error: {e}")
