import json
import telebot
import traceback
import pandas as pd
import datetime as dt
from telebot import types
from flask import Flask, request

secret = "SECRET_KEY"  # ключ из BotFather
MY_ID = ''  # айди тг разраба
ADMIN_IDS = []  # айдишники тг админов
ADMIN_FI = ["Валяев Георгий"]  # фи админов
ADMIN_VK_LINK = ["https://vk.com/exponencial"]  # ссылки вк админов

bot = telebot.TeleBot("токен тг бота", threaded=False)  # токен из BotFather
bot.remove_webhook()
bot.set_webhook(url='https://sha2024.pythonanywhere.com/{}'.format(secret))
app = Flask(__name__)  # подключение бота

# расшифровщик и дешифровщик дат собесов под удобный datetime формат
dates_to_locale = {
    "26.02": "26 февраля",
    "27.02": "27 февраля",
    "28.02": "28 февраля",
    "29.02": "29 февраля",
    "01.03": "1 марта",
    "02.03": "2 марта",
    "03.03": "3 марта",
    "04.03": "4 марта",
    "05.03": "5 марта",
}

locale_to_dates = {
    "26 февраля": "26.02",
    "27 февраля": "27.02",
    "28 февраля": "28.02",
    "29 февраля": "29.02",
    "1 марта": "01.03",
    "2 марта": "02.03",
    "3 марта": "03.03",
    "4 марта": "04.03",
    "5 марта": "05.03"
}

try:
    df = pd.read_csv('dataslots.csv')
except:
    bot.send_message(MY_ID, text=f"{str(traceback.format_exc())[:4000]}]")
    df = pd.DataFrame(columns=['user_id', 'status',
                      'fullname', 'vk_link', 'date', 'time'])
    df.to_csv('dataslots.csv', index=False)


def get_user_data(user_id, column=None):
    global df
    user_data = df[df['user_id'] == user_id]
    if user_data.empty:
        return None
    elif column is not None:
        return user_data[column].item()
    return user_data.iloc[0]


def update_user_data(user_id, new_data):
    # new_data = ((столбец1, значение1), (столбец2, значение2))
    global df
    # условие работы с несколькими парами и одной парой значений
    if (len(new_data) >= 2) and (len(new_data[0]) == 2):
        for column, value in new_data:
            df.loc[df['user_id'] == user_id, column] = value
    else:
        df.loc[df['user_id'] == user_id, new_data[0]] = new_data[1]
    df.to_csv('dataslots.csv', index=False)


def load_slots(filename="slots.json"):
    with open(filename, "r") as f:
        return json.load(f)


