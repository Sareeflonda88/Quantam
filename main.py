from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import json
import secrets
import asyncio
import logging
import re
import requests
import os

# Pyrogram bot configuration
app = Client(
    name="OkaiBot",
    api_id=28362125,
    api_hash="c750e5872a2af51801d9b449983f4c84",
    bot_token="7038637559:AAFmvn2kmNuN2MukROcmc12B2jBgU8WuJGU"
)

# File to store user chat IDs and secrets
DATA_FILE = 'users.json'

# Simulated subscription storage (in-memory for simplicity)
subscribed_users = set()

# Track user states (e.g., whether they are in ai_qa mode or waiting for CSV)
user_states = {}

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API configuration
API_KEY = "661048094dmshd422f34bffd5dc0p1d4d56jsn3bbc61e1a120"  # Replace with your actual RapidAPI key
BASE_URL = "https://okai.p.rapidapi.com/v1/chat"  # Replace with the actual API endpoint
AI_MODEL = "quantum"  # Replace with the actual model name

# Load and save user data
def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Welcome message
WELCOME_MESSAGE = """
Welcome to QuantroBotics Quantum-Inspired AI Bot!

This assistant helps you make the most of quantum-inspired AI in robotics, automation, and data science.
Here’s what you can do:

🔹 Analyze your data — Upload your CSV logs for instant anomaly detection and optimization.
🔹 Optimize paths/tasks — Upload grid maps or task lists to get quantum-accelerated solutions.
🔹 AI Q&A — Ask anything about quantum-inspired AI, robotics, or implementation advice (powered by AI).
🔹 Get scheduled reports — Subscribe for weekly summaries and actionable tips.

Start by selecting an option below or use the menu commands.

➕ Tips:
- Use /getid to find your chat ID
- Use /webhooksecret to get or reset your secure webhook secret
- Use /unsubscribe to stop reports anytime

📚 Need help? Just ask!
"""

# Back to Menu button
def get_back_button():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]]
    )

# Main menu keyboard
def get_main_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📈 Analyze Data (CSV)", callback_data="analyze_data")],
            [InlineKeyboardButton("🗺️ Pathfinding/Optimization", callback_data="optimize_tasks")],
            [InlineKeyboardButton("💬 Ask Quantum AI (AI)", callback_data="ai_qa")],
            [InlineKeyboardButton("⏰ Subscribe For Weekly Reports", callback_data="subscribe_reports")],
            [InlineKeyboardButton("💡 About Quantum-Inspired AI", callback_data="about_quantum_ai")],
            [InlineKeyboardButton("🔑 My Chat ID & Webhook Secrets", callback_data="get_chat_id")]
        ]
    )

# API request function
async def make_api_request(query, model=AI_MODEL):
    payload = {
        "messages": [
            {
                "role": "user",
                "content": query
            }
        ],
        "stream": False,
        "model": model
    }
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "okai.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(BASE_URL, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "Sorry, I couldn't fetch the data.")
        else:
            return f"Failed to fetch data from the API. Status code: {response.status_code}"
    except Exception as e:
        return f"An error occurred: {e}"

# Start command handler
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    chat_id = str(message.chat.id)
    data = load_data()

    if chat_id not in data:
        # Generate a unique webhook secret
        secret = secrets.token_hex(16)
        data[chat_id] = {'webhook_secret': secret}
        save_data(data)
        message_text = f'✅ Welcome! Your webhook secret is:\n\n{secret}\n\nKeep it safe!\n\n{WELCOME_MESSAGE}'
    else:
        message_text = WELCOME_MESSAGE

    # Reset user state on /start
    user_states[chat_id] = None
    await message.reply(message_text, reply_markup=get_main_menu())

# Regen secret command handler
@app.on_message(filters.command("regensecret"))
async def regen_secret_command(client: Client, message: Message):
    chat_id = str(message.chat.id)
    data = load_data()

    if chat_id in data:
        # Generate a new webhook secret
        new_secret = secrets.token_hex(16)
        data[chat_id]['webhook_secret'] = new_secret
        save_data(data)
        await message.reply(f"🔑 Your new webhook secret is:\n\n{new_secret}\n\nKeep it safe!", reply_markup=get_back_button())
    else:
        await message.reply("🚫 You need to start the bot first with /start.", reply_markup=get_back_button())

# Get ID command handler
@app.on_message(filters.command("getid"))
async def get_id_command(client: Client, message: Message):
    chat_id = str(message.chat.id)
    data = load_data()
    secret = data.get(chat_id, {}).get('webhook_secret', 'Not set')
    await message.reply(f"Your Telegram chat ID:\n{chat_id}\n\nYour webhook secret:\n{secret}", reply_markup=get_back_button())

# Webhook secret command handler
@app.on_message(filters.command("webhooksecret"))
async def webhook_secret_command(client: Client, message: Message):
    chat_id = str(message.chat.id)
    data = load_data()

    if chat_id in data:
        secret = data[chat_id]['webhook_secret']
        await message.reply(f"🔑 Your Telegram chat ID:\n{chat_id}\n\n🔐 Your webhook secret:\n{secret}\n\nUse /regensecret to regenerate.", reply_markup=get_back_button())
    else:
        await message.reply("🚫 You need to start the bot first with /start.", reply_markup=get_back_button())

