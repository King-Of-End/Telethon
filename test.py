# userbot.py
# Python 3.11, pyrogram
import os
import re
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Конфигурация через переменные окружения:
# API_ID (int), API_HASH (str). SESSION - имя файла сессии или session string. Если SESSION не задано, будет "userbot".
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
SESSION = os.environ.get("SESSION", "userbot")

if API_ID == 0 or API_HASH == "":
    raise SystemExit("Нужно задать API_ID и API_HASH через переменные окружения")

app = Client(SESSION, api_id=API_ID, api_hash=API_HASH)

# Разрешаем числа с опциональными десятичными дробями: "5 Привет", "2.5 Тест"
INPUT_RE = re.compile(r'^\s*([0-9]+(?:\.[0-9]+)?)\s+(.+)$', re.DOTALL)

async def schedule_send(client: Client, chat_id: int, text: str, delay: float):
    try:
        await asyncio.sleep(delay)
        await client.send_message(chat_id, text)
    except Exception:
        logging.exception("Ошибка при отправке отложенного сообщения")

@app.on_message(filters.private | filters.group | filters.channel)
async def handler(client: Client, message: Message):
    raw = message.text or message.caption or ""
    if not raw:
        return  # ничего не парсим для пустых сообщений
    m = INPUT_RE.match(raw.strip())
    if not m:
        return  # формат не соответствует, игнорируем
    seconds_str, reply_text = m.group(1), m.group(2).strip()
    try:
        delay = float(seconds_str)
    except ValueError:
        return
    if delay < 0:
        return
    chat_id = message.chat.id
    # Создаём фоновую задачу — не блокирует обработку других сообщений
    asyncio.create_task(schedule_send(client, chat_id, reply_text, delay))
    logging.info("Запланировано сообщение в %s сек. в чат %s: %r", delay, chat_id, reply_text)

if __name__ == "__main__":
    app.run()
