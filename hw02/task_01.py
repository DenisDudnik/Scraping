# https://hh.ru/search/vacancy?area=113&clusters=true&enable_snippets=true&ored_clusters=true&schedule=remote&text=python
import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import pandas as pd

SAVE_TO_FILE_NAME = 'vacancies'
text_for_search = input('Введите вакансию, которую хотите найти: ')

try:
    user_max_page = int(input('Сколько страниц результатов обработать? '))
except:
    user_max_page = None

url = 'https://hh.ru'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                         '(KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}
params = {'area': 113, 'clusters': 'true', 'enable_snippets': 'true', 'ored_clusters': 'true', 'schedule': 'remote',
          'text': text_for_search, 'page': 0}

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

pprint(vacancies_list)

df = pd.DataFrame(vacancies_list)
print(df)
df.to_json(SAVE_TO_FILE_NAME + '.json', force_ascii=False)
df.to_csv(SAVE_TO_FILE_NAME + '.csv', index=False, encoding='utf-8', sep=';')
print(f'Результаты сохранены в файлы CSV и JSON под названием {SAVE_TO_FILE_NAME}')