# Unsubscribe command handler
@app.on_message(filters.command("unsubscribe"))
async def unsubscribe_command(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in subscribed_users:
        subscribed_users.remove(user_id)
        await message.reply("You have been unsubscribed from weekly reports.", reply_markup=get_back_button())
    else:
        await message.reply("You are not subscribed to any reports.", reply_markup=get_back_button())

# Callback query handler
@app.on_callback_query()
async def handle_callback_query(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id
    chat_id = str(callback_query.from_user.id)
    users = load_data()

    if data == "back_to_menu":
        # Reset user state when going back to menu
        user_states[chat_id] = None
        await callback_query.message.edit(WELCOME_MESSAGE, reply_markup=get_main_menu())
        return

    if data == "analyze_data":
        message = """
📈 Analyze Your Data (CSV)

Upload a CSV file with your robot, factory, or sensor data.
I'll detect anomalies and suggest optimizations using quantum-inspired AI!
Example: timestamp,accel_x,accel_y,gyro,temperature

After upload, you'll get a detailed summary.
        """
        user_states[chat_id] = "analyze_data"  # Set state to expect CSV
        await callback_query.message.edit(message, reply_markup=get_back_button())

    elif data == "optimize_tasks":
        message = """
🗺️ Pathfinding/Task Optimization

Upload a CSV with a grid map (0=open, 1=wall) or task allocation table.
I'll use quantum-inspired Grover search to suggest an efficient path or assignment!
Send your file now.
        """
        user_states[chat_id] = "optimize_tasks"  # Set state to expect CSV
        await callback_query.message.edit(message, reply_markup=get_back_button())

    elif data == "ai_qa":
        message = """
💬 Ask Anything about Quantum-Inspired AI or Robotics!

Examples:
- How does quantum-inspired RL help robots?
- Can I optimize my warehouse robots?
- Show me code with PennyLane/Qiskit!

Type your question below:
        """
        user_states[chat_id] = "ai_qa"  # Set state to expect AI question
        await callback_query.message.edit(message, reply_markup=get_back_button())

    elif data == "subscribe_reports":
        subscribed_users.add(user_id)
        message = "You have successfully subscribed to weekly reports!"
        await callback_query.message.edit(message, reply_markup=get_back_button())

    elif data == "about_quantum_ai":
        message = """
💡 About Quantum-Inspired AI

- Entangled state evaluation
- Probabilistic feedback loops
- Quantum-style pathfinding (Grover search)

Frameworks: TensorFlow Quantum, PennyLane, Qiskit
For: robotics, automation, optimization, anomaly detection, etc.
        """
        await callback_query.message.edit(message, reply_markup=get_back_button())

    elif data == "get_chat_id":
        secret = users.get(chat_id, {}).get('webhook_secret', 'Not set')
        message = f"""
🔑 Your Telegram chat ID:
{chat_id}

🔐 Your personal webhook secret:
{secret}

To regenerate your secret, use /regensecret
        """
        await callback_query.message.edit(message, reply_markup=get_back_button())

    await callback_query.answer()

# Handler for incoming document (CSV files)
@app.on_message(filters.document & filters.private)
async def handle_document(client, message):
    chat_id = str(message.chat.id)
    state = user_states.get(chat_id)

    if state not in ["analyze_data", "optimize_tasks"]:
        await message.reply("Please select an option first (e.g., Analyze Data or Pathfinding) before uploading a CSV.", reply_markup=get_main_menu())
        return

    if message.document.mime_type != "text/csv":
        await message.reply("Please upload a valid CSV file.", reply_markup=get_back_button())
        return

    # Download the CSV file
    file_path = await message.download()
    try:
        # Read CSV content
        with open(file_path, 'r') as f:
            csv_content = f.read()

        # Prepare query based on state
        if state == "analyze_data":
            query = f"Analyze this CSV data for anomalies and optimizations:\n{csv_content}"
        elif state == "optimize_tasks":
            query = f"Optimize this CSV grid map or task list using quantum-inspired algorithms:\n{csv_content}"

        # Make API request
        reply = await make_api_request(query)

        # Reply with API response
        await message.reply(reply, reply_markup=get_main_menu())
    except Exception as e:
        await message.reply(f"Error processing CSV: {e}", reply_markup=get_main_menu())
    finally:
        # Clean up downloaded file
        if os.path.exists(file_path):
            os.remove(file_path)

    # Reset user state
    user_states[chat_id] = None

# Handler for incoming text messages
@app.on_message(filters.text & filters.private & ~filters.command(["start", "unsubscribe", "getid", "webhooksecret", "regensecret"]))
async def handle_message(client, message):
    chat_id = str(message.chat.id)
    state = user_states.get(chat_id)

    if state == "ai_qa":
        # Remove keywords "quantum" and "AI" (case-insensitive)
        query = message.text
        cleaned_query = re.sub(r'\bquantum\b|\bAI\b', '', query, flags=re.IGNORECASE).strip()

        # Make API request
        response = await make_api_request(cleaned_query or query)

        # Reply with API response
        await message.reply(response, reply_markup=get_main_menu())
    else:
        # Default behavior: reply with welcome message and main menu
        await message.reply(WELCOME_MESSAGE, reply_markup=get_main_menu())

# Main function to run bot
async def main():
    # Start Pyrogram client
    await app.start()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(app.stop())
        loop.close()
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}")
