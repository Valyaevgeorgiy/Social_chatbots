import vk_api
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

with open('key.txt', 'r') as f:
    key = f.readline()

vk_session = vk_api.VkApi(token=key)  # ключ доступа из группы
longpoll = VkBotLongPoll(vk_session, "...")  # id группы


if __name__ == '__main__':
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
            peer_id = event.object.message['from_id']
            text = event.object.message['text']
            print('Новое сообщение:', text)

            if text.lower() == "привет":
                reply = 'Привет'
                vk_session.method('messages.send', {
                    'peer_id': peer_id,
                    'message': reply,
                    'random_id': get_random_id()
                })

            if text.lower() == "пока":
                reply = 'До свидания'
                vk_session.method('messages.send', {
                    'peer_id': peer_id,
                    'message': reply,
                    'random_id': get_random_id()
                })
