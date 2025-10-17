import asyncio
from concurrent.futures import ThreadPoolExecutor
from pyrogram import Client, filters

# Replace these with your actual API ID and API Hash from my.telegram.org
API_ID = 25364356  # Your API ID (integer)
API_HASH = "ae13c2eb22d8157151ef505a82bdb840"  # Your API Hash (string)


# Define the message processing function
# This is a synchronous function; it can be expanded later.
# For demonstration, it just echoes the message with the username.
def proceed_message(message_text, username):
    # Simulate a potentially long-running operation (remove or adjust as needed)
    import time
    with open('logs.txt', 'a', encoding='utf-8') as log_file:
        log_file.write(f"{username}: {message_text}\n")
    time.sleep(5)  # Simulate delay
    return f"Work in progress\nРазработка в процессе\n\n**Теория Мертвого Интернета**"


# Create the Pyrogram Client for a user account (not a bot)
app = Client(
    "my_account",  # Session name
    api_id=API_ID,
    api_hash=API_HASH,
    workers=10  # Increase workers for better parallelism if needed
)

# Set up a thread pool executor for running synchronous, potentially blocking functions
executor = ThreadPoolExecutor(max_workers=10)  # Adjust max_workers based on expected load


@app.on_message(filters.private)  # Handle private text messages
async def handle_message(client, message):
    username = message.from_user.username or message.from_user.first_name  # Fallback to first name if no username
    text = message.text

    # Run the proceed_message in a separate thread to avoid blocking the asyncio loop
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(executor, proceed_message, text, username)

    # Send the response back to the user
    await message.reply_text(response)


# Run the client
print("Starting the Telegram client...")
app.run()