from pyrogram import Client, filters
from pyrogram.enums import ChatAction, ParseMode
import http.client
import json
from config import API_ID, API_HASH, BOT_TOKEN

app = Client("quantum_robotics_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# API configuration
API_HOST = "okai.p.rapidapi.com"
API_KEY = "661048094dmshd422f34bffd5dc0p1d4d56jsn3bbc61e1a120"

async def query_api(prompt):
    """Helper function to query the RapidAPI endpoint."""
    try:
        conn = http.client.HTTPSConnection(API_HOST)
        payload = json.dumps({"messages": [{"role": "user", "content": prompt}]})
        headers = {
            'x-rapidapi-key': API_KEY,
            'x-rapidapi-host': API_HOST,
            'Content-Type': "application/json"
        }
        conn.request("POST", "/v1/chat/completions", payload, headers)
        res = conn.getresponse()
        if res.status == 200:
            data = json.loads(res.read().decode("utf-8"))
            return data.get("choices", [{}])[0].get("message", {}).get("content", "Sorry, I couldn't fetch the data.")
        return "Failed to fetch data from the API."
    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        conn.close()

@app.on_message(filters.command("start"))
async def start_command(bot, message):
    """Handle /start command with a welcome message and photo."""
    try:
        await message.reply_photo(
            photo="https://files.catbox.moe/k2l5a8.jpg",
            caption=(
                "🌟 Welcome to Quantum Robotics – Your AI Fitness Coach! 🌟\n\n"
                "👨‍⚕️ What I Can Do:\n"
                "🔹 Guide beginners in fitness.\n"
                "🔹 Answer fitness questions.\n"
                "🔹 Create tailored daily goals & diet plans.\n\n"
                "💪 Share your needs, and I’ll provide instant AI-driven insights!\n"
                "Let’s boost your fitness journey! 💖"
            ),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        print(f"Error in /start: {e}")
        await message.reply_text("❍ Error: Unable to process the command.")

@app.on_message(filters.command("doctor") & filters.group)
async def fetch_med_info(client, message):
    """Handle /doctor command in groups."""
    query = " ".join(message.command[1:])
    if not query:
        await message.reply_text("Please provide a fitness query.")
        return

    await client.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    reply = await query_api(query)
    await message.reply_text(reply)

@app.on_message(filters.private & ~filters.command(["start", "doctor"]))
async def handle_private_query(client, message):
    """Handle private message queries (non-commands)."""
    query = message.text.strip()
    if not query:
        await message.reply_text("Please provide a fitness query.")
        return

    await client.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    reply = await query_api(query)
    await message.reply_text(reply)

if __name__ == "__main__":
    print("Quantum Robotics Bot is running...")
    app.run()
