from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import json, secrets, asyncio, logging, re, requests, os, csv, io

# Pyrogram bot configuration
app = Client(
    name="RoboFluxAI",
    api_id=28362125,
    api_hash="c750e5872a2af51801d9b449983f4c84",
    bot_token="7705137466:AAEZbzei-auJWxOj165Gqwc2Kv9ckuP0WCg"
)

# File to store user chat IDs and secrets
DATA_FILE = 'users.json'

# Simulated subscription storage
subscribed_users = set()

# Track user states
user_states = {}

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API configuration
API_KEY = "661048094dmshd422f34bffd5dc0p1d4d56jsn3bbc61e1a120"
BASE_URL = "https://okai.p.rapidapi.com/v1/chat"
AI_MODEL = "quantum"

# Maximum file size (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

# Load and save user data
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {}
    except json.JSONDecodeError:
        logger.error("Corrupted users.json file, starting with empty data")
        return {}
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return {}

def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving data: {e}")

# Validate CSV content
def validate_csv(file_path, state):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read first 1MB to avoid memory issues
            content = f.read(1024 * 1024)
            f.seek(0)
            dialect = csv.Sniffer().sniff(content[:1024])
            reader = csv.reader(io.StringIO(content), dialect)
            headers = next(reader, None)
            if not headers or len(headers) < 1:
                return False, "CSV is empty or missing headers."
            
            # Check for expected columns based on state
            if state == "analyze_data":
                expected = {'timestamp', 'accel_x', 'accel_y', 'gyro', 'temperature'}
                if not any(h.lower() in expected for h in headers):
                    return False, "CSV lacks expected columns (e.g., timestamp, accel_x)."
            elif state == "optimize_tasks":
                # For grid maps, check for numeric values
                row = next(reader, None)
                if row and not all(re.match(r'^-?\d*\.?\d*$', cell.strip()) for cell in row if cell.strip()):
                    return False, "Grid map CSV contains non-numeric values."
            
            # Check row consistency
            row_count = sum(1 for row in reader) + 1
            logger.info(f"CSV validated: {row_count} rows, headers: {headers}")
            return True, f"CSV looks good! Found {row_count} rows with headers: {headers[:3]}..."
    except csv.Error:
        return False, "Invalid CSV format (e.g., incorrect delimiters or quotes)."
    except UnicodeDecodeError:
        return False, "CSV file encoding is not UTF-8. Please use UTF-8 encoding."
    except Exception as e:
        return False, f"Error reading CSV: {str(e)}"

