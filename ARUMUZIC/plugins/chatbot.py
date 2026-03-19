import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

# --- Configuration ---
CHAT_ENABLED = [] # Database ki jagah memory list (Restart par reset ho jayegi)

SYSTEM_PROMPT = "You are ARU MUSIC BOT, a helpful and witty AI assistant. Respond in a friendly way, sometimes using Hinglish."

@Client.on_message(filters.command(["chaton"]) & filters.group)
async def chat_on(client, message: Message):
    # Admin Check
    user = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await message.reply("❌ **Only Admins can enable Chatbot!**")
    
    if message.chat.id not in CHAT_ENABLED:
        CHAT_ENABLED.append(message.chat.id)
        await message.reply("✅ **Chatbot Enabled!** Now I will reply to all messages.")
    else:
        await message.reply("🤖 **Chatbot is already ON.**")

@Client.on_message(filters.command(["chatoff"]) & filters.group)
async def chat_off(client, message: Message):
    # Admin Check
    user = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await message.reply("❌ **Only Admins can disable Chatbot!**")

    if message.chat.id in CHAT_ENABLED:
        CHAT_ENABLED.remove(message.chat.id)
        await message.reply("🚫 **Chatbot Disabled!** I will only respond to commands now.")
    else:
        await message.reply("📴 **Chatbot is already OFF.**")

@Client.on_message(filters.group & ~filters.bot & ~filters.command(["chaton", "chatoff"]))
async def chatbot_reply(client, message: Message):
    if message.chat.id not in CHAT_ENABLED:
        return

    # Jab koi reply kare ya message likhe
    query = message.text
    if not query:
        return

    # Bot ko thoda human feel dene ke liye typing action
    await client.send_chat_action(message.chat.id, "typing")

    try:
        # API Call with System Prompt
        # Note: Agar API system prompt support karti hai toh thik, 
        # nahi toh hum query ke saath merge karke bhejenge.
        full_query = f"{SYSTEM_PROMPT}\n\nUser: {query}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://sxyanu.vercel.app/api/asked?query={full_query}") as r:
                data = await r.json()
                response = data.get("response") or data.get("reply") # API keys ke hisab se check kar lena

        if response:
            await message.reply_text(response)
    except Exception as e:
        print(f"Chatbot Error: {e}")
