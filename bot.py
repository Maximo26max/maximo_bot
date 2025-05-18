import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart

import os

API_TOKEN = "8179276423:AAHCWemkXe4taseLPaaoD2b6iafjKbxlPaw"
CHANNEL_ID = -1001954952198
ADMIN_ID = 1388312519
USERS_FILE = "users.txt"

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Старт
@dp.message(CommandStart())
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📲 Перейти на канал", url="https://t.me/+Ix3uck7QcoUzZTUy")],
        [InlineKeyboardButton(text="✅ Я підписався(-лася)", callback_data="check_sub")]
    ])
    await message.answer(
        f"Привіт, {message.from_user.first_name}!\n\n"
        f"Щоб отримати чек-лист, спершу підпишись на канал, а потім натисни кнопку нижче.",
        reply_markup=keyboard
    )

# Перевірка підписки
@dp.callback_query(lambda c: c.data == "check_sub")
async def check_subscription(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            # Запис користувача
            if not os.path.exists(USERS_FILE):
                with open(USERS_FILE, "w") as f: pass
            with open(USERS_FILE, "r") as f:
                users = f.read().splitlines()
            if str(user_id) not in users:
                with open(USERS_FILE, "a") as f:
                    f.write(str(user_id) + "\n")

            await callback_query.message.answer("Дякую за підписку! Ось твій чек-лист:")
            file = FSInputFile("checklist200.pdf")
            await bot.send_document(chat_id=user_id, document=file)
        else:
            await callback_query.message.answer("Здається, ти ще не підписаний(на). Спробуй ще раз.")
    except Exception as e:
        await callback_query.message.answer("Помилка перевірки.")
        print("Error:", e)

# Розсилка
@dp.message()
async def broadcast(message: types.Message):
    if message.from_user.id == ADMIN_ID and message.text.startswith("розсилка:"):
        text = message.text.replace("розсилка:", "").strip()
        if not text:
            await message.answer("Введи текст після 'розсилка:'.")
            return
        if not os.path.exists(USERS_FILE):
            await message.answer("Немає збережених користувачів.")
            return
        with open(USERS_FILE, "r") as f:
            users = f.read().splitlines()
        count = 0
        for user_id in users:
            try:
                await bot.send_message(chat_id=int(user_id), text=text)
                count += 1
            except:
                pass
        await message.answer(f"Розсилка завершена. Успішно надіслано: {count} користувачам.")
    elif message.from_user.id == ADMIN_ID and message.text.lower() == "статс":
        if not os.path.exists(USERS_FILE):
            await message.answer("Ще немає жодного користувача.")
        else:
            with open(USERS_FILE, "r") as f:
                users = f.read().splitlines()
            await message.answer(f"У боті — {len(users)} унікальних користувачів.")
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
