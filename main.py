import os, re, aiohttp, asyncio
from pyrogram import Client, filters, idle

# Telegram Bot credentials (replace with your own)
API_ID = "28362125"  # Get from my.telegram.org
API_HASH = "c750e5872a2af51801d9b449983f4c84"  # Get from my.telegram.org
BOT_TOKEN = "7038637559:AAFmvn2kmNuN2MukROcmc12B2jBgU8WuJGU"  # Get from @BotFather

# RapidAPI credentials
RAPID_API_KEY = "661048094dmshd422f34bffd5dc0p1d4d56jsn3bbc61e1a120"
RAPID_API_HOST = "okai.p.rapidapi.com"
RAPID_API_BASE_URL = "https://okai.p.rapidapi.com/v1/chat/completions"

# Initialize Pyrogram Client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Helper function to make RapidAPI request
async def make_rapid_api_request(number):
    url = f"{RAPID_API_BASE_URL}/{number}/math"
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    # Numbers API returns plain text for this endpoint
                    return await response.text()
                else:
                    return {"error": f"API request failed with status {response.status}"}
        except Exception as e:
            return {"error": f"Exception occurred: {str(e)}"}

# Start command handler
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "Hello! I'm a Telegram bot integrated with RapidAPI.\n"
        "Send me a number, and I'll fetch a math fact about it!\n"
        "Use /help to see available commands."
    )

# Help command handler
@app.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply_text(
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "\nJust send a number (e.g., 42), and I'll get a math fact from the Numbers API!"
    )

# Text message handler to process numbers
@app.on_message(filters.text)
async def text_handler(client, message):
    # Extract the first number from the message using regex
    text = message.text.strip()
    match = re.search(r'\d+', text)
    
    if not match:
        await message.reply_text("Please send a number (e.g., 42) to get a math fact!")
        return
    
    number = match.group(0)
    await message.reply_text(f"Fetching math fact for {number}, please wait...")
    
    result = await make_rapid_api_request(number)
    
    if isinstance(result, dict) and "error" in result:
        await message.reply_text(f"Error: {result['error']}")
    else:
        await message.reply_text(f"Math Fact for {number}:\n{result}")

# Main function to run the bot
async def main():
    await app.start()
    print("Bot is running...")
    await app.idle()

if __name__ == "__main__":
    asyncio.run(main())
