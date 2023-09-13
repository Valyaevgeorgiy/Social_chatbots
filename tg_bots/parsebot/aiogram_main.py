import traceback
import time
import asyncio
from parser import get_sales
from aiogram.types import Message
from aiogram import Bot, Dispatcher, F

telegram_token = 'токен тг бота'

bot = Bot(telegram_token)
dp = Dispatcher()
is_monitoring = True


@dp.message(F.text == "/start")
async def handle_start(message: Message):
    await message.answer("Привет!\nЯ — бот для мониторинга списка цен на номера телефонов. Чем могу помочь?")


@dp.message(F.text == "/monitoring")
async def handle_monitoring(message: Message):
    global is_monitoring
    is_monitoring = False

    await message.answer("Отслеживание списка номеров успешно запущено!")
    await message.answer("Получаем первый результат...")

    try:
        is_monitoring = True

        phones_dict, top10_list = await get_sales()

        await message.answer(top10_list)

        while is_monitoring:

            time.sleep(15)
            new_phones_dict, top10_list = await get_sales()

            if (new_phones_dict != {}) and (list(phones_dict.keys()) != list(new_phones_dict.keys())) and (list(phones_dict.values()) != list(new_phones_dict.values())):
                phones_dict = new_phones_dict
                await message.answer("Есть изменения!")
                time.sleep(2)
                await message.answer(top10_list)
            elif (new_phones_dict == {}):
                await message.answer(top10_list)
                break
    except:
        await message.answer("Произошла ошибка! В скором времени бот снова заработает!\nКод ошибки:")
        await message.answer(str(traceback.format_exc()))


@dp.message(F.text == '/stop')
async def handle_stop(message: Message):
    global is_monitoring
    is_monitoring = False
    await message.answer("Отслеживание списка номеров успешно остановлено!")


@dp.message()
async def echo_all(message: Message):
    await message.reply(message.text)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