# Welcome message
WELCOME_MESSAGE = """
Welcome to RoboFlux Quantum-Inspired AI Bot!

This assistant helps you make the most of quantum-inspired AI in robotics, automation, and data science.
Here’s what you can do:

🔹 Analyze your CSV data — Upload your CSV logs for instant anomaly detection and optimization.
🔹 Data Optimizer — Upload grid maps or task lists to get quantum-accelerated solutions.
🔹 AI Queries — Ask anything about quantum-inspired AI, robotics, or implementation advice (powered by RoboFlux AI).
🔹 System Insights — Subscribe for weekly summaries and actionable tips.

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

# Retry button for failed uploads
def get_retry_button():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔄 Retry Upload", callback_data="retry_upload")],
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]
        ]
    )

# Main menu keyboard
def get_main_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("👨‍🔧 Robot Dashboard (CSV)", callback_data="analyze_data")],
            [InlineKeyboardButton("📊 Data Optimizer", callback_data="optimize_tasks")],
            [InlineKeyboardButton("🗺️ Path Planner", callback_data="ai_qa")],
            [InlineKeyboardButton("🎛️ System Insights", callback_data="subscribe_reports")],
            [InlineKeyboardButton("📨 AI Queries", callback_data="about_quantum_ai")],
            [InlineKeyboardButton("⚙️ Account Settings", callback_data="get_chat_id")]
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
        response = requests.post(BASE_URL, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "Sorry, I couldn't fetch the data.")
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return f"Failed to fetch data from the API: {str(e)}"
    except ValueError:
        logger.error("Invalid JSON response from API")
        return "Invalid response from the API. Please try again later."
    except Exception as e:
        logger.error(f"Unexpected error in API request: {e}")
        return f"An error occurred: {e}"

# Start command handler
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    chat_id = str(message.chat.id)
    data = load_data()

    if chat_id not in data:
        secret = secrets.token_hex(16)
        data[chat_id] = {'webhook_secret': secret}
        save_data(data)
        message_text = f'✅ Welcome! Your webhook secret is:\n\n{secret}\n\nKeep it safe!\n\n{WELCOME_MESSAGE}'
    else:
        message_text = WELCOME_MESSAGE

    user_states[chat_id] = None
    await message.reply(message_text, reply_markup=get_main_menu())

# Regen secret command handler
@app.on_message(filters.command("regensecret"))
async def regen_secret_command(client: Client, message: Message):
    chat_id = str(message.chat.id)
    data = load_data()

    if chat_id in data:
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
    chat_id = message.chat.id
    if chat_id in subscribed_users:
        subscribed_users.remove(chat_id)
        await message.reply("You have been unsubscribed from weekly reports. 😢", reply_markup=get_back_button())
    else:
        await message.reply("You are not subscribed to any reports.", reply_markup=get_back_button())

# Callback query handler
@app.on_callback_query()
async def handle_callback_query(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id
    chat_id = str(user_id)
    users = load_data()

    if data == "back_to_menu":
        user_states[chat_id] = None
        await callback_query.message.edit(WELCOME_MESSAGE, reply_markup=get_main_menu())
        return

    if data == "retry_upload":
        state = user_states.get(chat_id, "analyze_data")  # Default to analyze_data if state lost
        if state == "analyze_data":
            message = """
👨‍🔧 Robot Dashboard (CSV)

Upload a CSV file with robot, factory, or sensor data.
**Expected format**: timestamp,accel_x,accel_y,gyro,temperature
**Example**:
```
timestamp,accel_x,accel_y,gyro,temperature
2023-10-01 10:00:00,1.2,-0.5,0.1,25.3
```

I'll detect anomalies and suggest optimizations using quantum-inspired AI!
            """
        elif state == "optimize_tasks":
            message = """
📊 Data Optimizer

Upload a CSV with a grid map (0=open, 1=wall) or task allocation table.
**Example grid map**:
```
0,0,1,0
0,1,0,0
1,0,0,0
```
I'll use quantum-inspired Grover search to suggest an efficient path or assignment!
            """
        await callback_query.message.edit(message, reply_markup=get_back_button())
        return

    if data == "analyze_data":
        message = """
👨‍🔧 Robot Dashboard (CSV)

Upload a CSV file with robot, factory, or sensor data.
**Expected format**: timestamp,accel_x,accel_y,gyro,temperature
**Example**:
```
timestamp,accel_x,accel_y,gyro,temperature
2023-10-01 10:00:00,1.2,-0.5,0.1,25.3
```

I'll detect anomalies and suggest optimizations using quantum-inspired AI!
        """
        user_states[chat_id] = "analyze_data"
        await callback_query.message.edit(message, reply_markup=get_back_button())

    elif data == "optimize_tasks":
        message = """
📊 Data Optimizer

Upload a CSV with a grid map (0=open, 1=wall) or task allocation table.
**Example grid map**:
```
0,0,1,0
0,1,0,0
1,0,0,0
```
I'll use quantum-inspired Grover search to suggest an efficient path or assignment!
        """
        user_states[chat_id] = "optimize_tasks"
        await callback_query.message.edit(message, reply_markup=get_back_button())

    elif data == "ai_qa":
        message = """
💬 Ask Anything about Quantum to RoboFluxAI AI or Robotics!

Examples:
- What are the potential benefits of quantum robotics?
- What are the challenges in developing quantum robotics?
- Show me code with PennyLane/Qiskit!

