from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import http.client
import json
import time

# Pyrogram bot configuration
app = Client(
    "OkaiBot",
    api_id=28362125,
    api_hash="c750e5872a2af51801d9b449983f4c84",
    bot_token="7038637559:AAFmvn2kmNuN2MukROcmc12B2jBgU8WuJGU"
)

# Welcome message
WELCOME_MESSAGE = """
Welcome to QuantroBotics Quantum-Inspired AI Bot!

This assistant helps you make the most of quantum-inspired AI in robotics, automation, and data science.
Here’s what you can do:

🔹 Analyze your data — Upload your CSV logs for instant anomaly detection and optimization.
🔹 Optimize paths/tasks — Upload grid maps or task lists to get quantum-accelerated solutions.
🔹 Integrate with your robot — Secure webhook for direct robot-to-bot analysis.
🔹 AI Q&A — Ask anything about quantum-inspired AI, robotics, or implementation advice (powered by AI).
🔹 Get scheduled reports — Subscribe for weekly summaries and actionable tips.

Start by selecting an option below or use the menu commands.

➕ Tips:
- Use /getid to find your chat ID (for API/robot integration)
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
        print("Raw API response:", response)  # Debug print
        if 'response' in response:
            return response['response']
        else:
            return f"Error: Unexpected API response structure. Raw response: {response}"
    except Exception as e:
        return f"Error: API call failed. Details: {str(e)}"
    finally:
        conn.close()

# Start command handler
@app.on_message(filters.command("start"))
async def start_command(client, message):
    # Define inline keyboard with 7 buttons
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Analyze Data", callback_data="analyze_data")],
            [    InlineKeyboardButton("Optimize Tasks", callback_data="optimize_tasks")
            ],
            [
                InlineKeyboardButton("Robot Integration", callback_data="robot_integration")],
            [   InlineKeyboardButton("AI Q&A", callback_data="ai_qa")
            ],
            [
                InlineKeyboardButton("Subscribe Reports", callback_data="subscribe_reports")],
            [    InlineKeyboardButton("Get Chat ID", callback_data="get_chat_id")
            ],
            [
                InlineKeyboardButton("Webhook Secret", callback_data="webhook_secret")
            ]
        ]
    )
    
    # Send welcome message with buttons
    await message.reply(WELCOME_MESSAGE, reply_markup=keyboard)

# Handler for incoming messages
@app.on_message(filters.text & filters.private & ~filters.command("start"))
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

# Start the bot
print("Bot is running...")
app.run()
