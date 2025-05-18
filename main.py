from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
import http.client
import json
import asyncio
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Configuration
# Replace 'YOUR_API_ID' and 'YOUR_API_HASH' with your Telegram API credentials
# Obtain these from https://my.telegram.org
# Replace 'YOUR_BOT_TOKEN' with your bot token from BotFather
app = Client(
    "QuantumRoboticsBot",
    api_id="28362125",
    api_hash="c750e5872a2af51801d9b449983f4c84",
    bot_token="7038637559:AAEP_KxPW5Te-7SO7DNGEUKN-aWRVbRzpaU"
)

# RapidAPI Configuration
RAPIDAPI_HOST = "okai.p.rapidapi.com"
RAPIDAPI_KEY = "661048094dmshd422f34bffd5dc0p1d4d56jsn3bbc61e1a120"
RAPIDAPI_ENDPOINT = "/v1/chat/completions"

# Welcome photo URL (publicly available quantum robotics image)
WELCOME_PHOTO_URL = "https://example.com/quantum_robotics_image.jpg"  # Replace with a real image URL

async def send_typing_action(chat_id):
    """Send typing action to indicate the bot is processing."""
    await app.send_chat_action(chat_id, ChatAction.TYPING)
    await asyncio.sleep(1)  # Simulate processing time

def query_rapidapi(message: str) -> str:
    """Query the RapidAPI for a response to the user's message."""
    try:
        conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
        payload = json.dumps({
            "messages": [
                {
                    "role": "system",
                    "content": "You are a quantum robotics expert. Provide accurate and concise information about quantum robotics."
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
        })
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': RAPIDAPI_HOST,
            'Content-Type': "application/json"
        }
        conn.request("POST", RAPIDAPI_ENDPOINT, payload, headers)
        res = conn.getresponse()
        data = res.read()
        response = json.loads(data.decode("utf-8"))
        conn.close()
        
        # Extract the assistant's response
        if "choices" in response and len(response["choices"]) > 0:
            return response["choices"][0]["message"]["content"]
        else:
            return "Sorry, I couldn't process your request. Please try again."
    except Exception as e:
        logger.error(f"Error querying RapidAPI: {e}")
        return "An error occurred while processing your request. Please try again later."

# Start Command Handler
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Handle the /start command with a welcome photo and message."""
    await send_typing_action(message.chat.id)
    
    welcome_message = (
        "🤖 Welcome to the Quantum Robotics Bot! 🤖\n\n"
        "I'm here to answer all your questions about quantum robotics. "
        "Ask me anything about quantum computing, robotics, or their exciting intersection!\n\n"
        "Use /help to see available commands."
    )
    
    try:
        await message.reply_photo(
            photo=WELCOME_PHOTO_URL,
            caption=welcome_message
        )
    except Exception as e:
        logger.error(f"Error sending welcome photo: {e}")
        await message.reply_text(welcome_message)

# Help Command Handler
@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    """Handle the /help command with usage instructions."""
    await send_typing_action(message.chat.id)
    
    help_message = (
        "📚 Quantum Robotics Bot Help 📚\n\n"
        "Here's how to use me:\n"
        "- /start: Start the bot and get a welcome message.\n"
        "- /help: Show this help message.\n"
        "- Send any text message to ask about quantum robotics!\n\n"
        "Example: 'What is quantum robotics?' or 'How do quantum computers enhance robotics?'"
    )
    
    await message.reply_text(help_message)

# Text Message Handler
@app.on_message(filters.text & ~filters.command(["start", "help"]))
async def handle_text(client: Client, message: Message):
    """Handle general text messages by querying the RapidAPI."""
    await send_typing_action(message.chat.id)
    
    user_message = message.text
    response = query_rapidapi(user_message)
    await message.reply_text(response)

# Error Handler
@app.on_message(filters.all)
async def error_handler(client: Client, message: Message):
    """Catch any unhandled errors."""
    try:
        await message.reply_text("Sorry, I didn't understand that. Use /help for guidance.")
    except Exception as e:
        logger.error(f"Error in message handler: {e}")

# Start the Bot
async def main():
    """Start the bot and keep it running."""
    try:
        await app.start()
        logger.info("Quantum Robotics Bot is running...")
        await app.idle()
    except Exception as e:
        logger.error(f"Error running bot: {e}")
    finally:
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
