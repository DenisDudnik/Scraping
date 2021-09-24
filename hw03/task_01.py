# https://hh.ru/search/vacancy?area=113&clusters=true&enable_snippets=true&ored_clusters=true&schedule=remote&text=python
import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
from pymongo import MongoClient

text_for_search = input('Введите вакансию, которую хотите найти: ')

try:
    user_max_page = int(input('Сколько страниц результатов обработать? '))
except:
    user_max_page = None

url = 'https://hh.ru'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                         '(KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}
params = {'area': 113, 'clusters': 'true', 'enable_snippets': 'true', 'ored_clusters': 'true', 'schedule': 'remote',
          'text': text_for_search, 'items_on_page': 20, 'page': 0}

response = requests.get(url + '/search/vacancy', params=params, headers=headers)
soup = bs(response.text, 'html.parser')

max_page = 1

pages = soup.find_all('a', {'data-qa': 'pager-page'})

if len(pages) > 0:
    max_page_block = pages[-1].children
    max_page = int(list(max_page_block)[-1].text)

if user_max_page:
    max_page = min(user_max_page, max_page)

vacancies_list = []

for page in range(max_page):
    params['page'] = page
    print(f'Working... Page {page}')

    response = requests.get(url + '/search/vacancy', params=params, headers=headers)
    soup = bs(response.text, 'html.parser')
    vacancies = soup.find_all('div', {'class': 'vacancy-serp-item'})

    for vacancy in vacancies:
        vacancy_data = {}

        info = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
        title = info.text
        link = info.get('href')
        from_site = url

        info = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        salary = [None, None, None]
        try:
            salary_text = info.text.replace('\u202f', '')
            salary_list = salary_text.split(' ')

            if salary_list[0] == 'от':
                salary[0] = int(salary_list[1])
            elif salary_list[0] == 'до':
                salary[1] = int(salary_list[1])
            else:
                salary[0] = int(salary_list[0])
                salary[1] = int(salary_list[2])

            salary[2] = salary_list[-1]
        except:
            salary[0] = None
            salary[1] = None
            salary[2] = None

        vacancy_data['title'] = title
        vacancy_data['link'] = link
        vacancy_data['salary'] = salary
        vacancy_data['url'] = url

        vacancies_list.append(vacancy_data)

vacancy_data = {  # Вакансия для тестирования случая, когда ссылка совпадает, а содержимое
    'title': 'test9',  # меняется.
    'link': 'testlink',  # Первый проход программы запустить с одним содержимым.
    'salary': [888887, 999999, 'ru'],  # Остальные проходы - с измененным
    'url': 'urli'  # Ссылку не менять для теста
}
vacancies_list.append(vacancy_data)  # Добавление тестовой вакансии в конец списка собранных

client = MongoClient('127.0.0.1', 27017)
db = client['vacancies']

actual_vacancies = db.actual_vacancies
history_vacancies = db.history_vacancies

# actual_vacancies.delete_many({})  #   Если нужно очистить таблицу перед вставкой
# history_vacancies.delete_many({}) #   Если нужно очистить таблицу перед вставкой

for vacancy in vacancies_list:

    doc = {
        'title': vacancy['title'],
        'link': vacancy['link'],
        'salary_min': vacancy['salary'][0],
        'salary_max': vacancy['salary'][1],
        'salary_currency': vacancy['salary'][2],
        'url': vacancy['url']
    }
    if actual_vacancies.count_documents(doc.copy()) == 0:  # Если содержимое вакансии отсутствует в актуальном
        history_vacancies.insert_one(doc.copy())  # добавить в историческую
        if actual_vacancies.count_documents({'link': doc['link']}) > 0:  # Если вакансия с такой ссылкой есть
            actual_vacancies.replace_one({'link': doc['link']}, doc.copy())  # обновить в актуальных
        else:
            actual_vacancies.insert_one(doc.copy())  # добавить в актуальную

for item in actual_vacancies.find({}):
    pprint(item)

salary_min = int(input('Какую минимальную зарплату будем искать? '))
for item in actual_vacancies.find(
        {'$or': [{'salary_min': {'$gte': salary_min}}, {'salary_max': {'$gte': salary_min}}]}):
    pprint(item)
