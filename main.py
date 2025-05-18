from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pyrogram.enums import ChatAction
import aiohttp
import json
import asyncio
import logging

# Set up logging for debugging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Telegram Bot Configuration
app = Client(
    "QuantumRoboticsBot",
    api_id="28362125",
    api_hash="c750e5872a2af51801d9b449983f4c84",
    bot_token="7038637559:AAHMjoy7ka3cKMnDkIS_N5-lylbuZB9TZww"
)

# RapidAPI Configuration
RAPIDAPI_HOST = "okai.p.rapidapi.com"
RAPIDAPI_KEY = "661048094dmshd422f34bffd5dc0p1d4d56jsn3bbc61e1a120"
RAPIDAPI_ENDPOINT = "/v1/chat/completions"

# Welcome photo URL (publicly available quantum robotics image)
WELCOME_PHOTO_URL = "https://files.catbox.moe/u0ujif.jpg"

async def send_typing_action(chat_id):
    """Send typing action to indicate the bot is processing."""
    try:
        await app.send_chat_action(chat_id, ChatAction.TYPING)
        await asyncio.sleep(1)  # Simulate processing time
    except Exception as e:
        logger.error(f"Error sending typing action: {e}")

async def query_rapidapi(message: str) -> str:
    """Query the RapidAPI for a response to the user's message."""
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
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
            }
            headers = {
                'x-rapidapi-key': RAPIDAPI_KEY,
                'x-rapidapi-host': RAPIDAPI_HOST,
                'Content-Type': "application/json"
            }
            async with session.post(
                f"https://{RAPIDAPI_HOST}{RAPIDAPI_ENDPOINT}",
                json=payload,
                headers=headers
            ) as response:
                if response.status != 200:
                    logger.error(f"RapidAPI returned status {response.status}")
                    return "Sorry, I couldn't process your request. Please try again."
                data = await response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                logger.error("No choices found in RapidAPI response")
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
    response = await query_rapidapi(user_message)
    try:
        await message.reply_text(response)
    except Exception as e:
        logger.error(f"Error replying to message: {e}")
        await message.reply_text("Sorry, I couldn't send a response. Please try again.")

# Error Handler
@app.on_message(filters.all)
async def error_handler(client: Client, message: Message):
    """Catch any unhandled messages."""
    try:
        await message.reply_text("Sorry, I didn't understand that. Use /help for guidance.")
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

# Start the Bot
if __name__ == "__main__":
    logger.info("Starting Quantum Robotics Bot...")
    app.run()  # Use Pyrogram's built-in run method
