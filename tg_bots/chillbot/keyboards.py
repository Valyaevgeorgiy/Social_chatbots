from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = [
    [KeyboardButton(text='Записать')],
    [KeyboardButton(text='Очистить')],
    [KeyboardButton(text='Отправить')]
]

main = ReplyKeyboardMarkup(keyboard=main_kb,
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт ниже.')