def save_slots(data, filename="slots.json"):
    with open(filename, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def decrease_slot(date, time):
    slots = load_slots()
    slots[date][time] -= 1
    save_slots(slots)


def increase_slot(date, time):
    slots = load_slots()
    slots[date][time] += 1
    save_slots(slots)


def check_datetime_difference(date_record, time_record):
    global locale_to_dates

    date_now = (dt.datetime.utcnow() +
                dt.timedelta(hours=3)).strftime("%Y.%d.%m")
    time_now = (dt.datetime.utcnow() +
                dt.timedelta(hours=3)).strftime("%H:%M:%S")

    if date_record in list(locale_to_dates.keys()):
        dl_record = locale_to_dates[date_record]

        year_now, day_now, month_now = date_now.split('.')
        day_record, month_record = dl_record.split('.')

        dt_now = dt.datetime(int(year_now), int(month_now), int(day_now))
        dt_record = dt.datetime(int(year_now), int(
            month_record), int(day_record))

        time_record += ":00"

        # до слота на собес строго больше 1 дня
        if ((dt_record - dt_now).days) > 1:
            return True

        # до слота на собес 1 день и сколько-то там времени
        elif ((dt_record - dt_now).days) == 1:
            # в первую очередь, проверяем текущее время
            if time_now < "19:00:00":
                return True
            # если время слота собеса на завтра позднее 19:00, и при этом текущее время позднее 19:00, но также до слота на собес остаётся 1 день и сколько-то там времени
            else:
                return False

        # до слота на собес меньше 1 дня
        elif ((dt_record - dt_now).days) < 1:
            # в первую очередь, проверяем текущее время
            if time_now < "19:00:00":
                # когда мы говорим об одном и том же дне - кейс для дундуков, решивших попробовать что-то в день собеса
                if (day_now == day_record):
                    return "полный ноль"
                # тот самый кейс когда меньше 1 дня, но слот записи на следующий день
                elif (time_now > time_record) and (day_now < day_record):
                    return True
            # если текущее время позднее 19:00
            else:
                return False

        # ниже ПОЛЕЗНЫЙ код по расчёту разницы времени вплоть до секунд

        # if dt_now == dt_record:
        #     time_format = "%H:%M:%S"
        #     time1 = dt.datetime.strptime(time_record, time_format)
        #     time2 = dt.datetime.strptime(time_now, time_format)

        #     # Вычисляем разницу
        #     time_difference = time1 - time2

        #     time_dif_sec = int(time_difference.total_seconds())
        #     time_dif_min = int(time_difference.total_seconds() / 60)
        #     time_dif_h = int(time_difference.total_seconds() / 3600)

        #     if time_dif_sec < 0:
        #         return False
        #     else:
        #         return (time_dif_h, time_dif_min, time_dif_sec)

        # elif dt_now < dt_record:
        #     datetime_record = f"{year_now}-{month_record}-{day_record} {time_record}"
        #     datetime_now = f"{year_now}-{month_now}-{day_now} {time_now}"

        #     datetime_format = "%Y-%m-%d %H:%M:%S"
        #     datetime1 = dt.datetime.strptime(datetime_record, datetime_format)
        #     datetime2 = dt.datetime.strptime(datetime_now, datetime_format)

        #     # Вычисляем разницу
        #     datetime_difference = datetime1 - datetime2

        #     datetime_dif_sec = int(datetime_difference.total_seconds())
        #     datetime_dif_min = int(datetime_difference.total_seconds() / 60)
        #     datetime_dif_h = int(datetime_difference.total_seconds() / 3600)
        #     datetime_dif_days = datetime_difference.days

        #     return (datetime_dif_days, datetime_dif_h, datetime_dif_min, datetime_dif_sec)
    else:
        return False


def create_keyboard(options, back_button=True):
    keyboard = types.InlineKeyboardMarkup()
    for option in options:
        keyboard.add(types.InlineKeyboardButton(
            text=option, callback_data=option))
    if back_button:
        keyboard.add(types.InlineKeyboardButton(
            text="Назад", callback_data="back"))
    return keyboard


def create_confirmation_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(
        "Да", callback_data='confirm_cancel'))
    keyboard.add(types.InlineKeyboardButton(
        "Нет", callback_data='deny_cancel'))
    return keyboard


# подгружаем все доступные слоты собеседований
slots = load_slots()


