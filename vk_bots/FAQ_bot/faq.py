import httplib2
import json
import os
import nltk
import re
import time
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from pymystem3 import Mystem


def get_service_sacc():
    """Создание сервисного аккаунта Google"""
    creds_json = os.path.dirname(__file__) + "/creds/mysacc2.json"
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds_service = ServiceAccountCredentials.from_json_keyfile_name(
        creds_json, scopes).authorize(httplib2.Http())
    return build('sheets', 'v4', http=creds_service)


# Подключение к Google Sheets
service = get_service_sacc()
sheet = service.spreadsheets()


class FAQ(object):
    def __init__(self, name: str, sheet_link: str, status: bool, timer='', sheet_name="FAQ"):
        self.name = name
        self.sheet_link = sheet_link
        self.shortlink = sheet_link
        self.sheet_name = sheet_name
        self.sheet_id = self.sheet_link.split('/')[-2]
        self.status = status
        self.timer = timer
        # Все данные из листа
        self.all_values = sheet.values().get(spreadsheetId=self.sheet_id,
                                             range=f"{self.sheet_name}!A1:ZZ100").execute()['values'][2:]

        # массив примитивных названий (юзер сейс)
        self.user_says = [element[0] for element in self.all_values]
        # название шаблона и сообщение от бота
        self.templates = [element[2:4] for element in self.all_values]
        # прямые наименования шаблонов
        self.names_templates = [element[2] for element in self.all_values][:-1]
        # массив кнопок, нужно их объединить в клавиатуру
        self.buttons = [element[-1] for element in self.all_values]

        # словарь template с баллами после обработки юс
        self.templates_scores = {
            elem: 0 for elem in self.names_templates if elem}

    def render_full_names_templates(self):
        names_templates = list(filter(None, self.names_templates))
        full_names_templates = list(
            filter(None, [element[1] for element in self.all_values]))
        return dict(zip(names_templates, full_names_templates))

    def clean_template_scores(self):
        self.templates_scores = {
            elem: 0 for elem in self.names_templates if elem}

    def __str__(self):
        final_str = f"Таблица «{self.name}»\n\n"
        final_str += f"Ссылка на таблицу: {self.sheet_link}\n"
        final_str += f"Лист: {self.sheet_name}\n\n"
        final_str += f"Статус проекта: " + \
            ("работает" if self.status else "не работает") + "\n"
        final_str += f"Таймер: " + \
            (self.timer if self.timer != '' else "нет") + "\n"
        return final_str

    def clean(self, text):
        # преобразуем слово к нижнему регистру
        text_low = text.lower()

        # проверка текста на наличие в нём кода эмодзи вк
        # принцип — если первый символ в тексте слова не буква, то это точно эмодзи!
        if text_low[0].isalpha() == False:
            return ""

        # описываем текстовый шаблон для удаления: "все, что НЕ (^) является буквой \w или пробелом \s"
        re_not_word = r'[^\w\s]'
        # заменяем в исходном тексте то, что соответствует шаблону, на пустой текст (удаляем)
        text_final = re.sub(re_not_word, '', text_low)
        # возвращаем очищенный текст
        return text_final

    def render_templates(self):
        template_dict = {}
        current_name = ""

        for i in range(len(self.buttons)):
            t_name = self.templates[i][0]  # название шаблона
            t_message = self.templates[i][1]  # сообщение для шаблона
            button = self.buttons[i]  # кнопка в шаблоне
            button = button.replace("'", '"')  # меняем кавычки
            button = json.loads(button)  # переводим строку в json

            if t_name != "":
                current_name = t_name
                template_dict[t_name] = {
                    "message": t_message,
                    "keyboard": {
                        "one_time": False,
                        "inline": False,
                        "buttons": []
                    }
                }

            template_dict[current_name]["keyboard"]["buttons"].append(
                button)  # добавляем кнопку к шаблону

        with open(f'{os.path.dirname(__file__)}/templates.json', 'w', encoding='utf-8') as write_file:
            json.dump(template_dict, write_file, ensure_ascii=False, indent=4)

        return template_dict

    def reshape_self_user_says(self):
        user_says = [us_word.split(", ")
                     for us_word in list(filter(None, self.user_says))]
        return dict(zip(list(filter(None, self.names_templates)), user_says))

    # РЕАЛИЗОВАТЬ ПОЛУЧЕНИЕ РАССТОЯНИЯ ЛЕВЕНШТЕЙНА МЕЖДУ СЛОВОМ ПОЛЬЗОВАТЕЛЯ И ЮС
    def get_levenstein_score(self, us_words, real_word):
        lst_levensteins = []
        for us_word in us_words:
            # применение алгоритма расстояния Дамерау-Левенштейна (использование транспозиции символов при обработке)
            value_levenstein = nltk.edit_distance(
                us_word, real_word, transpositions=True)
            lst_levensteins.append(value_levenstein)
        total_score = min(lst_levensteins)
        return total_score

    # РЕАЛИЗОВАТЬ ПОЛУЧЕНИЕ ПОТЕНЦИАЛЬНЫХ TEMPLATES ДЛЯ ВСЕХ СЛОВ ПОЛЬЗОВАТЕЛЯ

    def get_potential_templates(self, real_word):
        templates_scores = self.templates_scores
        user_says = self.reshape_self_user_says()
        for template, us_case in user_says.items():
            new_score_template = self.get_levenstein_score(us_case, real_word)
            templates_scores[template] += new_score_template
        sorted_templates_scores = sorted(
            templates_scores.items(), key=lambda item: item[1])
        self.templates_scores = dict(sorted_templates_scores)
        return [-1, sorted_templates_scores[0][0], sorted_templates_scores[1][0], sorted_templates_scores[2][0]]

    def search_in_one_word(self, user_word):
        for index, template_names in enumerate(self.user_says):
            names = template_names.lower().split(", ")
            if user_word in names:
                return [0, self.templates[index][0]]
        return self.get_potential_templates(user_word)

    # ПРОПИСАТЬ РУЧКАМИ, КАК БУДЕТ РАБОТАТЬ СИСТЕМА ПОТЕНЦИАЛЬНЫХ ЮС С ВЫВОДОМ INLINE КНОПОК !!!

    def search_user_says(self, user_sentence):
        user_words = [self.clean(
            word) for word in user_sentence.split() if self.clean(word) != ""]
        m = Mystem()
        if len(user_words) == 1:
            return self.search_in_one_word("".join(m.lemmatize(user_words[0])).rstrip('\n'))
        elif len(user_words) > 1:
            list_results = []
            indexes_0 = []
            list_template_values = []
            for index, word in enumerate(user_words):
                result = self.search_in_one_word(
                    "".join(m.lemmatize(word)).rstrip('\n'))
                list_results.append(result[0])
                if result[0] == 0:
                    indexes_0.append(index)
                list_template_values.append(result[1:])
            if 0 in list_results:
                # тогда мы точно говорим о том, что у нас есть точное совпадение

                # Проблема, которая остаётся — мы, заранее прописывая этот алгоритм, никогда не сможем узнать по точным
                # совпадениям, какое конкретно из них имел в виду пользователь, печатая текст боту

                # Как я поступлю в такой ситуации — будет выводиться сообщение, аналогичное ответу о том, что
                # точный ответ на текст пользователя не найден, но бот точно уверен в том, что пользователь сможет
                # найти ответ по inline-кнопкам с шаблонами, по которым найдено точное совпадение

                if len(indexes_0) == 1:
                    # если точное совпадение одно — выводим только его
                    self.templates_scores[list_template_values[indexes_0[0]][0]] = 0
                    return [0, list_template_values[indexes_0[0]][0]]
                elif len(indexes_0) == 2 and (list_template_values[indexes_0[0]] != list_template_values[indexes_0[1]]):
                    # если точных совпадений 2, и при этом они разные — то выводим 2
                    return [2, list_template_values[indexes_0[0]][0], list_template_values[indexes_0[1]][0]]
                elif len(indexes_0) == 2 and (list_template_values[indexes_0[0]] == list_template_values[indexes_0[1]]):
                    # прошлая ситуация, но сейчас templates одинаковые
                    return [0, list_template_values[indexes_0[0]][0]]
                else:
                    # если точных совпадений несколько — будем выводить топ-3

                    # кейс с повторными точными совпадениями мы избегаем циклом ниже, потому что обнуляем значение по
                    # одному и тому же ключу
                    for index_0 in indexes_0:
                        accurate_template = list_template_values[index_0][0]
                        self.templates_scores[accurate_template] = 0

                    sorted_templates_scores = sorted(
                        self.templates_scores.items(), key=lambda item: item[1])
                    self.templates_scores = dict(sorted_templates_scores)

                    # код, который более понятно показывает картину обработки данных словаря баллов template & scores
                    keys_sorted = list(self.templates_scores.keys())
                    values_sorted = list(self.templates_scores.values())

                    # если получается такая ситуация, что у нас оказалось 3 и более одинаковых по названию точных
                    # совпадения, то мы меняем индикатор на 0 и просто выводим первую пару
                    # в отсортированном словаре template & scores
                    if values_sorted[0] == 0 and (values_sorted[1] > 0):
                        return [0, keys_sorted[0]]

                    # кейс, когда 2 точных совпадения, частота встречи которых выше чем 1 раз
                    # тип когда эта пара точных совпадений встречается у нас больше чем 1 раз
                    elif values_sorted[0] == values_sorted[1] == 0 and (values_sorted[2] > 0):
                        return [2, keys_sorted[0], keys_sorted[1]]

                    # во всех остальных кейсах - выводим топ-3
                    else:
                        return [3, keys_sorted[0], keys_sorted[1], keys_sorted[2]]

            else:
                # если точных совпадений нет, то мы берём самое актуальное состояние template_scores
                # и выводим -1 вместе с последним результатом вызова функции potential_templates

                return [-1] + list_template_values[-1]

    def get_templates(self):
        try:
            with open(f"{os.path.dirname(__file__)}/templates.json", 'r', encoding='utf-8') as read_file:
                templates = json.load(read_file)
        except (FileNotFoundError, json.decoder.JSONDecodeError, TypeError):
            templates = {}

        return templates

# --------------------- ЭТАП ТЕСТИРОВАНИЯ ---------------------


faq = FAQ(name="Бот_FAQ_ПК",
          sheet_link="https://docs.google.com/spreadsheets/d/1WqtGUcJmr-fPrdV7VosDbUj-FxnCWbLlfayHWsImzAk/edit#gid=0",
          status=True)

print(faq.templates)
print()
# print(faq.render_full_names_templates())
# print()
# print(faq.reshape_self_user_says())
# print()
# print(faq.render_full_names_templates())
print()
start = time.time()
print(faq.search_user_says('Какие возрастные ограничения на балу ?'))
end = time.time()
print(f"Поиск юс обошёлся в {end - start} секунд")

# print()
# print(faq.search_user_says("сф - это who?"))

# Лемматизация - тесты
# m = Mystem()
# def dict_form(text):
#     return "".join(m.lemmatize(text)).rstrip('\n')
#
# print(dict_form("проектк"))
