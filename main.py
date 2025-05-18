from pyrogram import Client, filters
import http.client
import json
import time

# Pyrogram bot configuration
app = Client(
    "OkaiBot",
    api_id=28362125,  # Replace with your API ID
    api_hash="c750e5872a2af51801d9b449983f4c84",  # Replace with your API Hash
    bot_token="7038637559:AAFmvn2kmNuN2MukROcmc12B2jBgU8WuJGU"  # Replace with your Bot Token
)

# Function to call OKAI API
def call_okai_api(user_message):
    conn = http.client.HTTPSConnection(" okr.p.rapidapi.com")
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
        if 'choices' in response and len(response['choices']) > 0:
            return response['choices'][0]['message']['content']
        else:
            return f"Error: Unexpected API response structure. Raw response: {response}"
    except Exception as e:
        return f"Error: API call failed. Details: {str(e)}"
    finally:
        conn.close()

# Handler for incoming messages
@app.on_message(filters.text & filters.private)
async def handle_message(client, message):
    user_message = message.text
    try:
        # Call OKAI API with user's message
        response = call_okai_api(user_message)
        # Reply with the API response
        await message.reply(response)
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")

# Start the bot
print("Bot is running...")
app.run()
