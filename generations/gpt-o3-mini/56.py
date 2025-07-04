# Unchanged code above

# --- Begin Highlighted Section: Telegram Bot with aiogram 3 ---
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

API_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hi! I am your aiogram v3 bot. Send me any message and I'll echo it back!")

@dp.message()
async def echo(message: types.Message):
    await message.answer(message.text)

async def main():
    try:
        print("Bot is starting...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
# --- End Highlighted Section ---

# Unchanged code below
