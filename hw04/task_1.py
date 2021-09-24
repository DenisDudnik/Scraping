from lxml import html
from pprint import pprint
import requests
from pymongo import MongoClient
import hashlib

URL = 'https://lenta.ru/'
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}

response = requests.get(URL, headers=header)

dom = html.fromstring(response.text)

items = dom.xpath("//section[contains(@class, 'b-top7-for-main')]/div[@class='span4']/div[@class='first-item']/h2|"
                  "//section[contains(@class, 'b-top7-for-main')]/div[@class='span4']/div[@class='item']")

items_list = []
for item in items:
    items_data = {}
    topic = item.xpath("./a/text()")[0].replace('\xa0', ' ')
    link = item.xpath("./a/@href")[0]
    if link[0] == '/':
        link = f'{URL}{link}'
    time = item.xpath(".//time[@class='g-time']//@datetime")[0]

    items_data['topic'] = topic
    items_data['link'] = link
    items_data['time'] = time
    items_data['_id'] = hashlib.sha256(link.encode()).hexdigest()

    items_list.append(items_data)

client = MongoClient('127.0.0.1', 27017)
db = client['vacancies']

news = db.news

# news.delete_many({})  #   Если нужно очистить таблицу перед вставкой

for item in items_list:
    doc = {
        '_id': item['_id'],
        'topic': item['topic'],
        'link': item['link'],
        'time': item['time']
    }

    news.update_one({'_id': doc['_id']}, {'$set': doc}, upsert=True)

for idx in news.find({}):
    pprint(idx)
