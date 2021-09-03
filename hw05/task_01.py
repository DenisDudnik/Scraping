from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import selenium.common.exceptions as s_exceptions
import settings
import hashlib
import json
from pymongo import MongoClient


def mail_to_dict():
    mail_dict = {}
    subj = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'thread__subject'))).text
    date = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class = 'letter__date']"))).text
    sender = wait.until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'letter-contact')]"))).get_attribute(
        'title')
    text = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class = 'letter__body']"))).text
    mail_dict['subj'] = subj
    mail_dict['date'] = date
    mail_dict['sender'] = sender
    mail_dict['text'] = text
    mail_dict['_id'] = hashlib.sha1(json.dumps(mail_dict).encode()).hexdigest()
    return mail_dict


client = MongoClient('127.0.0.1', 27017)
db = client['mails']

mails = db.mails

LOGIN = settings.login
PASSWORD = settings.password

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(executable_path='./chromedriver.exe', options=chrome_options)

driver.get('https://mail.ru/')  # Загружаем всю страницу в driver

block_login = driver.find_element_by_id("mailbox")  # Ищем блок с окном логина и присваиваем его переменной block_login

elem = block_login.find_element_by_name("login")  # Ищем поле login в блоке логина block_login
elem.send_keys(LOGIN)

try:
    wait = WebDriverWait(block_login, 20)  # ищем кнопку "Ввести пароль" и ждем пока она станет активна
    elem = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='enter-password']")))
    elem.click()
except s_exceptions.TimeoutException:
    print('Кнопка Ввести пароль не появляется')  # Но иногда она не становится активной долго и тогда - медный таз

try:
    wait = WebDriverWait(block_login, 20)
    elem = wait.until(
        EC.element_to_be_clickable((By.NAME, "password")))  # Ищем поле password в блоке логина block_login
    elem.send_keys(PASSWORD)
    elem.send_keys(Keys.ENTER)
except s_exceptions.TimeoutException:
    print('Поле для пароля не появляется')  # Но иногда оно не становится активным долго и тогда - медный таз

# После логина

try:
    wait = WebDriverWait(driver, 20)  # Пробуем поймать момент когда строка на странице пробежит и содержимое загрузится
    wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, '//span[(@id = "bootscreenProgress" and @style = "display: none; width: 100%;")]')))
except s_exceptions.TimeoutException:
    print('Письма не появляются')  # Но иногда не получается и тогда - медный таз

mail_links = set()

while True:
    msg_count_control = len(mail_links)  # Запоминаем количество собранных ссылок на письма

    try:
        wait = WebDriverWait(driver, 40)  # Ждем когда письма станут кликабельны
        wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@class, "js-letter-list-item")]')))
    except:
        continue  # Если не дождались, просто продолжим цикл без перехода к следующим письмам
    else:  # Если дождались, то ищем блок писем и записываем его в block_mails (родитель первого письма)
        block_mails = driver.find_element_by_xpath('//a[contains(@class, "js-letter-list-item")]/..')
        mails_part = block_mails.find_elements_by_xpath('//a[contains(@class, "js-letter-list-item")]')
        for items in mails_part:
            if items:
                mail_links.add(items.get_attribute('href'))  # складываем ссылки в множество

        if msg_count_control == len(mail_links):  # Больше писем нет
            break

    actions = ActionChains(driver)  # переходим на последнее найденное письмо для загрузки следующей порции
    actions.move_to_element(mails_part[-1])  # но если использую не driver, а block_mails в этом месте,
    actions.perform()  # то потом получаю ошибки разные

for mail in mail_links:
    driver.get(mail)  # проходим по собранным ссылкам (их кстат меньше чем писем в ящике, так и не понял где косяк)

    try:
        wait = WebDriverWait(driver,
                             20)  # Пробуем поймать момент когда строка на странице пробежит и содержимое загрузится
        wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, '//span[(@id = "bootscreenProgress" and @style = "display: none; width: 100%;")]')))
        res = mail_to_dict()  # через функцию собраем данные из письма
    except s_exceptions.TimeoutException:
        print('Окно письма не загрузилось')  # Если окно не прогрузилось вовремя, то просто идем дальше по ссылкам
        continue
    else:
        mails.update_one({'_id': res['_id']}, {'$set': res}, upsert=True)  # Если все ОК, то сохраняяем письмо в базу
