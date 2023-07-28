from flask import Flask, request, json
from random import choice, shuffle, randint
from geopy import geocoders
from vk_api.utils import get_random_id
from PIL import Image, ImageDraw, ImageFont
import vk_api
import requests
import bs4
import os
import re
import traceback
import json as JSON
import textwrap
import urllib.request

# Объект бота представляющий собой группу, от которой приходят сообщения
vk_session = vk_api.VkApi(
    token="токен группы")

# Объект бота личного аккаунта, позволяющий пользоваться большинством методов
vk_u = vk_api.VkApi(
    token="токен юзера админа группы")

with open(f'{os.path.dirname(__file__)}/intents_dataset.json', 'r', encoding='utf-8') as f:
    dataset_int = JSON.load(f)


def send_message(peer_id, message, keyboard=None, attachment_id=None):
    args = {
        "peer_id": peer_id,
        "message": message,
        "random_id": get_random_id()
    }
    if keyboard is not None:
        args['keyboard'] = json.JSONEncoder().encode(keyboard)
    elif attachment_id is not None:
        args["attachment"] = attachment_id
    vk_session.method('messages.send', args)


def prepare_mask(size, antialias=2):
    mask = Image.new('L', (size[0] * antialias, size[1] * antialias), 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
    return mask.resize(size, Image.ANTIALIAS)


def get_short_link(need_full_url):
    res = vk_session.method('utils.getShortLink', {'url': need_full_url})
    return res['short_url']


def geo_pos(city):
    city = "Москва" if city == "" else city
    geolocator = geocoders.Nominatim(user_agent="telebot")
    latitude = str(geolocator.geocode(city).latitude)
    longitude = str(geolocator.geocode(city).longitude)
    return latitude, longitude


def yandex_weather(latitude, longitude, token_yandex):
    url_yandex = 'https://api.weather.yandex.ru/v2/informers/?lat=' + \
        latitude + '&lon=' + longitude + '&[lang=ru_RU]'
    yandex_req = requests.get(
        url_yandex, headers={'X-Yandex-API-Key': token_yandex}, verify=False)

    conditions = {'clear': 'Ясно', 'partly-cloudy': 'Малооблачно', 'cloudy': 'Облачно с прояснениями',
                  'overcast': 'Пасмурно', 'drizzle': 'Морось', 'light-rain': 'Небольшой дождь', 'rain': 'Дождь',
                  'moderate-rain': 'Умеренно сильный', 'heavy-rain': 'Сильный дождь',
                  'continuous-heavy-rain': 'Длительный сильный дождь', 'showers': 'Ливень',
                  'wet-snow': 'Дождь со снегом',
                  'light-snow': 'Небольшой снег', 'snow': 'Снег', 'snow-showers': 'Снегопад', 'hail': 'Град',
                  'thunderstorm': 'Гроза', 'thunderstorm-with-rain': 'Дождь с грозой',
                  'thunderstorm-with-hail': 'Гроза с градом'}

    wind_dir = {'nw': 'северо-западного', 'n': 'северного', 'ne': 'северо-восточного', 'e': 'восточного',
                'se': 'юго-восточного', 's': 'южного', 'sw': 'юго-западного', 'w': 'западного', 'с': 'штиль'}

    yandex_json = JSON.loads(yandex_req.text)
    yandex_json['fact']['condition'] = conditions[yandex_json['fact']['condition']]
    yandex_json['fact']['wind_dir'] = wind_dir[yandex_json['fact']['wind_dir']]

    for parts in yandex_json['forecast']['parts']:
        parts['condition'] = conditions[parts['condition']]
        parts['wind_dir'] = wind_dir[parts['wind_dir']]

    pogoda = dict()
    params = ['condition', 'wind_dir', 'pressure_mm',
              'humidity', 'feels_like', 'wind_speed', 'wind_gust']

    pogoda['fact'] = dict()
    pogoda['fact']['temp'] = yandex_json['fact']['temp']
    pogoda['fact']['is_part'] = False

    for param in params:
        pogoda['fact'][param] = yandex_json['fact'][param]

    for parts in yandex_json['forecast']['parts']:
        pogoda[parts['part_name']] = dict()
        pogoda[parts['part_name']]['is_part'] = True
        pogoda[parts['part_name']]['temp'] = parts['temp_avg']
        pogoda[parts['part_name']]['temp_min'] = parts['temp_min']
        pogoda[parts['part_name']]['temp_max'] = parts['temp_max']
        for param in params:
            pogoda[parts['part_name']][param] = parts[param]

    pogoda['link'] = yandex_json['info']['url']
    return pogoda


def print_yandex_weather(dict_weather_yandex, city, is_fast):
    city = "Москва" if city == "" else city
    day = {'night': 'Ночью', 'morning': 'Утром',
           'day': 'Днём', 'evening': 'Вечером', 'fact': 'Сейчас'}
    total_string = 'Город ' + city.capitalize() + ', хмм...\nЯндекс говорит нам следующее:\n'
    total_link = get_short_link(dict_weather_yandex["link"])[8:]

    if is_fast:
        index = list(dict_weather_yandex.keys())[0]
        total_string += '\n\nСейчас t° = ' + str(dict_weather_yandex[index]["temp"]) + '°C, а за окном чувство ' + str(
            dict_weather_yandex[index]["feels_like"]) + '°C\n'
        total_string += '\nСостояние на небе ~ ' + \
            dict_weather_yandex[index]["condition"] + '\n'
        total_string += 'Скорость ветра = ' + \
            str(dict_weather_yandex[index]["wind_speed"]) + ' м/с '
        total_string += dict_weather_yandex[index]["wind_dir"] + \
            ' направления' + '\n'
        total_string += 'Порывы скорости = ' + \
            str(dict_weather_yandex[index]['wind_gust']) + ' м/с\n'
        total_string += '\nАтмосферное давление = ' + \
            str(dict_weather_yandex[index]['pressure_mm']) + ' мм.рт.ст.\n'
        total_string += 'Влажность воздуха ~ ' + \
            str(dict_weather_yandex[index]["humidity"]) + '%\n'

    else:

        for num, i in enumerate(dict_weather_yandex.keys()):
            if i != 'link':
                time_day = day[i]
                total_string += '\n' + str(num + 1) + ') ' + time_day + '\n'
                total_string += 't° => ' + str(dict_weather_yandex[i]["temp"]) + '°C, а за окном чувство ' + str(
                    dict_weather_yandex[i]["feels_like"]) + '°C)\n'

                if dict_weather_yandex[i]['is_part']:
                    total_string += 'Мин t° => ' + \
                        str(dict_weather_yandex[i]['temp_min']) + '°C, '
                    total_string += 'макс t° => ' + \
                        str(dict_weather_yandex[i]['temp_max']) + '°C\n'

                total_string += '\nСостояние на небе ' + \
                    dict_weather_yandex[i]["condition"] + '\n'
                total_string += 'Скорость ветра = ' + \
                    str(dict_weather_yandex[i]["wind_speed"]) + ' м/с '
                total_string += dict_weather_yandex[i]["wind_dir"] + \
                    ' направления' + '\n'
                total_string += 'Порывы скорости = ' + \
                    str(dict_weather_yandex[i]['wind_gust']) + ' м/с\n'
                total_string += 'Атмосферное давление = ' + \
                    str(dict_weather_yandex[i]['pressure_mm']) + ' мм.рт.ст.\n'
                total_string += 'Влажность воздуха ~ ' + \
                    str(dict_weather_yandex[i]["humidity"]) + '%\n'

    total_string += '\nА здесь ссылка на подробности: ' + total_link + '.'
    return total_string


def get_jokes():
    # список разделов анекдотов
    # 1 - свежие анекдоты
    # 2 - лучшие анекдоты прошлых лет
    # 3 - без политики
    # 4 - анекдоты за последний день
    # 5 - анекдоты за последнюю неделю
    # 6 - анекдоты за последний месяц
    # 7 - самые смешные с 1995 года
    # 8 - самые случайные анекдоты
    url = ["https://www.anekdot.ru/last/anekdot/", "https://www.anekdot.ru/best/anekdot/1106/",
           "https://www.anekdot.ru/last/non_burning/", "https://www.anekdot.ru/release/anekdot/day/",
           "https://www.anekdot.ru/release/anekdot/week/", "https://www.anekdot.ru/release/anekdot/month/",
           "https://www.anekdot.ru/release/anekdot/year/", "https://www.anekdot.ru/author-best/years/?years=anekdot",
           "https://www.anekdot.ru/random/anekdot/"]

    full_jokes = []
    for url_j in url:
        joke = requests.get(url_j)
        soup = bs4.BeautifulSoup(joke.text, 'html.parser')

        jokes = soup.select(".topicbox")
        full_jokes.extend([joke.find('div', {'class': 'text'}).get_text(strip=True, separator='\n')
                           for joke in jokes if joke.find('div', {'class': 'text'}) != None])

    new_jokes = list(set(full_jokes))
    shuffle(new_jokes)
    return choice(new_jokes)


def get_phrase():
    # список разделов афоризмов
    # 1 - свежие афоризмы
    # 2 - лучшие афоризмы прошлых лет
    # 3 - афоризмы за последнюю неделю
    # 4 - афоризмы за последний месяц
    # 5 - афоризмы за последний год
    # 6 - все афоризмы с 1998 года
    # 7 - самые случайные фразы
    url = ["https://www.anekdot.ru/last/aphorism/", "https://www.anekdot.ru/best/aphorism/1106/",
           "https://www.anekdot.ru/release/aphorism/week/", "https://www.anekdot.ru/release/aphorism/month/",
           "https://www.anekdot.ru/release/aphorism/year/", "https://www.anekdot.ru/author-best/years/?years=aphorism",
           "https://www.anekdot.ru/random/aphorism/"]

    full_phrases = []
    for url_ph in url:
        phrase = requests.get(url_ph)
        soup = bs4.BeautifulSoup(phrase.text, 'html.parser')

        phrases = soup.select(".topicbox")
        full_phrases.extend(
            [phrase.find('div', {'class': 'text'}).get_text(strip=True, separator='\n') for phrase in phrases if
             phrase.find('div', {'class': 'text'}) != None])

    new_phrases = list(set(full_phrases))
    shuffle(new_phrases)
    return choice(new_phrases)


def wrap_text(text):
    wrapper = textwrap.TextWrapper(width=35)
    word_list = wrapper.wrap(text=text)
    if len(word_list) > 4:
        word_list = word_list[:4]
    output = '\n'.join(word_list)
    return output


def shipper_people(members, tag_people=False):
    lst_names = [
        "@" + member["screen_name"] + " (" + member["first_name"] + " " + member["last_name"] + ")" if tag_people
        else member["first_name"] + " " + member["last_name"] for member in members]
    return f"Счастливые влюблённые: {choice(lst_names)} и {choice(lst_names)}"


app = Flask(__name__)

# Айдишники группы и альбома с цитатами
group_bot_id, album_id = ..., ...

# словарь со склонениями местоимений
mest_dict = {'я': 'ты', 'меня': 'тебя', 'мне': 'тебе', 'мной': 'тобой',
             'мною': 'тобою', 'мы': 'вы', 'нас': 'вас', 'нам': 'вам',
             'нами': 'вами', 'мой': 'твой', 'мое': 'твое', 'моё': 'твоё', 'моя': 'твоя',
             'мои': 'твои', 'наш': 'ваш', 'наше': 'ваше', 'наша': 'ваша', 'наши': 'ваши',
             'моего': 'твоего', 'моей': 'твоей', 'моих': 'твоих', 'моему': 'твоему',
             'моим': 'твоим', 'мою': 'твою', 'моими': 'твоими', 'моем': 'твоем',
             'моём': 'твоём', 'ты': 'я', 'тебя': 'меня', 'тебе': 'мне', 'тобой': 'мной',
             'тобою': 'мною', 'вы': 'мы', 'вас': 'нас', 'вам': 'нам',
             'вами': 'нами', 'твой': 'мой', 'твое': 'мое', 'твоё': 'моё', 'твоя': 'моя',
             'твои': 'мои', 'ваш': 'наш', 'ваше': 'наше', 'ваша': 'наша', 'ваши': 'наши',
             'твоего': 'моего', 'твоей': 'моей', 'твоих': 'моих', 'твоему': 'моему',
             'твоим': 'моим', 'твою': 'мою', 'твоими': 'моими', 'твоем': 'моем', 'твоём': 'моём'}


@app.route('/', methods=["POST"])  # Функция принимающая запросы
def main():
    try:
        # Преобразовываем json-ответ в питоновский объект
        data = json.loads(request.data)

        if data["type"] == "confirmation":  # Если событие — подтверждение группы
            return "код подтверждения"

        if data["type"] == "message_new":  # Если событие — сообщение
            message = data["object"]["message"]
            peer_id = message["peer_id"]
            from_id = message["from_id"]
            text = message["text"]

            try:

                if text.lower()[:7] == '~помощь':
                    reply = "Ну здарова, @id" + \
                        str(from_id) + " (дорогой!)\n\n"
                    reply += "\nПеред тобой сейчас разработка собственных рук @exponencial (прекрасного человека с чувством флекса!)"
                    reply += "\n\nКоманды у нас тут простые, чекай:"
                    reply += "\n\n~айди — вкидывает айди чата для бота (в лс присылает ваш айдишник)."
                    reply += "\n\n~подскажи {текст} — помогает тебе принять тяжёлое, но, порой, важное жизненное решение."
                    reply += "\n\n~цитата — делает тебя знаменитым среди Флексонычей и добавляет цитату в золотой сборник!"
                    reply += "\n\n~мысль {текст} — флекс-флексыч вкидывает тебе рандомную цитату, вот прям абсолютно, под твою ситуацию."
                    reply += "\n\n~топ {текст} — прилетает прекрасный топ-5 людей из чата по твоему тексту."
                    reply += "\n\n~вероятность, что {текст} — флекс-флексыч подумает и вкинет от себя вероятность твоего события."
                    reply += "\n\n~шипперить — присылает влюблённую парочку на вкус и цвет!"
                    reply += "\n\n~анекдот — происходит вкид кайфового анекдота для рофла :)"
                    reply += "\n\n~сократить {твоя ссылка} — в секунду сделаем для тебя короткую ссылку через сервис vk.cc."
                    reply += "\n\n~фраза — флекс-флексыч даёт тебе классную мысль на подумать!"
                    reply += "\n\n~фастпогода {название города} — ну что ж, всё просто: получаешь точненький прогноз погоды от самого Яндекса."
                    reply += "\n\n~фуллпогода {название города} — тэкс, ну тут вся подробная погода по городу на сейчас и на 2 периода вперёд (подробности узнаешь, когда введёшь командОчку)."
                    reply += "\n\nЕсли у тебя есть идея добавить что-то новое для своего брата Флекс-флексыча, то зафлекси это @exponencial (ему!)"
                    reply += "\n\nВсё чекнем и сделаем в лучшем виде, а пока... #флексим"

                    send_message(peer_id, reply)

                # раздел маленькой модели машинного обучения с реакцией на приветствие, прощание и благодарность

                if text.lower() in [elem.lower() for elem in dataset_int['hello']['examples']]:
                    reply = "@id" + str(from_id) + " (Дружище), " + \
                        choice(dataset_int['hello']['responses'])
                    send_message(peer_id, reply)

                elif text.lower() in [elem.lower() for elem in dataset_int['bye']['examples']]:
                    reply = "@id" + str(from_id) + " (Флексоныч), " + \
                        choice(dataset_int['bye']['responses'])
                    send_message(peer_id, reply)

                elif text.lower() in [elem.lower() for elem in dataset_int['thanks']['examples']]:
                    reply = choice(
                        dataset_int['thanks']['responses']) + " @id" + str(from_id) + " (Флексоныч)"
                    send_message(peer_id, reply)

                # тут типа раздел пошёл по обработке команд бота дорогого

                if text.lower()[:11] == "~фастпогода":
                    token_yandex = "токен яндекс апи по погоде"
                    city = text.lower().split(
                    )[-1] if len(text.lower().split()) > 1 else ""
                    latitude, longitude = geo_pos(city)
                    dict_ya_w = yandex_weather(
                        latitude, longitude, token_yandex)
                    reply = print_yandex_weather(dict_ya_w, city, is_fast=True)
                    send_message(peer_id, reply)

                elif text.lower()[:5] == "~айди":
                    send_message(peer_id, message=str(peer_id))

                elif text.lower()[:11] == "~фуллпогода":
                    token_yandex = "токен яндекс апи по погоде"
                    city = text.lower().split(
                    )[-1] if len(text.lower().split()) > 1 else ""
                    latitude, longitude = geo_pos(city)
                    dict_ya_w = yandex_weather(
                        latitude, longitude, token_yandex)
                    reply = print_yandex_weather(
                        dict_ya_w, city, is_fast=False)
                    send_message(peer_id, reply)

                elif text.lower()[:9] == "~подскажи":
                    send_message(peer_id, message=choice(["да", "нет", "хз"]))

                elif text.lower()[:7] == "~цитата":

                    try:
                        text_m = str(message['reply_message']['text'])
                        from_id_m = str(message['reply_message']['from_id'])
                    except:
                        from_id_m = str(message['fwd_messages'][0]['from_id'])
                        text_m = str(message['fwd_messages'][0]['text'])
                        for mes in message['fwd_messages'][1:]:
                            text_m += ', ' + mes['text']

                    text_list = textwrap.wrap(
                        text_m, width=28, replace_whitespace=False)
                    txt = "\n".join(text_list)

                    # это изначальная высота картинки, без текста
                    si = 333 + 30 * len(txt.split('\n'))
                    if int(from_id_m) < 0:
                        logo1 = vk_session.method(
                            "groups.getById", {"groups_ids": int(from_id_m)})
                        name = logo1[0]['name']
                    else:
                        logo1 = vk_session.method(
                            "users.get", {"user_ids": int(from_id_m), "fields": "photo_100"})
                        name = logo1[0]['first_name'] + \
                            " " + logo1[0]['last_name']

                    logo = urllib.request.urlopen(logo1[0]['photo_100']).read()

                    f = open(str(from_id_m) + '.png', 'wb')
                    f.write(logo)
                    f.close()

                    im = Image.new('RGB', (700, si))
                    font = ImageFont.truetype(
                        f'{os.path.dirname(__file__)}/HeliosExt.ttf', size=30)  # вызываем шкрифт

                    draw_text = ImageDraw.Draw(im)
                    draw_text.text(
                        (130, 20),
                        "Цитаты великих Флексонычей",
                        font=font,
                        fill="#ffffff"
                    )

                    draw_text = ImageDraw.Draw(im)
                    draw_text.text(
                        (90, 100),
                        "«" + txt + "»",
                        font=font,
                        fill="#ffffff"
                    )

                    draw_text = ImageDraw.Draw(im)
                    draw_text.text(
                        (130, si - 95),
                        "© " + name,
                        font=font,
                        fill="#ffffff"
                    )

                    image = Image.open(str(from_id_m) + ".png").convert("RGBA")
                    image.putalpha(prepare_mask((100, 100), 4))
                    im.paste(image, (20, si - 130), image)
                    im.save("logo.png")

                    # добавление фотографии с цитатой в альбом цитат группы
                    step_1 = vk_u.method('photos.getUploadServer', {
                                         "album_id": album_id, "group_id": group_bot_id})
                    step_2 = requests.post(step_1['upload_url'], files={
                                           'photo': open('logo.png', 'rb')}).json()
                    step_3 = vk_u.method('photos.save', {"album_id": album_id, "group_id": group_bot_id,
                                                         'photos_list': step_2['photos_list'],
                                                         'server': step_2['server'], 'hash': step_2['hash']})[0]
                    final_photo = 'photo{}_{}'.format(
                        step_3['owner_id'], step_3['id'])

                    os.remove('logo.png')
                    os.remove(str(from_id_m) + ".png")

                    send_message(peer_id, "#цитата", attachment_id=final_photo)

                elif text.lower()[:6] == "~мысль":
                    photos_list = vk_u.method("photos.get", {
                        "owner_id": -group_bot_id, "album_id": album_id
                    })["items"]
                    attachment_id = f"photo-{group_bot_id}_{choice(photos_list)['id']}"
                    send_message(peer_id, "#цитата",
                                 attachment_id=attachment_id)

                elif text.lower()[:8] == "~анекдот":
                    resp = get_jokes()
                    reply = "А поехали: \n\n" + resp
                    send_message(peer_id, reply)

                elif text.lower()[:6] == "~фраза":
                    resp = get_phrase()
                    reply = "В общем и целом: \n\n" + resp
                    send_message(peer_id, reply)

                elif text.lower()[:10] == "~сократить":
                    link_full = text.lower().split()
                    if link_full[-1][0] != '[':
                        reply = "Лови short URL: " + \
                            get_short_link(link_full[-1])[8:]
                    else:
                        param = "https://vk.com/" + \
                            link_full[-1].split("|")[-1][1:-1]
                        reply = "Лови short URL: " + get_short_link(param)[8:]
                    send_message(peer_id, reply)

                elif bool(re.search(r'~вероятность.*что.*', text.lower())):
                    result = ""
                    body = re.sub(r',', "", text)
                    lst_words = body.split(" ")
                    if lst_words[1].lower() == "того":
                        for word in lst_words[3:]:
                            if not word.lower() in mest_dict.keys():
                                result += word + " "
                            else:
                                result += mest_dict[word.lower()] + " "
                    elif lst_words[1].lower() == "что":
                        for word in lst_words[2:]:
                            if not word.lower() in mest_dict.keys():
                                result += word + " "
                            else:
                                result += mest_dict[word.lower()] + " "
                    else:
                        send_message(peer_id,
                                     "Неправильно введена твоя гипотеза. Попробуй использовать «того» или «что»")
                    result = result[0].replace(result[0], result[0].capitalize()) + result[
                        1:] + "с вероятностью " + str(
                        randint(0, 100)) + "%"
                    send_message(peer_id, result)

                if str(peer_id).startswith('20000'):

                    if text.lower()[:4] == "~топ":
                        body = text.lower()[4:]
                        res_stroke, res_top = f"Топ 5 {body} этого чата:\n\n", [
                        ]
                        result = vk_session.method(
                            "messages.getConversationMembers", {"peer_id": peer_id})
                        while len(res_top) != 5:
                            human = choice(result['profiles'])
                            if human not in res_top:
                                res_top.append(human)
                                res_stroke += f"{len(res_top)} - {human['last_name']} {human['first_name']}\n"
                        send_message(peer_id, message=res_stroke)

                    elif text.lower()[:10] == "~шипперить":
                        members = vk_session.method("messages.getConversationMembers", {
                                                    "peer_id": peer_id})['profiles']
                        final_mes = shipper_people(members, False)
                        send_message(peer_id, final_mes)

            except:
                send_message(peer_id,
                             "Упс, возник конфуз, по этому вопросу напиши @exponencial (ему) в лс. Всё решим :)")
                send_message(
                    '...', "Бро, тут возник конфуз, проверь, пеже:\n\n" + str(traceback.format_exc()))

    except:  # Если возникает ошибка, сообщаем об этом разработчику
        send_message(
            '...', "Бро, тут возник конфуз, проверь, пеже:\n\n" + str(traceback.format_exc()))
    return 'ok'
