from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)

scheduler = AsyncIOScheduler()

async def send_reminder(chat_id: int, text: str):
    await bot.send_message(chat_id, f"⏰ Напоминание: {text}")

def add_reminder(chat_id: int, text: str, time_in_seconds: int):
    scheduler.add_job(
        send_reminder,
        'interval',
        seconds=time_in_seconds,
        args=(chat_id, text)
    )

# Запуск планировщика
scheduler.start()
