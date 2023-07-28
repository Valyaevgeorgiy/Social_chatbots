import json

def add_database():

    with open('data/db.json', 'r', encoding='utf-8') as file:
        all_data = json.load(file)

    for project in all_data.keys():
        print(project)
        print(type(all_data[project]['status']), end='\t|\t')
        print(all_data[project]['status'])

        new_value_status = True if all_data[project]['status'] == 'True' else False

        print(type(new_value_status), end='\t|\t')
        print(new_value_status)

    #for key, value in all_data['Осенний Бал'].items():
    #    print(f"{key}: {value}")

if __name__ == "__main__":
    print("Hello, world!")


"""
АЛГОС ДЛЯ нахождения дат отзывов с учётом объединения ячеек заголовков столбцов

# Общий случай - по отзыву в день
                    if n_rev_day == 1:
                        list_dates = [self.base_dates[index] for index in list_ind_dates]

                    # Обработка события - 2 или 3 отзыва за 1 день
                    if n_days == 1:
                        if n_rev_day == 2 or n_rev_day == 3:
                            list_dates = [self.base_dates[0] for _ in list_ind_dates]

                    # Обработка события - 2 или 3 отзыва в 2 дня
                    elif n_days == 2:
                        if n_rev_day == 2:
                            list_dates = [self.base_dates[0] if (index < 2) else
                                          self.base_dates[1] for index in list_ind_dates]
                        elif n_rev_day == 3:
                            list_dates = [self.base_dates[0] if (index < 3) else
                                          self.base_dates[1] for index in list_ind_dates]

                    # Обработка события - 2 или 3 отзыва в 3 дня
                    elif n_days == 3:
                        if n_rev_day == 2:
                            list_dates = [self.base_dates[0] if (index < 2) else
                                          self.base_dates[1] if (2 <= index < 4) else
                                          self.base_dates[2] for index in list_ind_dates]
                        elif n_rev_day == 3:
                            list_dates = [self.base_dates[0] if (index < 3) else
                                          self.base_dates[1] if (3 <= index < 6) else
                                          self.base_dates[2] for index in list_ind_dates]

                    # Обработка события - 2 или 3 отзыва в 4 дня
                    elif n_days == 4:
                        if n_rev_day == 2:
                            list_dates = [self.base_dates[0] if (index < 2) else
                                          self.base_dates[1] if (2 <= index < 4) else
                                          self.base_dates[2] if (4 <= index < 6) else
                                          self.base_dates[3] for index in list_ind_dates]
                        elif n_rev_day == 3:
                            list_dates = [self.base_dates[0] if (index < 3) else
                                          self.base_dates[1] if (3 <= index < 6) else
                                          self.base_dates[2] if (6 <= index < 9) else
                                          self.base_dates[3] for index in list_ind_dates]

                    # Обработка события - 2 или 3 отзыва в 5 дней
                    elif n_days == 5:
                        if n_rev_day == 2:
                            list_dates = [self.base_dates[0] if (index < 2) else
                                          self.base_dates[1] if (2 <= index < 4) else
                                          self.base_dates[2] if (4 <= index < 6) else
                                          self.base_dates[3] if (6 <= index < 8) else
                                          self.base_dates[4] for index in list_ind_dates]
                        elif n_rev_day == 3:
                            list_dates = [self.base_dates[0] if (index < 3) else
                                          self.base_dates[1] if (3 <= index < 6) else
                                          self.base_dates[2] if (6 <= index < 9) else
                                          self.base_dates[3] if (9 <= index < 12) else
                                          self.base_dates[4] for index in list_ind_dates]

                    # Обработка события - 2 или 3 отзыва в 6 дней
                    elif n_days == 6:
                        if n_rev_day == 2:
                            list_dates = [self.base_dates[0] if (index < 2) else
                                          self.base_dates[1] if (2 <= index < 4) else
                                          self.base_dates[2] if (4 <= index < 6) else
                                          self.base_dates[3] if (6 <= index < 8) else
                                          self.base_dates[4] if (8 <= index < 10) else
                                          self.base_dates[5] for index in list_ind_dates]
                        elif n_rev_day == 3:
                            list_dates = [self.base_dates[0] if (index < 3) else
                                          self.base_dates[1] if (3 <= index < 6) else
                                          self.base_dates[2] if (6 <= index < 9) else
                                          self.base_dates[3] if (9 <= index < 12) else
                                          self.base_dates[4] if (12 <= index < 15) else
                                          self.base_dates[5] for index in list_ind_dates]


ФУНКЦИЯ СЧИТЫВАНИЯ ВСЕХ ТАБЛИЧЕК ИЗ БАЗЫ 

def print_info_projects():
    with open('data/db.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    projects = list(data.keys())
    for project in projects:
        # обрабатываем статус проекта (типизация из строкового в булевский)
        new_value_status = True if data[project]['status'] == 'True' else False
        data[project]['status'] = new_value_status

        if data[project]['link'].startswith('типа'):
            final_str = "\nПроект " + project + "\n"
            final_str += "Ссылка на таблицу: отсутствует, её типа нет\n"
            new_status = "работает" if data[project]['status'] else "не работает"
            final_str += "Статус проекта: " + new_status + "\n"
            final_str += "Список факаперов слева направо пуст, поскольку нет ссылки на таблицу отзывов, ага-ага."
            print(final_str)
        else:

            # ДЕЛАТЬ ЭТО при каждой проверке отзывов
            project_class = Project(name=project, link=data[project]['link'], sheet_name=data[project]['sheet_name'])
            print(project_class)

БАЗА

{
    "Осенний Бал": {
        "link": "типа https://docs.google.com/spreadsheets/d/1Ep_X2yHuiR-aqyLctLWIMKvY-TgR7CneqZZZmmeym-U/edit#gid=908754566",
        "sheet_name": "Отзывы",
        "status": "True"
    },
    "ФКЛ": {
        "link": "типа ссылка на ФКЛ",
        "sheet_name": "Отзывы",
        "status": "True"
    },
    "Урбан Фест": {
        "link": "https://docs.google.com/spreadsheets/d/1_KSzw7ly_13kL1HlIRq6LjG6JBMEheUO0ZwT-wlxBnc/edit#gid=0",
        "sheet_name": "Отзывы",
        "status": "False"
    },
    "Твоя Москва": {
        "link": "https://docs.google.com/spreadsheets/d/1F0-TwqfS6qVhnshHwBsXEM7JTqWCzMNnJb12-KO0ROc/edit#gid=712283393",
        "sheet_name": "Отзывы",
        "status": "False"
    }
}

ГЛАВНЫЙ КОД

        while True:

        try:
            with open('data/db.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                name_projects = list(data.keys())
        except (FileNotFoundError, json.decoder.JSONDecodeError, TypeError) as e:
            if_base_null = True

        command = input("Введи любую команду => ").split()
        try:
            if len(command) > 1:

                # 1 команда "!добавить {название проекта} {ссылка на табличку}"
                if command[0].lower() == "!добавить":
                    name, link = ' '.join(command[1:-1]), command[-1]
                    if if_base_null:
                        add_to_database(name=name, link=link, base_null=if_base_null)
                        if_base_null = False
                    else:
                        add_to_database(name=name, link=link, base_null=if_base_null)

                # 2 команда "!проверка {название проекта}"
                elif command[0] == "!проверка":
                    name = ' '.join(command[1:])
                    if name in name_projects:
                        link, sheet_name = data[name]['link'], data[name]['sheet_name']
                        project = Project(name=name, link=link, sheet_name=sheet_name)
                        print(project)
                    else:
                        print("Такого проекта не существует в базе, попробуйте снова!")

                # 3 команда "!рассылка {название проекта}"
                elif command[0] == "!рассылка":
                    name = ' '.join(command[1:])
                    if name in name_projects:
                        link, sheet_name = data[name]['link'], data[name]['sheet_name']
                        project = Project(name=name, link=link, sheet_name=sheet_name)
                        project.remind_feedbacks()
                    else:
                        print("Такого проекта не существует в базе, попробуйте снова!")

                else:
                    print("Такой команды нет в списке, попробуй написать что-то из этого:")
                    print("1 команда !добавить {название проекта} {ссылка на табличку}")
                    print("2 команда !проверка {название проекта}")
                    print("3 команда !рассылка {название проекта}")
            else:
                print("Такой команды нет в списке, попробуй написать что-то из этого:")
                print("1 команда !добавить {название проекта} {ссылка на табличку}")
                print("2 команда !проверка {название проекта}")
                print("3 команда !рассылка {название проекта}")

                # моя часть - это можно удалить в финальном коде
                if_exit = input("Желаешь закончить проверку? (да/нет) => ").lower()
                if if_exit == 'да':
                    break
        except:
            print("Возникла ошибка в процессе работы бота, код ошибки: ")
            print(traceback.format_exc())

"""