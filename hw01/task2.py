# 2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.

import conf
import requests
from pprint import pprint
import json

ACCESS_TOKEN = conf.TOKEN  # token загружаем из файла conf.py (для проверки первого else можно сломать token здесь)
SERVICE = 'https://api.vk.com/method/groups.search'  # адрес сервиса (для проверки второго else можно сломать адрес)
SERVICE_PARAMS = {  # устанавливаем параметры запроса
    'v': 5.54,
    'q': 'Global hearing',  # будем искать группы на тему Global Hearing
    'type': 'group',
    'count': 100,
    'access_token': ACCESS_TOKEN
}
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/92.0.4515.131 Safari/537.36'
}
FILE_N = 'res.json'  # указываем в какой файл сохранить данные от сервера

response = requests.get(SERVICE, params=SERVICE_PARAMS, headers=HEADERS)  # отправляем запрос

if response.ok:  # если сервер вернул статус 200
    response_json = response.json()  # преобразуем ответ в json-формат из текста
    if not response_json.get('error'):  # если запрос обработан без ошибок
        print(f"Найдено групп по сбору на операцию в Global Hearing: {response_json.get('response').get('count')}")
        for gr_num in range(response_json.get('response').get('count')):
            print(
                f"Ссылка: https:vk.com/{response_json.get('response').get('items')[gr_num].get('screen_name')} "
                f"Название группы: {response_json.get('response').get('items')[gr_num].get('name')}")
    else:  # если запрос обработан с ошибками
        pprint(response_json)
    with open(FILE_N, 'w', encoding='utf-8') as f:
        json.dump(response_json, f, ensure_ascii=False)  # сохраняем ответ сервера в файл в человекочитаемой кодировке
    print(f'Ответ сервера сохранен в файл {FILE_N}')
else:  # если сервер вернул статус, отличный от 200
    print(f'Сервер вернул статус {response.status_code}:')
    print(response.text)
