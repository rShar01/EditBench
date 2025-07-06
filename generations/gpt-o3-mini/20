import asyncio
from aiogram import Bot, Dispatcher, executor, types
import time

token = "<MASKED>"
bot = Bot(token=token)
dp = Dispatcher(bot)
id = 821885486
time_time = 5

b = bool(True)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup = types.InlineKeyboardMarkup(inline_keuboard = [
        [types.InlineKeyboardButton(text="Да", callback_data="stop"),
        types.InlineKeyboardButton(text="Нет", callback_data="continue")]
        ])
    await bot.send_message(chat_id=id, text="Ты робот?", reply_markup=markup)

@dp.callback_query_handler(text="stop")
async def stop(call: types.CallbackQuery):
    global b
    # b = False
    # await bot.send_message(chat_id=call.message.chat.id, text="<profane>")
    await bot.send_message(chat_id=call.message.chat.id, text="<profane>!")

@dp.callback_query_handler(text="continue")
async def stop(call: types.CallbackQuery):
    await bot.send_message(chat_id=call.message.chat.id, text="<profane>")

@dp.message_handler(content_types=['text'])
async def handle_all_messages(message: types.Message):
    with open(r"D:\Python files\<profane>", "rb") as vid:
        await bot.send_video(chat_id=id, video=vid, caption="<profane>")

async def send_periodic_messages():
    while b:
        await bot.send_message(chat_id=id, text="<profane>")
        with open(r"D:\Python files\!MoexApiBot\Shocked13.mp4", "rb") as vid:
            await bot.send_video(chat_id=id, video=vid, caption="Ты проиграл")
        await asyncio.sleep(time_time)

async def on_startup(dp):
    print('Бот запущен!')
    asyncio.create_task(send_periodic_messages())

async def main():
    await dp.start_polling(skip_updates=True, on_startup=on_startup)

if __name__ == '__main__':
    asyncio.run(main())
