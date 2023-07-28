from flask import Flask, request, json
from faq import FAQ
import vk_api
import traceback
from vk_api.utils import get_random_id

# Объект бота представляющий собой группу, от которой приходят сообщения
vk_session = vk_api.VkApi(
    token="токен группы")

# Объект бота личного аккаунта, позволяющий пользоваться большинством методов
vk_u = vk_api.VkApi(token="токен юзера админа группы")
app = Flask(__name__)


def send_message(peer_id, message, keyboard=None):
    args = {
        'peer_id': peer_id,
        'message': message,
        'random_id': get_random_id()
    }
    if keyboard is not None:
        args['keyboard'] = json.JSONEncoder().encode(keyboard)
    vk_session.method('messages.send', args)


main_kb_faq = {
    "one_time": False,
    "inline": False,
    "buttons": [
        [
            {
                "action": {
                    "type": "text",
                    "payload": {
                        "function": "update"
                    },
                    "label": "💫 Обновить таблицу"
                },
                "color": "primary"
            }
        ],
        [
            {
                "action": {
                    "type": "text",
                    "payload": {
                        "function": "help"
                    },
                    "label": "❓ Помощь"
                },
                "color": "secondary"
            }
        ]
    ]
}

plug_kb = {
    "inline": True,
    "buttons": [
        [
            {
                "action": {
                    "type": "text",
                    "payload": {
                        "function": "plug_on"
                    },
                    "label": "Включить"
                },
                "color": "positive"
            },
            {
                "action": {
                    "type": "text",
                    "payload": {
                        "function": "plug_off"
                    },
                    "label": "Выключить"
                },
                "color": "negative"
            }
        ]
    ]
}

# айди беседы тестовой для работы с ботом (id чата ГО и Старших)
id_testchat = "..."

faq_table = FAQ(name="Бот_FAQ_ПК",
                sheet_link="https://docs.google.com/spreadsheets/d/1WqtGUcJmr-fPrdV7VosDbUj-FxnCWbLlfayHWsImzAk/edit#gid=0",
                status=True)

# Логический флаг для функционирования механики обращения пользователей в поддержку
is_problem = False

# Логический флаг для функционирования работы режима заглушки у бота
is_plug = False