@app.route('/{}'.format(secret), methods=["POST"])
def flask_start():  # функция - тело самого бота
    global df, slots
    try:  # конструкция трай-эксцепт на проверку ошибок

        # подгружаем актуальное состояние базы авторизованных участников
        df = pd.read_csv('dataslots.csv')

        # открываем базу кандидатов с этапа ДЗ
        members_df = pd.read_csv('membersdb.csv')
        members_fi = list(members_df['fullname'])
        members_vk_link = list(members_df['vk_link'])

        # фиксируем всевозможные статусы пользователя в системе
        statuses = ["начал авторизацию", "ФИ нет в базе", "ввёл ФИ",
                    "ссылки вк нет в базе", "авторизовался", "записался", "выбрал дату собеса"]

        update = request.get_json()  # мы приняли джейсон запрос от телеграмма

        try:
            with open('log.json', 'r', encoding="utf-8") as read_file:  # проверка первый ли это запрос
                log = json.load(read_file)
            read_file.close()
        except FileNotFoundError:
            log = []

        if update['update_id'] in log:  # записывает айди запроса
            return "ok"

        log.append(update['update_id'])

        with open('log.json', 'w') as write_file:
            json.dump(log, write_file)
        write_file.close()

        if "callback_query" in update:
            user_id = update["callback_query"]["message"]["chat"]["id"]
            text = update["callback_query"]["data"]
            user_name = "кандидат"

            try:
                # имя пользователя
                user_name = update["callback_query"]["message"]["chat"]["first_name"]
            except:
                user_name = "кандидат"

        if "message" in update:  # берёт информацию из сообщения
            user_id = update["message"]["chat"]["id"]  # айди пользователя
            user_name = "кандидат"

            try:
                # имя пользователя
                user_name = update["message"]["chat"]["first_name"]
            except:
                user_name = "кандидат"

            if "photo" in update["message"] or "video" in update["message"] or "voice" in update["message"] or "sticker" in update["message"] or "document" in update["message"]:
                bot.send_message(
                    int(user_id), "К сожалению, данный бот не принимает файлы.")
                return "ok"

            if "text" in update["message"]:  # обработка текста
                text = update["message"]["text"]

        # Основной функционал
        if user_id in ADMIN_IDS and text.startswith('!'):
            # админская панель функций

            if text.lower() == "!помощь":
                # вывод всех админских команд
                bot.send_message(int(user_id), "Добро пожаловать в админскую панель функций!\nТебе доступны следующие команды:\n\n!помощь — выводит данное сообщение.\n!кандидаты — выводит общую сводку записавшихся на собеседование кандидатов.\n!(дата собеса) (например, !1 марта) — получить список записавшихся на собеседование кандидатов по указанной дате.\n\nПользуйся ими с умом и кайфом!")
                return "ok"

            elif text.lower() == "!очистить себя":
                update_user_data(user_id, (("status", "начал авторизацию"), (
                    "fullname", None), ("vk_link", None), ("date", None), ("time", None)))
                bot.send_message(
                    int(user_id), "Ты очищен(-а)!\nТеперь мир перед тобой полностью открыт!")
                return "ok"

            elif text.lower() == "!база":
                members_fi = [fi for fi in members_fi if fi not in ADMIN_FI]
                members_vk_link = [
                    vk_link for vk_link in members_vk_link if vk_link not in ADMIN_VK_LINK]
                members_range = list(range(len(members_fi)))
                message = "База кандидатов:\n\n"
                for index, fi, vk_link in zip(members_range, members_fi, members_vk_link):
                    if (index+1) % 50 == 0:
                        message += f"{index+1}) {fi} ({vk_link})" + "\n"
                        bot.send_message(int(user_id), message)
                        message = ""
                    else:
                        message += f"{index+1}) {fi} ({vk_link})" + "\n"
                bot.send_message(int(user_id), message)
                return "ok"

            elif text.lower() == "!кандидаты":
                # получение общего списка записавшихся
                message_1, counter_1 = 'Записавшиеся на собеседование кандидаты:\n\n', 1
                message_2, counter_2 = '\nКандидаты с иным статусом в системе:\n\n', 1
                candidates = [(index, row) for index, row in list(
                    df.iterrows()) if row['user_id'] not in ADMIN_IDS]
                for index, row in candidates:
                    if row['status'] == "записался":
                        if len(message_1) >= 2500:
                            bot.send_message(int(user_id), message_1)
                            message_1 = 'Записавшиеся на собеседование кандидаты:\n\n'
                        else:
                            message_1 += f"{counter_1}) {row['fullname']} ({row['vk_link']}), {row['date']} в {row['time']}\n"
                            counter_1 += 1
                    else:
                        if len(message_2) >= 2500:
                            bot.send_message(int(user_id), message_2)
                            message_2 = '\nКандидаты с иным статусом в системе:\n\n'
                        else:
                            if row['status'] == "ввёл ФИ":
                                message_2 += f"{counter_2}) {row['fullname']}, статус — {row['status']}\n"
                            elif row['status'] == "авторизовался":
                                message_2 += f"{counter_2}) {row['fullname']} ({row['vk_link']}), статус — {row['status']}\n"
                            elif row['status'] == "выбрал дату собеса":
                                message_2 += f"{counter_2}) {row['fullname']} ({row['vk_link']}), {row['date']}, статус — {row['status']}\n"

                            counter_2 += 1

                if message_1 == 'Записавшиеся на собеседование кандидаты:\n\n' and message_2 == '\nКандидаты с иным статусом в системе:\n\n':
                    message = "Пока никого нету, но мы над этим работаем!"
                elif message_1 != 'Записавшиеся на собеседование кандидаты:\n\n' and message_2 != '\nКандидаты с иным статусом в системе:\n\n':
                    message = message_1 + message_2 + "\nГотово!"
                elif message_1 == 'Записавшиеся на собеседование кандидаты:\n\n':
                    message = message_2 + "\nГотово!"
                elif message_2 == '\nКандидаты с иным статусом в системе:\n\n':
                    message = message_1 + "\nГотово!"

                bot.send_message(int(user_id), message)
                return "ok"

            else:
                requested_date = text[1:].strip()
                if requested_date in slots:
                    registered_users = df[(df['date'] == requested_date)]
                    if not registered_users.empty:
                        response_text = f"На {requested_date} записались:\n\n"
                        regs_user = [row for index,
                                     row in registered_users.iterrows()]
                        response_text += "\n".join(
                            [f"{index+1}) {row['fullname']} ({row['vk_link']}), {row['date']} в {row['time']}" for index, row in enumerate(regs_user)])
                        bot.send_message(int(user_id), response_text)
                    else:
                        bot.send_message(
                            int(user_id), f"Никто не записан на {requested_date}.")
                else:
                    bot.send_message(int(
                        user_id), "К сожалению, выбрана неверная дата: напиши через «!» даты в диапазоне от 27 февраля до 4 марта!")

                return "ok"

        if text == '/id':  # возвращает твой айди
            bot.send_message(int(user_id), user_id)

        elif text == '/start':
            # обработка ситуаций авторизации и повторного начала работы с системой

            user_data = get_user_data(user_id)
            if user_data is None:
                df.loc[len(df)] = [user_id, 'начал авторизацию',
                                   None, None, None, None]
                df.to_csv('dataslots.csv', index=False)
                bot.send_message(int(
                    user_id), f"Привет, {user_name}!\n\nУчти, что дальше необходимо заполнить точные данные для успешной авторизации!\n\nПожалуйста, представься (Фамилия Имя).")
            else:
                if get_user_data(user_id, "status") == "начал авторизацию" or get_user_data(user_id, "status") == "ФИ нет в базе":
                    bot.send_message(int(
                        user_id), f"Привет, {user_name}!\n\nУчти, что дальше необходимо заполнить точные данные для успешной авторизации!\n\nПожалуйста, представься (Фамилия Имя).")

                elif get_user_data(user_id, "status") == "ссылки вк нет в базе" or get_user_data(user_id, "status") == "ввёл ФИ":
                    bot.send_message(int(
                        user_id), "Привет-привет!\nПродолжается процесс твоей авторизации в системе...\n\nТеперь отправь свою ссылку на аккаунт VK, от которого ты проходишь отбор.\n\nПример ссылки, которая должна быть: https://vk.com/exponencial!")

                elif get_user_data(user_id, "status") == "записался":
                    # сообщение о подтверждённой записи
                    bot.send_message(int(
                        user_id), f"Привет, {user_name}!\n\nТы успешно записался(-ась) на собеседование!\n\nИспользуй команды из меню для получения информации о своей записи или для отмены своей записи!")

                elif get_user_data(user_id, "status") == "авторизовался":
                    # сообщение о подтверждённой авторизации
                    bot.send_message(int(
                        user_id), f"Привет, {user_name}!\n\nТы успешно авторизовался(-ась) в системе!\n\nИспользуй команду «/signup» из меню для записи на собеседование!")

        elif text == '/signup' and get_user_data(user_id, "status") != "авторизовался":
            slots = load_slots()
            if get_user_data(user_id, "status") == "записался":
                bot.send_message(
                    int(user_id), "Ты уже записан(-а) на собеседование!")

            elif get_user_data(user_id, "status") == "выбрал дату собеса":
                date_user = get_user_data(user_id, "date")
                bot.send_message(int(
                    user_id), f"Твоя запись на собеседование в процессе: выбрана дата — {date_user}!")

            elif get_user_data(user_id, "status") in ["начал авторизацию", "ФИ нет в базе", "ввёл ФИ", "ссылки вк нет в базе"]:
                bot.send_message(int(
                    user_id), "Запись на собеседование невозможна: необходимо пройти процесс авторизации!")

            else:
                bot.send_message(
                    int(user_id), "Для входа в систему используй команду «/start»!")

        elif text == '/cancel' and get_user_data(user_id, "status") != "записался":

            if get_user_data(user_id, "status") in ["начал авторизацию", "ФИ нет в базе", "ввёл ФИ", "ссылки вк нет в базе"]:
                bot.send_message(int(
                    user_id), "Отмена записи на собеседование невозможна: необходимо пройти процесс авторизации!")

            elif get_user_data(user_id, "status") == "авторизовался":
                bot.send_message(int(
                    user_id), "Отмена записи на собеседование невозможна: необходимо записаться на собеседование!")

            elif get_user_data(user_id, "status") == "выбрал дату собеса":
                date_user = get_user_data(user_id, "date")
                bot.send_message(int(
                    user_id), f"Отмена записи на собеседование невозможна, поскольку твоя запись на собеседование в процессе: выбрана дата — {date_user}!")

            else:
                bot.send_message(
                    int(user_id), "Для входа в систему используй команду «/start»!")

        elif text == '/record' and get_user_data(user_id, "status") != "записался":

            if get_user_data(user_id, "status") in ["начал авторизацию", "ФИ нет в базе", "ввёл ФИ", "ссылки вк нет в базе"]:
                bot.send_message(int(
                    user_id), "Получение информации о записи невозможно: необходимо пройти процесс авторизации!")

            elif get_user_data(user_id, "status") == "авторизовался":
                bot.send_message(int(
                    user_id), "Получение информации о записи невозможно: необходимо записаться на собеседование!")

            elif get_user_data(user_id, "status") == "выбрал дату собеса":
                date_user = get_user_data(user_id, "date")
                bot.send_message(int(
                    user_id), f"Получение информации о записи невозможно, поскольку твоя запись на собеседование в процессе: выбрана дата — {date_user}!")

            else:
                bot.send_message(
                    int(user_id), "Для входа в систему используй команду «/start»!")

        else:
            # Обрабатываем все оставшиеся ситуации с разделением на блоки по статусу пользователя в системе
            status = get_user_data(user_id, "status")

            # 1. Авторизация — ввод ФИ и ссылки на ВК
            if status == "начал авторизацию" or status == "ФИ нет в базе":
                if text in members_fi:
                    # проверяем на то, есть ли уже среди авторизованных этот чел
                    if text not in list(df['fullname']):
                        update_user_data(
                            user_id, (("fullname", text), ("status", "ввёл ФИ")))
                        bot.send_message(int(
                            user_id), "Супер!\nТеперь отправь свою ссылку на аккаунт VK, от которого ты проходишь отбор.\n\nПример ссылки, которая должна быть: https://vk.com/exponencial!")
                    else:
                        bot.send_message(int(
                            user_id), "Кандидат с такими ФИ уже авторизован(-а) в системе!\n\nПопробуй, пожалуйста, снова либо напиши в личные сообщения группы Тренинг-Центра по вопросу актуализации информации!")
                else:
                    update_user_data(user_id, ("status", "ФИ нет в базе"))
                    bot.send_message(int(
                        user_id), "Такого ФИ нет в базе кандидатов, проходящих отбор.\n\nПопробуй, пожалуйста, снова либо напиши в личные сообщения группы Тренинг-Центра по вопросу актуализации информации!")

            elif status == "ввёл ФИ" or status == "ссылки вк нет в базе":
                if text in members_vk_link:
                    fullname_user = get_user_data(user_id, 'fullname')
                    index_userdb = members_fi.index(fullname_user)
                    valid_vk_link = members_vk_link[index_userdb]

                    # проверяем на то, есть ли уже среди авторизованных этот чел
                    if text not in list(df['vk_link']):
                        # проверяем, правильную ли ссылку именно на свой VK чел указал в соответствие с ФИ
                        if text == valid_vk_link:
                            update_user_data(
                                user_id, (("vk_link", text), ("status", "авторизовался")))
                            bot.send_message(int(
                                user_id), "Принято!\n\nАвторизация успешно пройдена!\n\nТеперь ты можешь записаться на собеседование на необходимую дату и время.")
                        else:
                            bot.send_message(int(
                                user_id), "Указана ссылка на VK другого кандидата!\nПопробуй, пожалуйста, снова указать свою правильную ссылку на аккаунт VK.")
                    else:
                        bot.send_message(int(
                            user_id), "Кандидат с такой ссылкой на аккаунт VK уже авторизован(-а) в системе!\n\nПопробуй, пожалуйста, снова либо напиши в личные сообщения группы Тренинг-Центра по вопросу актуализации информации!")
                else:
                    update_user_data(
                        user_id, ("status", "ссылки вк нет в базе"))
                    bot.send_message(int(
                        user_id), "Такой ссылки на VK нет в базе кандидатов, проходящих отбор.\n\nПопробуй, пожалуйста, снова либо напиши в личные сообщения группы Тренинг-Центра по вопросу актуализации информации!")

            elif status == "авторизовался":

                # 2. Запись на собеседование
                if text == '/signup':

                    # регулярно подгружаем актуальные слоты для записи
                    slots = load_slots()

                    # ЧЕКАЕМ время, когда чел решился записаться
                    time_now = (dt.datetime.utcnow() +
                                dt.timedelta(hours=3)).strftime("%H:%M:%S")
                    dates = list(slots.keys())  # Получаем все доступные даты
                    if time_now < "19:00:00":
                        # Убираем слоты текущей даты и показываем слоты, начиная со следующей даты
                        date_now = (dt.datetime.utcnow() +
                                    dt.timedelta(hours=3)).strftime("%d.%m")
                        date_locale_now = dates_to_locale[date_now]
                        index_dt = dates.index(date_locale_now) + 1
                        # Смотрим, остаются ли доступные слоты дат на запись, и проверяем по индексам
                        if index_dt < len(dates):
                            new_dates = dates[index_dt:]
                            bot.send_message(int(user_id), text="Теперь выбери дату собеседования ниже 👇",
                                             reply_markup=create_keyboard(new_dates, back_button=False))
                        else:
                            bot.send_message(int(
                                user_id), "Запись на собеседование недоступна: слишком позднее время записи (либо закончились все слоты)!")
                    else:
                        # Убираем дату следующего дня из доступных
                        date_now = (dt.datetime.utcnow() +
                                    dt.timedelta(hours=3)).strftime("%d.%m")
                        date_locale_now = dates_to_locale[date_now]
                        index_dt = dates.index(date_locale_now) + 2
                        # Смотрим, остаются ли доступные слоты дат на запись, и проверяем по индексам
                        if index_dt < len(dates):
                            new_dates = dates[index_dt:]
                            bot.send_message(int(user_id), text="Теперь выбери дату собеседования ниже 👇",
                                             reply_markup=create_keyboard(new_dates, back_button=False))
                        else:
                            bot.send_message(
                                int(user_id), "Запись на собеседование недоступна: слишком позднее время записи!")

                # Ответ на callback от кнопок дат
                elif text in list(slots.keys()):
                    bot.send_message(
                        int(user_id), f"Оукей!\nВыбрана дата — {update['callback_query']['data']}!")
                    update_user_data(
                        user_id, (("status", "выбрал дату собеса"), ("date", text)))
                    date_selected = get_user_data(
                        user_id, "date")  # Получаем выбранную дату

                    # фильтруем пустые слоты времени по выбранной дате записи на собес
                    # Получаем все доступные времена для выбранной даты
                    times = [time for time in list(
                        slots[date_selected].keys()) if slots[date_selected][time] > 0]
                    if len(times) > 0:
                        bot.send_message(int(
                            user_id), text="Теперь выбери время собеседования.", reply_markup=create_keyboard(times))
                    else:
                        # чекаем ситуацию, когда на дату закончились все слоты времени
                        update_user_data(
                            user_id, (('status', 'авторизовался'), ('date', None)))
                        bot.send_message(int(
                            user_id), f"На {date_selected} закончились слоты записи. Попробуй ещё раз использовать команду «/signup»!")
                else:
                    bot.send_message(int(
                        user_id), "Ты успешно авторизован(-а) в системе!\nИспользуй команду «/signup» из меню для записи на собеседование!")

            # 2.1 Переход с выбора времени обратно к выбору даты
            elif status == "выбрал дату собеса":

                user_selected_date = get_user_data(user_id, "date")

                if text == "back":
                    update_user_data(
                        user_id, (('status', 'авторизовался'), ('date', None), ('time', None)))

                    # ЧЕКАЕМ время, когда чел решился записаться
                    time_now = (dt.datetime.utcnow() +
                                dt.timedelta(hours=3)).strftime("%H:%M:%S")
                    dates = list(slots.keys())  # Получаем все доступные даты
                    if time_now < "19:00:00":
                        # Убираем слоты текущей даты и показываем слоты, начиная со следующей даты
                        date_now = (dt.datetime.utcnow() +
                                    dt.timedelta(hours=3)).strftime("%d.%m")
                        date_locale_now = dates_to_locale[date_now]
                        index_dt = dates.index(date_locale_now) + 1
                        # Смотрим, остаются ли доступные слоты дат на запись, и проверяем по индексам
                        if index_dt < len(dates):
                            new_dates = dates[index_dt:]
                            bot.send_message(int(user_id), text="Выбери дату снова 👇", reply_markup=create_keyboard(
                                new_dates, back_button=False))
                        else:
                            bot.send_message(int(
                                user_id), "Запись на собеседование недоступна: слишком позднее время записи (либо закончились все слоты)!")
                    else:
                        # Убираем дату следующего дня из доступных
                        date_now = (dt.datetime.utcnow() +
                                    dt.timedelta(hours=3)).strftime("%d.%m")
                        date_locale_now = dates_to_locale[date_now]
                        index_dt = dates.index(date_locale_now) + 2
                        # Смотрим, остаются ли доступные слоты дат на запись, и проверяем по индексам
                        if index_dt < len(dates):
                            new_dates = dates[index_dt:]
                            bot.send_message(int(user_id), text="Выбери дату снова 👇", reply_markup=create_keyboard(
                                new_dates, back_button=False))
                        else:
                            bot.send_message(
                                int(user_id), "Запись на собеседование недоступна: слишком позднее время записи!")

                elif text in list(slots[user_selected_date].keys()):
                    # Проверка доступности слота времени
                    if slots[user_selected_date][text] > 0:
                        update_user_data(
                            user_id, (('status', 'записался'), ('time', text)))
                        # Уменьшаем доступные слоты
                        decrease_slot(user_selected_date, text)
                        bot.send_message(int(user_id), text=f"Ты успешно записался(-ась) на собеседование!\n\nДата: {user_selected_date}\nВремя: {text}", reply_markup=create_keyboard(
                            ["Отменить запись"], back_button=False))
                    else:
                        times = list(slots[user_selected_date].keys())
                        bot.send_message(int(
                            user_id), text="На это время уже записан кандидат. Выбери другое время.", reply_markup=create_keyboard(times))

            elif status == "записался":

                user_data = get_user_data(user_id)
                name_user, date_user, time_user = user_data["fullname"], user_data["date"], user_data["time"]

                # 3. Отмена записи на собес
                if text == "Отменить запись" or text == "/cancel":

                    # ВЫЧИСЛЯЕМ РАЗНИЦУ ВО ВРЕМЕНИ
                    dt_diff = check_datetime_difference(date_user, time_user)

                    if dt_diff:
                        # проверяем, что чел отменяет запись более чем за час до самого собеса вплоть до секунд
                        bot.send_message(int(
                            user_id), text="Вы уверены, что хотите отменить запись?", reply_markup=create_confirmation_keyboard())
                    elif dt_diff == "полный ноль":
                        bot.send_message(int(
                            user_id), "Отмена записи на собеседование невозможна: твоё собеседование уже прошло!")
                    else:
                        bot.send_message(
                            int(user_id), "Отмена записи на собеседование невозможна: позднее время отмены!")

                elif text == "confirm_cancel":
                    # Увеличиваем доступные слоты
                    increase_slot(date_user, time_user)
                    # Сбрасываем статус, дату и время
                    update_user_data(
                        user_id, (('status', 'авторизовался'), ('date', None), ('time', None)))
                    bot.send_message(
                        int(user_id), "Твоя запись на собеседование была отменена!")

                elif text == "deny_cancel":
                    bot.send_message(
                        int(user_id), "Отмена отменена. Вы всё ещё успешно записаны на собеседование!")

                # 4. Получение информации о своей записи на собес
                elif text == "/record":
                    bot.send_message(int(
                        user_id), f"Информация о твоей записи на собеседование:\n\nФамилия Имя — {name_user}\nДата — {date_user}\nВремя — {time_user}\nМесто — г. Москва, м. Аэропорт\n\nПодробнее о месте проведения собеседования можно будет узнать в день собеседования в личных сообщениях группы Тренинг-Центра!")

                else:
                    bot.send_message(int(
                        user_id), f"Ещё раз привет, {user_name}!\n\nТы успешно записан(-а) на собеседование!\n\nЕсли хочешь посмотреть свою запись, используй «/record».\nЕсли хочешь отменить свою запись, используй «/cancel»!")

    except:  # если изначально какая-то ошибка кидает тебе её
        bot.send_message(
            MY_ID, text=f"{str(traceback.format_exc())[:4000]}]")  # ошибку
        bot.send_message(MY_ID, text=f"{str(update)[:4000]}]")  # текст запроса
    return "ok"
