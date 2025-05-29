import os
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import load_dotenv
from database import add_note, get_notes, delete_note

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

# Инициализация бота
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ================= Обработчики команд =================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "📝 Бот для заметок!\n\n"
        "Доступные команды:\n"
        "/add_note - добавить заметку\n"
        "/notes - посмотреть заметки\n"
        "/delete_note - удалить заметку\n\n"
        "Просто напишите текст, чтобы сохранить заметку!"
    )

@dp.message(Command("add_note"))
async def cmd_add_note(message: types.Message):
    await message.answer("Теперь просто напишите текст заметки, и я её сохраню!")

@dp.message(Command("notes"))
async def cmd_notes(message: types.Message):
    notes = get_notes(message.from_user.id)
    if not notes:
        await message.answer("Заметок нет.")
        return
    
    response = "📋 Ваши заметки:\n\n"
    for note_id, note_text in notes:
        response += f"{note_id}. {note_text}\n"
    await message.answer(response)

@dp.message(Command("delete_note"))
async def cmd_delete_note(message: types.Message):
    notes = get_notes(message.from_user.id)
    if not notes:
        await message.answer("Нет заметок для удаления.")
        return
    
    builder = InlineKeyboardBuilder()
    for note_id, note_text in notes:
        builder.button(
            text=f"❌ {note_id}. {note_text[:20]}...",
            callback_data=f"delete_{note_id}"
        )
    builder.adjust(1)
    await message.answer("Выберите заметку для удаления:", reply_markup=builder.as_markup())

# ========= Обработчик текстовых сообщений =========

@dp.message(F.text & ~F.command)
async def handle_text_message(message: types.Message):
    try:
        add_note(message.from_user.id, message.text)
        await message.answer("✅ Заметка сохранена!")
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")
        await message.answer("❌ Не удалось сохранить заметку")

# ========= Обработчик кнопок удаления =========

@dp.callback_query(F.data.startswith("delete_"))
async def delete_note_callback(callback: types.CallbackQuery):
    note_id = int(callback.data.split("_")[1])
    delete_note(note_id)
    await callback.message.answer("🗑 Заметка удалена!")
    await callback.answer()

# ========= Основная функция =========

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

# ========= Проверка запуска =========

async def check_bot_running():
    try:
        session = AiohttpSession()
        await session.close()
        return False
    except Exception as e:
        logger.error(f"Ошибка проверки: {e}")
        return True

# ========= Точка входа =========

if __name__ == '__main__':
    try:
        if asyncio.run(check_bot_running()):
            logger.error("Ошибка: Бот уже запущен в другом процессе!")
            sys.exit(1)
        
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)
