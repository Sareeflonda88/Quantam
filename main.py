from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import http.client
import json
import time
import secrets
import asyncio
import logging

# Pyrogram bot configuration
app = Client(
    "OkaiBot",
    api_id=28362125,
    api_hash="c750e5872a2af51801d9b449983f4c84",
    bot_token="7038637559:AAFmvn2kmNuN2MukROcmc12B2jBgU8WuJGU"
)

# File to store user chat IDs and secrets
DATA_FILE = 'users.json'

# Simulated subscription storage (in-memory for simplicity)
subscribed_users = set()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Function to check if the message is related to quantum robotics
def is_quantum_robotics_question(message):
    keywords = ["quantum", "robotics", "quantum robotics", "qubit", "quantum computing", 
                "quantum algorithm", "robotic control", "quantum sensor", "quantum mechanics"]
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in keywords)

# Function to call OKAI API
def call_okai_api(user_message):
    conn = http.client.HTTPSConnection("okai.p.rapidapi.com")
    payload = json.dumps({
        "messages": [{"role": "user", "content": user_message}]
    })
    headers = {
        'x-rapidapi-key': "661048094dmshd422f34bffd5dc0p1d4d56jsn3bbc61e1a120",
        'x-rapidapi-host': "okai.p.rapidapi.com",
        'Content-Type': "application/json"
    }
    try:
        time.sleep(1)  # Avoid rate limiting
        conn.request("POST", "/v1/chat/completions", payload, headers)
        res = conn.getresponse()
        data = res.read()
        response = json.loads(data.decode("utf-8"))
        logger.info(f"Raw API response: {response}")
        if 'response' in response:
            return response['response']
        else:
            return f"Error: Unexpected API response structure. Raw response: {response}"
    except Exception as e:
        return f"Error: API call failed. Details: {str(e)}"
    finally:
        conn.close()

# Back to Menu button
def get_back_button():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]]
    )

# Main menu keyboard
def get_main_menu():
    return InlineKeyboardMarkup(
        [
            [],  # Empty first row
            [InlineKeyboardButton("Analyze Data 📈", callback_data="analyze_data")],
            [InlineKeyboardButton("Optimize Tasks 🗺️", callback_data="optimize_tasks")],
            [InlineKeyboardButton("AI Q&A 💬", callback_data="ai_qa")],
            [InlineKeyboardButton("Subscribe Reports 📬", callback_data="subscribe_reports")],
            [InlineKeyboardButton("About Quantum-Inspired AI 💡", callback_data="about_quantum_ai")],
            [InlineKeyboardButton("Get Chat ID & Secret 🔑", callback_data="get_chat_id")]
        ]
    )

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
        await callback_query.message.edit(message, reply_markup=get_back_button())
    
    elif data == "optimize_tasks":
        message = """
🗺️ Pathfinding/Task Optimization

Upload a CSV with a grid map (0=open, 1=wall) or task allocation table.
I'll use quantum-inspired Grover search to suggest an efficient path or assignment!
Send your file now.
        """
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
        await callback_query.message.edit(message, reply_markup=get_back_button())
    
    elif data == "subscribe_reports":
        subscribed_users.add(user_id)
        message = "Subscribed successfully! You'll receive weekly summaries and tips.\nUse /unsubscribe to stop reports anytime."
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

# Handler for incoming messages
@app.on_message(filters.text & filters.private & ~filters.command(["start", "unsubscribe", "getid", "webhooksecret", "regensecret"]))
async def handle_message(client, message):
    user_message = message.text
    try:
        # Check if the message is related to quantum robotics
        if not is_quantum_robotics_question(user_message):
            await message.reply("Sorry, I only answer questions related to quantum robotics. Please ask a question about quantum robotics!")
            return
        
        # Call OKAI API with user's message
        response = call_okai_api(user_message)
        # Reply with the API response
        await message.reply(response)
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")

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