Type your question below:
        """
        user_states[chat_id] = "ai_qa"
        await callback_query.message.edit(message, reply_markup=get_back_button())

    elif data == "subscribe_reports":
        subscribed_users.add(user_id)
        message = "You have successfully subscribed to weekly reports! 🎉\nYou can unsubscribe anytime using /unsubscribe or the button below."
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("❌ Unsubscribe", callback_data="unsubscribe")],
                [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]
            ]
        )
        await callback_query.message.edit(message, reply_markup=reply_markup)

    elif data == "unsubscribe":
        if user_id in subscribed_users:
            subscribed_users.remove(user_id)
            message = "You have been unsubscribed from weekly reports. \nYou can resubscribe anytime from the main menu."
        else:
            message = "You are not subscribed to any reports."
        await callback_query.message.edit(message, reply_markup=get_back_button())

    elif data == "about_quantum_ai":
        message = """
📨 AI Queries

📩 Ask me anything about robotics AI, quantum algorithms, or PennyLane/Qiskit examples.

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

    # Check file extension and size
    if not message.document.file_name.lower().endswith('.csv'):
        await message.reply("Please upload a file with a .csv extension.", reply_markup=get_retry_button())
        return

    if message.document.file_size > MAX_FILE_SIZE:
        await message.reply(f"File is too large. Maximum size is {MAX_FILE_SIZE // 1024 // 1024}MB.", reply_markup=get_retry_button())
        return

    # Send processing message
    temp_message = await message.reply("⏳ Processing your CSV... (this may take a moment)")

    file_path = None
    try:
        # Download file with timeout
        file_path = await asyncio.wait_for(message.download(), timeout=30)

        # Validate CSV content
        is_valid, validation_message = validate_csv(file_path, state)
        if not is_valid:
            await temp_message.delete()
            await message.reply(f"🚫 {validation_message}\nPlease check the file and try again.", reply_markup=get_retry_button())
            return

        # Preview CSV
        await message.reply(f"✅ {validation_message}")

        # Read CSV content
        with open(file_path, 'r', encoding='utf-8') as f:
            csv_content = f.read()

        # Process based on state
        if state == "analyze_data":
            query = f"Analyze this CSV data for anomalies and optimizations:\n{csv_content}"
            response = await make_api_request(query)
            await temp_message.delete()
            await message.reply(f"👨‍🔧 Robot Dashboard:\n{response}", reply_markup=get_main_menu())
        elif state == "optimize_tasks":
            query = f"Optimize this CSV grid map or task list using quantum-inspired algorithms and provide the optimal path or task assignment:\n{csv_content}"
            response = await make_api_request(query)
            await temp_message.delete()
            await message.reply(f"📊 Data Optimizer Results:\n{response}", reply_markup=get_main_menu())

    except asyncio.TimeoutError:
        await temp_message.delete()
        await message.reply("⏰ Timeout while downloading file. Please try a smaller file.", reply_markup=get_retry_button())
    except Exception as e:
        logger.error(f"Error processing CSV for chat {chat_id}: {e}")
        await temp_message.delete()
        await message.reply(f"🚫 Error processing CSV: {str(e)}\nPlease try again or contact support.", reply_markup=get_retry_button())
    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Error deleting file {file_path}: {e}")

    user_states[chat_id] = None

# Handler for incoming text messages
@app.on_message(filters.text & filters.private & ~filters.command(["start", "unsubscribe", "getid", "webhooksecret", "regensecret"]))
async def handle_message(client, message):
    chat_id = str(message.chat.id)
    state = user_states.get(chat_id)

    if state == "ai_qa":
        temp_message = await message.reply("⏳ Asking AI...")
        await asyncio.sleep(0.5)
        await temp_message.delete()

        query = message.text
        cleaned_query = re.sub(r'\bquantum\b|\bAI\b', '', query, flags=re.IGNORECASE).strip()
        
        response = await make_api_request(cleaned_query or query)
        await message.reply(response, reply_markup=get_main_menu())
        user_states[chat_id] = None
    else:
        await message.reply("Use the menu or type /start.", reply_markup=get_main_menu())

# Main function to run bot
async def main():
    try:
        await app.start()
        logger.info("Bot started successfully")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(app.stop())
        logger.info("Bot stopped gracefully")
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
    finally:
        loop.close()
