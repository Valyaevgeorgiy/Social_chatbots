import aiohttp
import asyncio
import time
from bs4 import BeautifulSoup
from datetime import datetime

# здесь ниже функционал, который находит одинаковые по структуре цифр номера телефонов и их подчёркивает!

# async def count_shared_digits(number1, number2):
#     dupl_digits = 0
#     for ind in range(len(number1)):
#         if number1[ind] == number2[ind]:
#             dupl_digits += 1
#         else:
#             break
#     return dupl_digits


# async def check_dupls(list_numbers):
#     for ind in range(len(list_numbers)):
#         now_number = list_numbers[ind]
#         for number in list_numbers:
#             if now_number[5:] == number[5:]:
#                 # пропускаем тот номер из списка, с которого и начали сравнение
#                 continue
#             else:
#                 if await count_shared_digits(now_number[5:], number[5:]) >= 3:
#                     print(now_number, number)
#                     print()
#                     ind_dupl_num = list_numbers.index(number)
#                     # выделение группы одинаковых номеров уникальной разметкой HTML
#                     if "<u>" not in list_numbers[ind] and "<u>" not in list_numbers[ind_dupl_num]:
#                         list_numbers[ind] = "<u>"+list_numbers[ind]+"</u>"
#                         list_numbers[ind_dupl_num] = "<u>"+number+"</u>"
#                 else:
#                     continue
#     return list_numbers

# -------------------------------------------------------------------------------------------

# далее уже функционал, который находит в номерах повторение одних и тех же цифр (2 и более раз)!

async def check_dupls(list_numbers):
    for ind in range(len(list_numbers)):
        number = list_numbers[ind][5:9] + list_numbers[ind][10:]
        # number = "99675679"
        for ind_d in range(len(number)):
            if ind_d < (len(number) - 1):
                now_digit = number[ind_d]
                if now_digit == number[ind_d+1]:
                    # выделяем номер подчёркиванием!
                    list_numbers[ind] = "<u>"+list_numbers[ind]+"</u>"
                    break
    return list_numbers


async def get_sales():
    time.sleep(5)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://fragment.com/numbers?filter=sale") as response:
                if response.status == 200:
                    html_content = BeautifulSoup(await response.text(), "html.parser")
                    phone_top10 = html_content.find_all(
                        'tr', class_='tm-row-selectable')[:10]

                    phones_dict = {}
                    for phone_tag in phone_top10:
                        number_tag = phone_tag.find(
                            'div', class_='table-cell-value tm-value')
                        number_text = number_tag.get_text()

                        sale_tag = phone_tag.find(
                            'div', class_='table-cell-value tm-value icon-before icon-ton')
                        sale_text = sale_tag.get_text()

                        phones_dict[number_text] = sale_text

                    # Получаем текущее время и форматируем
                    current_time = datetime.now()
                    formatted_time = current_time.strftime("%d.%m.%Y %H:%M:%S")

                    top10_list = "Данные на " + str(formatted_time) + "\n"

                    ind = 0
                    top10_numbers, top10_sales = await check_dupls(
                        list(phones_dict.keys())), list(phones_dict.values())
                    for key, value in dict(zip(top10_numbers, top10_sales)).items():
                        ind += 1
                        top10_list += f'{ind}. {key} ({value} TON)\n'

                    return phones_dict, top10_list

                else:
                    return {}, "Failed to retrieve the web page. Status code: " + str(response.status_code)
    except aiohttp.client_exceptions.ServerDisconnectedError as e:
        return {}, "Произошёл разрыв соединения с сервером в течение запроса. Попробуйте ещё раз!"


async def main():
    await get_sales()

if __name__ == "__main__":
    asyncio.run(main())
