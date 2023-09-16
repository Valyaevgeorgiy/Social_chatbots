import time
import asyncio
import keyboards as kb
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

telegram_token = 'токен тг бота'

bot = Bot(telegram_token)
dp = Dispatcher()

handle_messages = {}
is_handle = False


class UserStorage:
    def __init__(self, user_id):
        self.user_id = user_id
        self.message = None

    def set_message(self, message):
        self.message = message

    def clean_message(self):
        self.message = None

    def get_message(self):
        return self.message


@dp.message(F.text == '/start')
async def cmd_start(message: Message):
    await message.answer('Привет!\nЯ — бот «основа, так сказать, база». Чем могу помочь?')


@dp.message(F.text == '/help')
async def cmd_help(message: Message):
    txt = "Итак, помогаю:\n\n/start — это запуск бота с приветственным сообщением\n/help — сообщение, которое ты сейчас читаешь\n/kb — клавиатура с фишечками записи и получения записанного сообщения\n/mem — подготовленный от меня мем\n\nХорошего тебе дня!"
    await message.answer_photo(photo='https://bronk.club/uploads/posts/2023-07/1688435416_bronk-club-p-pozitivnie-otkritki-s-dnem-rozhdeniya-pozd-48.jpg',
                               caption=txt)


@dp.message(F.text == '/kb')
async def handle_keyboard(message: Message):
    await message.answer("Изучай возможности клавиатуры ниже", reply_markup=kb.main)


@dp.message(F.text == "/mem")
async def cmd_mem(message: Message):
    await message.answer_photo(photo='https://img.gazeta.ru/files3/998/13419998/zag-pic4_zoom-1500x1500-59978.jpg',
                               caption='Вот тебе мем :)')
    time.sleep(5)
    await message.answer_photo(photo='https://news.store.rambler.ru/img/8216a3fa1bdcc02143a78295811e74ac?img-format=auto&img-1-resize=height:350,fit:max&img-2-filter=sharpen',
                               caption='Опа, а вот ещё, хехехехе')


@dp.message(F.text == 'Записать')
async def get_message(message: Message):
    global is_handle

    user_id = message.from_user.id
    await message.answer("Введите ваше сообщение")

    user_storage = UserStorage(user_id)
    handle_messages[user_id] = user_storage
    is_handle = True


@dp.message(F.text == 'Очистить')
async def clean_storage_message(message: Message):
    user_id = message.from_user.id
    user_storage = handle_messages.get(user_id)

    if user_storage and user_storage.message:
        user_storage.clean_message()
        await message.answer("Сообщение успешно очищено!")
    else:
        await message.answer("У вас нет записанных сообщений")


@dp.message(F.text == 'Отправить')
async def send_handle_message(message: Message):
    user_id = message.from_user.id
    user_storage = handle_messages.get(user_id)

    if user_storage and user_storage.get_message():
        await message.answer(user_storage.get_message())
    else:
        await message.answer("У вас нет записанных сообщений")


@dp.message(lambda message: is_handle and handle_messages.get(message.from_user.id) and not handle_messages[message.from_user.id].get_message())
async def get_storage_message(message: Message):
    global is_handle
    user_id = message.from_user.id
    user_storage = handle_messages.get(user_id)

    if user_storage:
        is_handle = False
        user_storage.set_message(message.text)
        await message.answer("Сообщение успешно записано!")


@dp.message()
async def echo_all(message: Message):
    await message.reply(message.text)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Выход с бота...')
