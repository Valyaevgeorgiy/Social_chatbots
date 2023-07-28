from flask import Flask, request, json
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import datetime as dt
import traceback
import time
import message
import random

vk = vk_api.VkApi(token="токен группы")
# vk_u = vk_api.VkApi(token="токен юзера админа группы")

app = Flask(__name__)

# функция прочтения json-файлика с кнопками при открытии нового раздела


def read_json_button(path):
    with open(path, 'r', encoding='utf-8') as file:
        keyboard = json.load(file)
        file.close()
    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    return str(keyboard.decode('utf-8'))


@app.route('/', methods=["POST"])
def main():
    try:
        try:
            data = json.loads(request.data)
            if data["type"] == "confirmation":
                return "код подтверждения соединения с сервером"

            elif data["type"] == "message_new":
                object_0 = data["object"]["message"]
                object1 = data["object"]["client_info"]

                id_peer = object_0["peer_id"]
                body = object_0["text"]
                from_id = str(object_0['from_id'])
                keyboard_work = object1["keyboard"]

                if keyboard_work == 1:

                    if body.lower() == "!айди":
                        vk.method("messages.send", {
                                  "peer_id": id_peer, "message": f"Айдишник этого чата => {id_peer}", "random_id": time.time()})

                    elif str(id_peer)[:-2] != "20000000":
                        if body.lower() == "начать" or object_0["payload"] == '{"command":"start"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.start, "keyboard": read_json_button(
                                '../start.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"student"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.student, "keyboard": read_json_button(
                                '../student.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"39"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.problema_vopros, "random_id": time.time()})
                            user_name = vk.method(
                                "users.get", {"user_ids": id_peer, "name_case": "Nom"})
                            notification = "@id"+from_id + \
                                " ("+user_name[0]['first_name']+" "+user_name[0]['last_name'] + \
                                ") нажал <<"+body+">>\nПриготовьтесь отвечать: vk.com/gim27590309"
                            vk.method("messages.send", {
                                      "peer_id": id_chat_studkomfort, "message": notification, "random_id": random.randint(1, 2147483647)})

                        elif object_0["payload"] == '{"button":"40"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.abitura, "keyboard": read_json_button(
                                '../abitura.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"2"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.maga, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"4"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.kontakt, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"5"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.social, "keyboard": read_json_button(
                                '../social.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"3"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.study, "keyboard": read_json_button(
                                '../study.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"80"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.zadolg, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"81"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.brs, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"7"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.voen_kaf, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"8"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.obschaga, "keyboard": read_json_button(
                                '../obschaga.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"9"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.faculty_life, "keyboard": read_json_button(
                                '../faculty_life.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"11"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.stud_sovet, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"12"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.sport, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"13"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.meropriyatiya, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"14"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.grafiki_raspisanie, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"15"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.social, "keyboard": read_json_button(
                                '../social.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"67"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.social, "keyboard": read_json_button(
                                '../abitura_faculty_life.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"68"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.abitura, "keyboard": read_json_button(
                                '../abitura.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"16"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.zasel, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"17"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.oplata_tr_onl, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"18"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.oko, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"19"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.adres_stoim, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"20"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.balt, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"21"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.galushka, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"23"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.transfer, "keyboard": read_json_button(
                                '../transfer.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"24"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.nauchnaya_rabota, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"25"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.scholarship, "keyboard": read_json_button(
                                '../scholarship.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"26"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.payment_discounts, "keyboard": read_json_button(
                                '../payment_discounts.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"28"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.megdy_napravleniyami, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"29"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.platka_budget, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"30"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.study, "keyboard": read_json_button(
                                '../study.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"31"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.payment, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"32"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.discounts, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"34"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.gas, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"35"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.pgas, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"36"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.gss, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"37"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.prav_msk, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"42"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.postuplenie, "keyboard": read_json_button(
                                '../postuplenie.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"43"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.virtual_tour, "keyboard": read_json_button(
                                '../virtual_tour.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"430"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.virtual_tour, "keyboard": read_json_button(
                                '../virtual_tour(student).json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"44"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.napravleniya, "keyboard": read_json_button(
                                '../napravleniya.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"46"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.dates_admission, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"47"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.respite_army, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"48"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.after_college, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"49"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.documents, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"50"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.abitura, "keyboard": read_json_button(
                                '../abitura.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"51"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.pm, "keyboard": read_json_button(
                                '../pm.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"52"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.pi, "keyboard": read_json_button(
                                '../pi.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"53"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.bi, "keyboard": read_json_button(
                                '../bi.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"54"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.ib, "keyboard": read_json_button(
                                '../ib.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"56"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.pm_disciplines, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"57"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.pm_profession, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"59"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.pi_disciplines, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"60"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.pi_profession, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"62"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.bi_disciplines, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"63"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.bi_profession, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"65"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.ib_disciplines, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"66"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.ib_profession, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"73"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.clubs, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"58"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.napravleniya, "keyboard": read_json_button(
                                '../napravleniya.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"74"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": tton(
                                '../lgoti.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"75"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.platnoeobuchenie, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"79"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.postupleniedop, "keyboard": read_json_button(
                                '../postupleniedop.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"76"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.bvi, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"77"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.celevoe, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"78"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.indivdost, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"82"}':
                            vk.method("messages.send", {"peer_id": id_peer, "message": message.info_zadol_brs, "keyboard": read_json_button(
                                '../ball_zadolgnost.json'), "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"83"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.poleznoe_ycheba, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"80"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.zadolg, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"81"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.brs, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"84"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.map_of_corp, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"85"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.chto_ryadom, "random_id": time.time()})

                        elif object_0["payload"] == '{"button":"86"}':
                            vk.method("messages.send", {
                                      "peer_id": id_peer, "message": message.benefits_for_students, "random_id": time.time()})

                elif keyboard_work == 0:
                    vk.method("messages.send", {
                              "peer_id": id_peer, "message": "К сожалению, на вашей версии VK не поддерживаются меню-клавиатуры ботов...\nВозможное решение: воспользуйтесь другим, более новым устройством.", "random_id": time.time()})

        except KeyError:
            user_name = vk.method(
                "users.get", {"user_ids": id_peer, "name_case": "Nom"})
            da = otv[dt.datetime.today().isoweekday() - 1]
            notification = "@id"+from_id+" ("+user_name[0]['first_name']+" "+user_name[0]['last_name']+") написал в группу сообщение:\n\n<<"+body+">>\n\nОтветственные за сегодня: "+str(
                da)+" \nЧеловек ждёт ответа: vk.com/gim27590309?sel="+from_id+"\nСсылка на сообщения группы: vk.com/gim27590309"
            vk.method("messages.send", {"peer_id": id_chat_studkomfort,
                      "message": notification, "random_id": random.randint(1, 2147483647)})
    except:
        vk.method("messages.send", {"peer_id": '...', "message": traceback.format_exc(
        ), "random_id": random.randint(1, 2147483647)})
        vk.method("messages.send", {"peer_id": '...', "message": traceback.format_exc(
        ), "random_id": random.randint(1, 2147483647)})

    return "ok"
