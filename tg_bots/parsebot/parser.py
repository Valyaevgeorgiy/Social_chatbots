import aiohttp
import asyncio
import time
from bs4 import BeautifulSoup
from datetime import datetime


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
                    for key, value in phones_dict.items():
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
