# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import hashlib
import re


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy0209

    def process_item(self, item, spider):
        # dict_item = dict(item)
        if spider.name == 'hhru':
            item['min_salary'], item['max_salary'], item['currency'] = self.process_salary_hh(item['salary'])
            item['site'] = 'https://hh.ru'
        if spider.name == 'sjru':
            item['min_salary'], item['max_salary'], item['currency'] = self.process_salary_sj(item['salary'])
            item['site'] = 'https://www.superjob.ru'
        item['_id'] = hashlib.sha256(item['url'].encode()).hexdigest()
        collection = self.mongo_base[spider.name]
        collection.update_one({'_id': item['_id']}, {'$set': item}, upsert=True)
        return item

    def process_salary_hh(self, salary):
        salary_min, salary_max, salary_cur = None, None, None
        try:
            salary = salary.replace('\xa0', '')
            salary_list = salary.split(' ')

            if salary_list[0] == 'от':
                salary_min = int(salary_list[1])
                salary_list[0:2] = []
            if salary_list[0] == 'до':
                salary_max = int(salary_list[1])
                salary_list[0:2] = []
            if not salary_list[-1] == 'указана':
                salary_cur = salary_list[0]
        except:
            pass
        return salary_min, salary_max, salary_cur

    def process_salary_sj(self, salary):
        salary_min, salary_max, salary_cur = None, None, None
        try:
            if len(salary) == 0:
                return salary_min, salary_max, salary_cur

            salary_txt = ' '.join(salary)
            salary_txt = salary_txt.replace('\xa0', '').replace('  ', ' ')

            pattern = r'\d+'  # Ищем все числовые вхождения
            all_res = re.findall(pattern, salary_txt)

            if len(all_res) == 0:  # Если ничего не найдено, то зарплата не указана
                return salary_min, salary_max, salary_cur

            if len(all_res) == 2:  # Если найдено 2 значения, то указан минимум и максимум. Просто забираем их
                salary_min = int(all_res[0])
                salary_max = int(all_res[1])
            elif salary_txt[0:2] == 'от':  # Иначе остается вариант с одним значением. Если "от", то кладем в минимум
                salary_min = int(all_res[0])
            elif salary_txt[0:2] == 'до':  # Если "до", то кладем в максимум
                salary_max = int(all_res[0])
            else:
                salary_max = int(all_res[0])  # Иногда есть просто одно число - кладем в максимум
                # Если мы еще здесь, значит ЗП указана, а значит есть и валюта
            pattern = r'[^1-90]+$'  # Ищем набор символов в конце строки (кроме цифр)
            all_res = re.findall(pattern, salary_txt)
            if len(all_res) > 0:  # Если нашли такой набор, то это и есть валюта
                salary_cur = all_res[-1]  # На всякий случай возьмем последний из найденных наборов
        except:
            pass
        return salary_min, salary_max, salary_cur
