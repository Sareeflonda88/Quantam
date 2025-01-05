from pyrogram import Client, filters
from pyrogram.enums import ChatAction, ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from config import API_ID, API_HASH, BOT_TOKEN

app = Client("message_handler_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(bot, message):
    try:
        await message.reply_photo(
            photo="https://files.catbox.moe/k2l5a8.jpg",
            caption=(
                "🌟 🌟 Welcome to Healix AI Fitness Bot – Your Ultimate Fitness Companion! 🌟\n\n👨‍⚕️ What Can I Help With?\n"
                "🔹 Guide you through beginner fitness steps.\n"
                "🔹 Answer all your fitness-related questions.\n🔹 Create personalized daily fitness goals and diet plans.\n\n"
                "✨ How Does It Work?\n✅ It’s simple! Share your fitness needs, and I’ll deliver AI-driven insights tailored just for you—instantly and effortlessly.\n\n"
                "💪 Let’s elevate your fitness journey together—smarter, faster, and better! 💖"
            ),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        print(f"Error in /start command: {e}")
        await message.reply_text("❍ ᴇʀʀᴏʀ: Unable to process the command.")

# Handler for the /doctor command
@app.on_message(filters.command("doctor") & filters.group)
async def fetch_med_info(client, message):
    query = " ".join(message.command[1:])  # Extract the query after the command
    if not query:
        await message.reply_text("Please provide a medical query to ask.")
        return

    # Send typing action to indicate bot is working
    await client.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    # Use the API to get medical data
    api_url = f"https://fitness.codesearch.workers.dev/?chat={query}"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            reply = data.get("data", "Sorry, I couldn't fetch the data.")
        else:
            reply = "Failed to fetch data from the API."
    except Exception as e:
        reply = f"An error occurred: {e}"

    # Reply to the user
    await message.reply_text(reply)

# Handler for private message queries (DM/PM), ignoring commands
@app.on_message(filters.private & ~filters.command(["start", "doctor"]))
async def handle_private_query(client, message):
    query = message.text.strip()  # Use the message text as the query
    if not query:
        await message.reply_text("Please provide a medical query.")  # Inform the user if no query is provided
        return

    # Send typing action to indicate bot is working
    await client.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    # Use the API to get medical data
    api_url = f"https://fitness.codesearch.workers.dev/?chat={query}"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            reply = data.get("data", "Sorry, I couldn't fetch the data.")
        else:
            reply = "Failed to fetch data from the API."
    except Exception as e:
        reply = f"An error occurred: {e}"

    # Reply to the user
    await message.reply_text(reply)

if __name__ == "__main__":
    print("Bot is running...")
    app.run()
