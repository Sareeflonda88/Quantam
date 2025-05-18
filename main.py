from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pyrogram.enums import ChatAction
import aiohttp
import json
import asyncio
import logging
import os
from dotenv import load_dotenv

# Load environment variables (optional, for secure storage of sensitive data)
load_dotenv()

# Set up logging for debugging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Telegram Bot Configuration
app = Client(
    name="QuantumRoboticsBot",
    api_id=os.getenv("API_ID", "28362125"),  # Fallback to hardcoded value if not in .env
    api_hash=os.getenv("API_HASH", "c750e5872a2af51801d9b449983f4c84"),
    bot_token=os.getenv("BOT_TOKEN", "7038637559:AAFmvn2kmNuN2MukROcmc12B2jBgU8WuJGU")
)

# RapidAPI Configuration
RAPIDAPI_HOST = "okai.p.rapidapi.com"
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "661048094dmshd422f34bffd5dc0p1d4d56jsn3bbc61e1a120")
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
    """Query the RapidAPI for a response to the user's message with retry logic."""
    retries = 3
    for attempt in range(retries):
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
                    logger.info(f"RapidAPI response status: {response.status}")
                    response_text = await response.text()
                    logger.info(f"RapidAPI response body: {response_text}")
                    if response.status == 429:  # Rate limit
                        logger.warning(f"Rate limit hit, retrying in {2 ** attempt} seconds...")
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    if response.status != 200:
                        logger.error(f"RapidAPI returned status {response.status}: {response_text}")
                        return "Sorry, I couldn't process your request. Please try again."
                    try:
                        data = json.loads(response_text)  # Explicitly parse JSON
                        if "choices" in data and len(data["choices"]) > 0:
                            content = data["choices"][0]["message"]["content"]
                            if content:
                                return content
                            logger.error("Empty content in RapidAPI response")
                            return "Sorry, I couldn't process your request. Please try again."
                        logger.error(f"No choices found in RapidAPI response: {data}")
                        return "Sorry, I couldn't process your request. Please try again."
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse RapidAPI response as JSON: {e}")
                        return "Sorry, I couldn't process your request due to a response error. Please try again."
        except Exception as e:
            logger.error(f"Error querying RapidAPI (attempt {attempt + 1}/{retries}): {e}")
            if attempt == retries - 1:
                return "An error occurred while processing your request. Please try again later."
    return "Sorry, I couldn't process your request due to rate limits or repeated errors. Please try again later."

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
    app.run()
