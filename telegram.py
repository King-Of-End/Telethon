import asyncio
from concurrent.futures import ThreadPoolExecutor
from pyrogram import Client, filters

from Graph import app
from states import MessageState

API_ID = 25364356
API_HASH = "ae13c2eb22d8157151ef505a82bdb840"


def proceed_message(message_text, username):
    print(f'Обработка сообщения - {username}: {message_text}')
    with open('logs.txt', 'a', encoding='utf-8') as log_file:
        log_file.write(f"{username}: {message_text}\n")
    msg = MessageState(
        user_message=message_text,
        username=username,
    )
    answer = asyncio.run(app.ainvoke(msg))
    return answer['message']


telegram_app = Client(
    "my_account",
    api_id=API_ID,
    api_hash=API_HASH,
    workers=10,

)

executor = ThreadPoolExecutor(max_workers=10)


@telegram_app.on_message(filters.private)
async def handle_message(client, message):
    username = message.from_user.username or message.from_user.first_name
    text = message.text
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(executor, proceed_message, text, username)

    await message.reply_text(response)

if __name__ == '__main__':
    telegram_app.run()