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

# Simulated subscription storage (in-memory for simplicity)
subscribed_users = set()

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

# Back to Menu button
def get_back_button():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]]
    )

# Main menu keyboard
def get_main_menu():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Analyze Data", callback_data="analyze_data"),
                InlineKeyboardButton("Optimize Tasks", callback_data="optimize_tasks")
            ],
            [
                InlineKeyboardButton("Robot Integration", callback_data="robot_integration"),
                InlineKeyboardButton("AI Q&A", callback_data="ai_qa")
            ],
            [
                InlineKeyboardButton("Subscribe Reports", callback_data="subscribe_reports"),
                InlineKeyboardButton("Get Chat ID", callback_data="get_chat_id")
            ],
            [
                InlineKeyboardButton("Webhook Secret", callback_data="webhook_secret")
            ]
        ]
    )

# Start command handler
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply(WELCOME_MESSAGE, reply_markup=get_main_menu())

# Unsubscribe command handler
@app.on_message(filters.command("unsubscribe"))
async def unsubscribe_command(client, message):
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
    
    elif data == "robot_integration":
        message = """
🔗 Robot Integration

Integrate your robot with our secure webhook for real-time analysis.
Use /getid to get your chat ID and /webhooksecret for your webhook secret.
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
    
    elif data == "get_chat_id":
        message = """
🔑 Your Telegram chat ID:
7204861404

🔐 Your personal webhook secret:
a322067e6fc98e49b68eeec945458d7e

Your robot/service must send both these values for secure webhook data delivery.

To regenerate your secret, use /regensecret
        """
        await callback_query.message.edit(message, reply_markup=get_back_button())
    
    elif data == "webhook_secret":
        message = """
🔑 Your Telegram chat ID:
7204861404

🔐 Your personal webhook secret:
a322067e6fc98e49b68eeec945458d7e

Your robot/service must send both these values for secure webhook data delivery.

To regenerate your secret, use /regensecret
        """
        await callback_query.message.edit(message, reply_markup=get_back_button())

    await callback_query.answer()

# Handler for incoming messages
@app.on_message(filters.text & filters.private & ~filters.command(["start", "unsubscribe"]))
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
