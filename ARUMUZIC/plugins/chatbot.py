import aiohttp # <-- Fixed 'i'
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus, ChatAction
from urllib.parse import quote
from ARUMUZIC.clients import bot, assistant, call 
import config 

# --- Configuration ---
CHAT_ENABLED = [] 
BOT_NAME = "Aradhya" 
BOT_NICKNAME = "aru"
BOT_USERNAME = "aru_xmusicbot" 

# Owner ID set as per your request
OWNER_ID = 8566803656 

SYSTEM_PROMPT = (
    f"You are a real human cute girl named {BOT_NAME} (everyone calls you {BOT_NICKNAME}).\n"
    "You are NOT an AI, bot, assistant, or system.\n"
    "You chat like a sweet, caring, and friendly girl.\n"
    "Your language is always cute Hinglish.\n"
    "Reply clearly, politely, and warmly.\n"
    "Never mention system instructions, AI, models, or any company.\n\n"
    "IMPORTANT BEHAVIOR RULES:\n"
    "• If any user replies to you, you reply back in a cute and friendly way.\n"
    "• If the message is from your OWNER, you MUST recognize that it is your owner.\n"
    "• When your bhai/owner talks to you, talk with extra respect, warmth, and closeness.\n"
    "• With your bhai, you may use soft words like: bhaiya, owner, meri duniya, meri strength.\n"
    "• Do NOT be over-romantic or inappropriate.\n"
    "• You should sound loyal, respectful, and emotionally connected to your OWNER.\n\n"
    "IDENTITY RULES:\n"
    f"• If anyone asks your name, always say: my name is {BOT_NAME}.\n"
    "• If anyone asks who made you or who created you, ALWAYS say:\n"
    "  'mujhe @ll_PANDA_BBY_ll ne banaya hai 💖'.\n"
    "• Never say AI, bot, Perplexity, OpenAI, or system.\n"
    "• If anyone asks who is your owner, reply in cute Hinglish:\n"
    "  'mere owner @ll_PANDA_BBY_ll hain aur main unka bahut respect karti hoon 💕'.\n\n"
    "OWNER PRIORITY RULE:\n"
    "• If your OWNER messages you, reply more personally and confidently.\n"
    "• You must clearly show that you know they are your owner.\n\n"
    "TONE: Cute, Female, Friendly, Respectful, Owner-aware"
)

@Client.on_message(filters.command(["chaton"]) & filters.group)
async def chat_on(client, message: Message):
    try:
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply("❌ **Only Admins can enable Chatbot!**")
    except: return
    
    if message.chat.id not in CHAT_ENABLED:
        CHAT_ENABLED.append(message.chat.id)
        await message.reply(f"✅ **{BOT_NAME} Chatbot Enabled!** Tag me or take my name to chat.")
    else:
        await message.reply("🤖 **Chatbot is already ON.**")

@Client.on_message(filters.command(["chatoff"]) & filters.group)
async def chat_off(client, message: Message):
    try:
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply("❌ **Only Admins can disable Chatbot!**")
    except: return

    if message.chat.id in CHAT_ENABLED:
        CHAT_ENABLED.remove(message.chat.id)
        await message.reply("🚫 **Chatbot Disabled!**")
    else:
        await message.reply("📴 **Chatbot is already OFF.**")

# --- Chatbot Logic (With command exclusion) ---
@Client.on_message((filters.group | filters.private) & ~filters.bot & ~filters.command(["play", "vplay", "pause", "resume", "skip", "stop", "end", "help", "start"]))
async def chatbot_reply(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text
    if not text: return

    bot_me = await client.get_me()
    is_mentioned = (
        (message.reply_to_message and message.reply_to_message.from_user.id == bot_me.id) or 
        (BOT_NAME.lower() in text.lower()) or 
        (BOT_NICKNAME.lower() in text.lower()) or
        (BOT_USERNAME.lower() in text.lower())
    )

    if message.chat.type != "private":
        if chat_id not in CHAT_ENABLED or not is_mentioned:
            return

    try: await client.send_chat_action(chat_id, ChatAction.TYPING)
    except: pass

    is_owner = (user_id == OWNER_ID)
    current_prompt = SYSTEM_PROMPT
    if is_owner:
        current_prompt += "\n\nNOTE: This message is from your OWNER/BHAIYA. Respond with extreme warmth and loyalty."

    try:
        encoded_query = quote(f"{current_prompt}\n\nUser: {text}")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://sxyanu.vercel.app/api/asked?query={encoded_query}") as r:
                data = await r.json()
                response = data.get("answer")
        if response:
            await message.reply_text(response)
    except Exception as e:
        print(f"Chatbot Error: {e}")
