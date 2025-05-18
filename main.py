from pyrogram import Client, filters
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

# Handler for incoming messages
@app.on_message(filters.text & filters.private)
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