@app.route('/', methods=["POST"])  # функция, принимающая запросы
def main():
    global is_problem, is_plug
    try:
        # Преобразовываем json-ответ в питоновский объект
        data = json.loads(request.data)
        templates = faq_table.get_templates()  # Получение актуальной клавиатуры кнопок

        if data["type"] == "confirmation":  # Если событие — подтверждение группы
            return "код подтверждения"

        if data["type"] == "message_new":  # Если событие — сообщение
            object_0 = data["object"]["message"]
            object_1 = data["object"]["client_info"]

            peer_id = object_0["peer_id"]
            body = object_0["text"]
            from_id = str(object_0['from_id'])

            keyboard_work = object_1["keyboard"]

            if keyboard_work == 1:

                # функционал бота, который работает везде

                # функция, показывающая id беседы (чата или переписки с пользователем)
                if body.lower()[:5] == "!айди":
                    send_message(peer_id, message=peer_id)

                elif body.lower()[:7] == "!начать":
                    template = templates['menu']
                    send_message(peer_id, **template)

                # функционал бота, который работает в чате с ГО и Старшими
                if str(peer_id) == id_testchat:
                    if body.lower()[:7] == "!помощь":
                        msg = "Добро пожаловать в чат Старших и ГО Проектного комитета!\n\nКоманды для вас, доступные в этом чате:\n\n1) !старт — позволяет вывести кнопки для обновления данных таблицы и вывода информации о таблице и группе проекта.\n\n2) !заглушка — помогает ввести в бота заглушку на возможные ошибки в работе и выводить сообщение о ведении технических работ над ботом группы!\n\nПриятного пользования!!!"
                        send_message(peer_id, msg)

                    elif body.lower()[:6] == "!старт":
                        send_message(
                            peer_id, f"Бот FAQ\n\n{faq_table.__str__()}\n\nЧем могу помочь?", main_kb_faq)

                    # функция заглушки работы бота
                    elif body.lower()[:9] == "!заглушка":
                        send_message(
                            peer_id, "Функция заглушки работы бота. Что стоит сделать с ней?", plug_kb)

                # функционал бота, который работает в личке
                else:

                    # отображение функции "бот печатает..."
                    arguments = {
                        "peer_id": peer_id,
                        "type": "typing"
                    }
                    vk_session.method('messages.setActivity', arguments)

                    # если пользователь отправляет стикер, то получает его же в ответ (принцип эхо-сервера)

                    try:
                        if len(object_0["attachments"]) != 0:
                            if object_0["attachments"][0]["type"] == "sticker":
                                args = {
                                    'peer_id': peer_id,
                                    'sticker_id': object_0["attachments"][0]["sticker"]["sticker_id"],
                                    'random_id': get_random_id()
                                }
                                vk_session.method('messages.send', args)
                            return 'ok'
                    except Exception as e:
                        pass

                    search_user_says = faq_table.search_user_says(body.lower())
                    faq_table.clean_template_scores()

                    # случай, когда юзер сейсы не дали вообще никакого результата — сигнал об ошибке в программе
                    # тут с целью поддержания диалога с пользователем в ответ выдаётся то же сообщение, которое пользователь ввёл
                    # и на которое бот не нашёл вообще никакого шаблона в базе

                    # начало работы чат-бота с NLP (функционирование user says)
                    if "payload" not in object_0.keys():
                        # подготовка клавиатуры для обработки ситуаций с неточными и точными совпадениями (топ-3)

                        # список заголовков для inline-кнопок
                        labels_templates = faq_table.render_full_names_templates()

                        # список наших потенциальных templates
                        potential_templates = search_user_says[1:]

                        if is_problem:
                            # 2. получение текста с проблемой-вопросом от пользователя и его передача в чат ГО и Старших
                            user_name = vk_session.method(
                                "users.get", {"user_ids": peer_id, "name_case": "Nom"})
                            notification = "@id" + from_id + " (" + user_name[0]['first_name'] + " " + user_name[0][
                                'last_name'] + ") написал(-а) в группу сообщение:\n\n<<" + body + ">>\n\nЧеловек ждёт ответа: vk.com/gim216949180?sel=" + from_id + "\nСсылка на сообщения группы: vk.com/gim216949180"
                            send_message(id_testchat, message=notification)

                            # 3. отправка пользователю сообщения о том, что информация о проблеме-вопросе успешно принята!
                            done_msg = 'Отлично! Информацию приняли, тебе в скором времени ответит один из наших ребят!'
                            send_message(peer_id, message=done_msg)

                            is_problem = False

                            # 4. автоматический вывод главного шаблона после отправки сообщения с проблемой
                            template = templates['menu']
                            send_message(peer_id, **template)

                        # очень много есть случаев и кейсов обработки юс, которые я сгруппировал по индикаторам ниже

                        # точное попадание под юс и template
                        elif search_user_says[0] == 0:
                            name_template = search_user_says[1]
                            if name_template == "support_0":
                                # тут будет функционал по отправке вопроса в чат ГО и Старших

                                # 1. отправка пользователю сообщения о том, что он может описать свою проблему поподробнее ниже
                                template = templates['support_0']
                                send_message(peer_id, **template)
                            else:
                                template = templates[name_template]
                                send_message(peer_id, **template)

                        # ситуация, когда найдено 2 точных совпадения
                        elif search_user_says[0] == 2:
                            keyboard = {
                                "inline": True,
                                "buttons": []
                            }

                            button = [
                                {
                                    "action": {
                                        "type": "text",
                                        "payload": {
                                            "template": potential_templates[0]
                                        },
                                        "label": labels_templates[potential_templates[0]]
                                    },
                                    "color": "primary"
                                },
                                {
                                    "action": {
                                        "type": "text",
                                        "payload": {
                                            "template": potential_templates[1]
                                        },
                                        "label": labels_templates[potential_templates[1]]
                                    },
                                    "color": "primary"
                                }
                            ]

                            button2 = str(button).replace("'", '"')
                            button22 = json.loads(button2)
                            keyboard["buttons"].append(button22)

                            message = "Точного ответа по такой теме не найдено, но есть большая уверенность в том, что по этим темам ниже вы точно найдёте ответ на свой вопрос!"
                            send_message(peer_id, message=message,
                                         keyboard=keyboard)

                        elif len(potential_templates) == 3:
                            keyboard = {
                                "inline": True,
                                "buttons": []
                            }

                            button = [
                                {
                                    "action": {
                                        "type": "text",
                                        "payload": {
                                            "template": potential_templates[0]
                                        },
                                        "label": labels_templates[potential_templates[0]]
                                    },
                                    "color": "primary"
                                },
                                {
                                    "action": {
                                        "type": "text",
                                        "payload": {
                                            "template": potential_templates[1]
                                        },
                                        "label": labels_templates[potential_templates[1]]
                                    },
                                    "color": "primary"
                                },
                                {
                                    "action": {
                                        "type": "text",
                                        "payload": {
                                            "template": potential_templates[2]
                                        },
                                        "label": labels_templates[potential_templates[2]]
                                    },
                                    "color": "primary"
                                }
                            ]

                            button1 = str(button).replace("'", '"')
                            button11 = json.loads(button1)
                            keyboard["buttons"].append(button11)

                            # ситуация, когда найдено 3 и более точных совпадений
                            if search_user_says[0] == 3:
                                message = "Точного ответа по такой теме не найдено, но есть большая уверенность в том, что по этим темам ниже вы точно найдёте ответ на свой вопрос!"
                                send_message(
                                    peer_id, message=message, keyboard=keyboard)

                            # вывод 3 примерных template под текст пользователя (0 точных совпадений)
                            elif search_user_says[0] == -1:
                                message = "По такой теме при поиске что-то пошло не так, но получилось найти нечто точно похожее ниже!"
                                send_message(
                                    peer_id, message=message, keyboard=keyboard)

                    # реагирование на ситуации, когда пользователь не печатает текст, а пользуется кнопками
                    else:
                        # здесь мы ловим ситуацию и запоминаем её при прослушивании текста с проблемой-вопросом
                        is_problem = False

                try:
                    payload = json.JSONDecoder().decode(object_0["payload"])
                    if payload["function"] == "update":
                        templates = faq_table.render_templates()
                        send_message(peer_id, "Данные обновлены!!!")

                    if payload["function"] == "help":
                        send_message(
                            peer_id, f"Бот FAQ\n\n{faq_table.__str__()}\n\nЧем могу помочь?", main_kb_faq)

                    if payload["function"] == "plug_on":
                        is_plug = True
                        send_message(peer_id, "Заглушка успешно включена!!")

                    if payload["function"] == "plug_off":
                        is_plug = False
                        send_message(peer_id, "Заглушка успешно отключена!!")

                except KeyError:
                    pass

                try:
                    payload = json.JSONDecoder().decode(object_0["payload"])
                    try:
                        # пробуем достать шаблон
                        t_name = payload["template"]
                        if t_name in templates.keys():
                            if t_name == 'support_0':
                                # тут будет функционал по отправке вопроса в чат ГО и Старших

                                # 1. отправка пользователю сообщения о том, что он может описать свою проблему поподробнее ниже
                                template = templates['support_0']
                                send_message(peer_id, **template)
                            elif t_name == 'support_1':
                                is_problem = True
                                template = templates['support_1']
                                send_message(peer_id, **template)
                            else:
                                template = templates[t_name]
                                send_message(peer_id, **template)
                    except KeyError:
                        # пробуем достать текст
                        answer = payload["text"]
                        send_message(peer_id, answer)
                except KeyError:
                    pass

            elif keyboard_work == 0:
                message = "На вашей версии VK не поддерживаются меню-клавиатуры ботов.\nВозможное решение: воспользуйтесь другим устройством."
                send_message(peer_id, message=message)

    except:  # Если возникает ошибка, сообщаем об этом разработчику

        # Также при включённом режиме заглушки отправляем пользователю сообщение о ведении технических работ

        if is_plug:
            send_message(
                peer_id, "Сейчас ведутся технические работы, попробуйте повторить попытку позже.")

        message = "Бро, тут возник конфуз, проверь, пеже:\n\n" + \
            str(traceback.format_exc())
        send_message(peer_id='...', message=message)

    return 'ok'
