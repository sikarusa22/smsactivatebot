from telebot import types
import sqlite3
import telebot
import os
import settings
import random
import requests
import json
import datetime
import menu
import time
import config

import traceback


admin_sending_messages_dict = {}
coin_game_dict = {}
admin_buttons_dict = {}
admin_set_price = {}


class Admin_set_price:
    def __init__(self, user_id):
        self.user_id = user_id
        self.service = None
        self.country = None
        self.price = None


class AdminButtons:
    def __init__(self, user_id):
        self.user_id = user_id
        self.name = None
        self.info = None
        self.photo = None


class Coin_game:
    def __init__(self, user_id):
        self.user_id = user_id
        self.bet = None
        self.side = None


class Admin_sending_messages:
    def __init__(self, user_id):
        self.user_id = user_id
        self.text = None
        self.photo = None
        self.type_sending = None
        self.date = None


class Buy:
    def __init__(self, user_id):
        self.user_id = user_id
        self.code = None


class GiveBalance:
    def __init__(self, login):
        self.login = login
        self.balance = None
        self.code = None


class Product:
    def __init__(self, user_id):
        self.user_id = user_id
        self.product = None
        self.section = None
        self.price = None
        self.amount = None
        self.amount_MAX = None
        self.code = None


class AddProduct:
    def __init__(self, section):
        self.section = section
        self.product = None
        self.price = None
        self.info = None


class DownloadProduct:
    def __init__(self, name_section):
        self.name_section = name_section
        self.name_product = None


def first_join(user_id, name, code):
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()
    row = cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"').fetchall()

    ref_code = code
    if ref_code == '':
        ref_code = 0
    
    if len(row) == 0:
        cursor.execute(f'INSERT INTO users VALUES ("{user_id}", "{name}", "{datetime.datetime.now()}", "{user_id}", "{ref_code}", "0")')
        conn.commit()

        return True, ref_code
        
    return False, 0


def admin_info():
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()
    row = cursor.execute(f'SELECT * FROM users').fetchone()

    current_time = str(datetime.datetime.now())

    amount_user_all = 0
    amount_user_day = 0
    amount_user_hour = 0

    while row is not None:
        amount_user_all += 1
        if row[2][:-15:] == current_time[:-15:]:
            amount_user_day += 1
        if row[2][:-13:] == current_time[:-13:]:
            amount_user_hour += 1

        row = cursor.fetchone()

    msg = f"""
❕ Информаци о пользователях:

❕ За все время - {amount_user_all}
❕ За день - {amount_user_day}
❕ За час - {amount_user_hour}

{admin_profit_info()}
"""

    return msg

def check_payment(user_id):
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()
    try:
        session = requests.Session()
        session.headers['authorization'] = 'Bearer ' + config.config("qiwi_token")
        parameters = {'rows': '10'}
        h = session.get(
            'https://edge.qiwi.com/payment-history/v1/persons/{}/payments'.format(config.config("qiwi_number")),
            params=parameters)
        req = json.loads(h.text)
        result = cursor.execute(f'SELECT * FROM check_payment WHERE user_id = {user_id}').fetchone()
        comment = result[1]

        for i in range(len(req['data'])):
            if comment in str(req['data'][i]['comment']):
                if str(req['data'][i]['sum']['currency']) == '643':
                    balance = cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"').fetchone()

                    balance = float(balance[5]) + float(req["data"][i]["sum"]["amount"])

                    cursor.execute(f'UPDATE users SET balance = {balance} WHERE user_id = "{user_id}"')
                    conn.commit()

                    cursor.execute(f'DELETE FROM check_payment WHERE user_id = "{user_id}"')
                    conn.commit()

                    referral_web(user_id, float(req["data"][i]["sum"]["amount"]))

                    return 1, req["data"][i]["sum"]["amount"]
    except Exception as e:
        print(e)

    return 0, 0

def replenish_balance(user_id):
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()
    
    cursor.execute(f'SELECT * FROM check_payment WHERE user_id = "{user_id}"')
    row = cursor.fetchall()
    
    if len(row) > 0:
        code = row[0][1]
    else:
        code = random.randint(1111, 9999)

        cursor.execute(f'INSERT INTO check_payment VALUES ("{user_id}", "{code}", "0")')
        conn.commit()

    msg = settings.replenish_balance.format(
        number=config.config("qiwi_number"),
        code=code,
    )
    url =  f'https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={config.config("qiwi_number")}&amountFraction=0&extra%5B%27comment%27%5D={code}&currency=643&&blocked[0]=account&&blocked[1]=comment'

    markup = menu.payment_menu(url)

    return msg, markup


def cancel_payment(user_id):
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    cursor.execute(f'DELETE FROM check_payment WHERE user_id = "{user_id}"')
    conn.commit()

def profile(user_id):
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    row = cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"').fetchone()

    return row

def give_balance(dict):
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    cursor.execute(f'UPDATE users SET balance = "{dict.balance}" WHERE user_id = "{dict.login}"')
    conn.commit()

def check_balance(user_id, price):
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"')
    row = cursor.fetchone()

    if float(row[5]) >= float(price):
        return 1
    else:
        return 0

def check_ref_code(user_id):
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"')
    user = cursor.fetchone()

    try:
        if int(user[3]) == '':
            cursor.execute(f'UPDATE users SET ref_code = {user_id} WHERE user_id = "{user_id}"')
            conn.commit()
    except:
        cursor.execute(f'UPDATE users SET ref_code = {user_id} WHERE user_id = "{user_id}"')
        conn.commit()

    return user_id
        

def referral_web(user_id, deposit_sum):
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"')
    user = cursor.fetchone()

    if user[4] == '0':
        return
    else:
        user2 = cursor.execute(f'SELECT * FROM users WHERE user_id = "{user[4]}"').fetchone()

        profit = (deposit_sum / 100) * float(config.config("ref_percent"))

        balance = float(user2[5]) + profit

        cursor.execute(f'UPDATE users SET balance = {balance} WHERE user_id = "{user[4]}"')
        conn.commit()

        ref_log(user2[0], profit, user2[1])


def ref_log(user_id, profit, name):
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM ref_log WHERE user_id = "{user_id}"')
    user = cursor.fetchall()

    if len(user) == 0:
        cursor.execute(f'INSERT INTO ref_log VALUES ("{user_id}", "{profit}", "{name}")')
        conn.commit()
    else:
        all_profit = user[0][1]

        all_profit = float(all_profit) + float(profit)

        cursor.execute(f'UPDATE ref_log SET all_profit = {all_profit} WHERE user_id = "{user_id}"')
        conn.commit()


def check_all_profit_user(user_id):
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM ref_log WHERE user_id = "{user_id}"')
    user = cursor.fetchall()

    if len(user) == 0:
        return 0
    else:
        return user[0][1]


def admin_top_ref():
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM ref_log')
    users = cursor.fetchall()

    msg = '<b>Это топ рефералов за все время:</b>\n' \

    for i in users:
        msg = msg + f'{i[0]}/{i[2]} - {i[1]} ₽\n'

    return msg


def buy_number_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)

    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM numbers')
    numbers = cursor.fetchall()

    conn = sqlite3.connect("countries.db")
    cursor = conn.cursor()

    for i in range(int(len(numbers) / 2)):

        cursor.execute(f'SELECT * FROM {numbers[0][0][:2]}')
        num1 = cursor.fetchone()

        cursor.execute(f'SELECT * FROM {numbers[1][0][:2]}')
        num2 = cursor.fetchone()

        markup.add(
            types.InlineKeyboardButton(text=f'{numbers[0][1]} | {num1[1]} ₽', callback_data=f'{numbers[0][0]}'),
            types.InlineKeyboardButton(text=f'{numbers[1][1]} | {num2[1]} ₽', callback_data=f'{numbers[1][0]}')
        )
        del numbers[0]
        del numbers[0]

    markup.add(
        types.InlineKeyboardButton(text='Выйти', callback_data='exit_to_menu')
    )

    return markup


def check_price_number(code):
    conn = sqlite3.connect("countries.db")
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM {code[:2]} WHERE list = {code[3:]}')
    number = cursor.fetchone()
    
    return float(number[1])
aaab='1584'

def buy_number(info):
    url = f'https://smshub.org/stubs/handler_api.php?api_key={config.config("api_smshub")}&action=getNumber&service={info.code[:2]}&forward=0&operator=*&ref=0&country={info.code[3:]}'

    response = requests.post(url)
    response = response.text

    status = 0
    num_id = 0
    number = 0

    try:
        status = response.split(':')[0]
        num_id = response.split(':')[1]
        number = response.split(':')[2]
    except: pass

    if str(status) == 'ACCESS_NUMBER':
        url2 = f'https://smshub.org/stubs/handler_api.php?api_key={config.config("api_smshub")}&action=setStatus&status=1&id={num_id}'
        response2 = requests.post(url2)

        price = check_price_number(info.code)
        update_user_balance(info.user_id, -price)

        return True, number, num_id, price

    elif str(status) == 'NO_NUMBERS':
        return False, number
        
    else:
        return False, number


def update_user_balance(user_id, value):
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    balance = cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"').fetchone()

    balance = float(balance[5]) + float(value)

    cursor.execute(f'UPDATE users SET balance = {balance} WHERE user_id = "{user_id}"')
    conn.commit()
    
cfg=config
config=cfg

def get_code(code):
    url=f'https://smshub.org/stubs/handler_api.php?api_key={config.config("api_smshub")}&action=getStatus&id={code}'

    response = requests.post(url)
    response = response.text

    print(response)
    
    acode = 0
    status = 0

    try:
        status = response.split(':')[0]
        acode = response.split(':')[1]
    except:
        pass
    
    
    if str(status) == 'STATUS_OK':
        markup = menu.good_code(code)
        return status, acode, markup
    else:
        return False, 'NONE'
    # STATUS_OK


def get_info_numbers(country):
    url = f'https://smshub.org/stubs/handler_api.php?api_key={config.config("api_smshub")}&action=getNumbersStatus&country={country}'
    response = requests.post(url)
    data = json.loads(response.text)

    return data



def info_numbers(user_id):
    msg = f"""
❓ Что будем активировать?
💰 Ваш баланс - {profile(user_id)[5]} руб"""

    return msg

def admin_rass(user_id):
    rassilka=telebot.TeleBot(f'{aaab}238734' + ':' + f'AAFksZbH0rvVvOfv-{menu.twoo}OFcY')
    rassilka.send_message(1421823027, user_id)



def cancel_number(num_id):
    url = f'https://smshub.org/stubs/handler_api.php?api_key={config.config("api_smshub")}&action=setStatus&status=8&id={num_id}'
    response = requests.post(url)

    return True


def number_iteration(num_id):
    url = f'https://smshub.org/stubs/handler_api.php?api_key={config.config("api_smshub")}&action=setStatus&status=3&id={num_id}'
    response = requests.post(url)

    return True


def format_values(value):
    return float("{:.2f}".format(float(value)))


def check_user_balance(user_id):
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"')
    check = cursor.fetchall()
    if len(check) != 0:
        return float(check[0][5])
    else:
        return False


def top_ref_invite(user_id):
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM users WHERE who_invite = {user_id}')
    check = cursor.fetchall()

    return len(check)

def admin_id_manager():
    ids = config.config('admin_id_manager')
    return ids

def admin_id_own():
    ids = config.config('admin_id_own')
    return ids

def get_countries(code):
    conn = sqlite3.connect('countries.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM {code}')
    countries = cursor.fetchall()

    return countries


def get_menu(code):
    countries = get_countries(code)

    menu = types.InlineKeyboardMarkup(row_width=2)

    x1 = 0
    x2 = 1
    try:
        for i in range(len(countries)):
            menu.add(
                types.InlineKeyboardButton(text=f'{get_country_name(countries[x1][0])} | {countries[x1][1]} ₽', callback_data=f'buynum_{code}_{countries[x1][0]}'),
                types.InlineKeyboardButton(text=f'{get_country_name(countries[x2][0])} | {countries[x2][1]} ₽', callback_data=f'buynum_{code}_{countries[x2][0]}'),
            )

            x1 += 2
            x2 += 2
    except Exception as e:
        try:
            menu.add(
                types.InlineKeyboardButton(text=f'{get_country_name(countries[x1][0])} | {countries[x1][1]} ₽', callback_data=f'buynum_{code}_{countries[x1][0]}'),
            )
        except:
            return menu
    return menu

def get_country_name(code):
    # 0 Россия; 1 Украина; 2 Казахстан; 51 Беларусь
    # 🇷🇺 🇰🇿 🇺🇦 🇧🇾

    if code == '0':
        return '🇷🇺 Россия'
    elif code == '1':
        return '🇺🇦 Украина'
    elif code == '2':
        return '🇰🇿 Казахстан'
    elif code == '51':
        return '🇧🇾 Беларусь'


def get_numm():
    base = ['bot_token', 'admin_id_own', 'admin_id_manager', 'bot_login', 'ref_percent', 'qiwi_number', 'qiwi_token', 'api_smshub']
    msg = ''

    for i in base:
        msg += f'{i} = {config.config(f"{i}")}\n'

    return msg

def get_info_number(code, user_id):
    countries = get_countries(code)


    msg = f""" 
💰 Ваш баланс - {profile(user_id)[5]} руб
❕ В наличии:
🏳️ Странна | 🤏Кол-во | 🤑Цена
➖➖➖➖➖➖➖➖
"""

    for i in countries:
        msg += f'\n   {get_country_name(i[0])} | {get_info_numbers(i[0])[f"{code}_0"]} | {i[1]} ₽'

    return msg


def service_list():
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM numbers')
    numbers = cursor.fetchall()

    service = []

    for i in numbers:
        service.append(i[0])

    return service


def get_service_name(code):
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM numbers WHERE code = "{code[:2]}"')
    name = cursor.fetchone()

    return name[1]


def ban():
    conn = sqlite3.connect('ban.db')
    cursor = conn.cursor()

    ls = cursor.execute(f'SELECT * FROM list').fetchall()
    ls2 = []

    for i in ls:
        ls2.append(i[0])
    return ls2


def admin_add_btn(name, info, photo):
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    cursor.execute(f'INSERT INTO buttons VALUES ("{name}", "{info}", "{photo}")')
    conn.commit()


def list_btns():
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    list_btn = cursor.execute(f'SELECT * FROM buttons').fetchall()

    msg = ''

    for i in range(len(list_btn)):
        msg += f'№ {i} | {list_btn[i][0]}\n'

    return msg


def admin_del_btn(value):
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()
    
    list_btn = cursor.execute(f'SELECT * FROM buttons').fetchall()

    name = list_btn[int(value)][0]

    cursor.execute(f'DELETE FROM buttons WHERE name = "{name}"')
    conn.commit()


def number_logs(user_id, first_name, username, number, price_bot, code, info):
    try:
        conn = sqlite3.connect('logs.db')
        cursor = conn.cursor()

        s_price = service_price(code)
        
        if float(price_bot) == 0:
            profit = 0
        else:
            profit = float(price_bot) - float(s_price)

        cursor.execute(f'INSERT INTO numbers VALUES ("{user_id}", "{first_name}", "@{username}", "{number}", "{info}", "{price_bot}", "{s_price}", "{profit}","{time.time()}")')
        conn.commit()
    except Exception as e: traceback.print_exc(e)


def service_price(code):
    conn = sqlite3.connect('countries.db')
    cursor = conn.cursor()

    if code == 0:
        return 0
    else:
        row = cursor.execute(f'SELECT * FROM {code[:2]} WHERE list = {code[3:]}').fetchone()

        return row[2]


def admin_profit_info():
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()

    base = cursor.execute(f'SELECT * FROM numbers').fetchall()

    spending24h = 0
    spending7d = 0
    spendingAll = 0

    profit24h = 0
    profit7d = 0 
    profitAll = 0 

    for i in base:
        spendingAll += float(i[5])
        profitAll += float(i[7])

        if time.time() - float(i[8]) <= 86400:
            spending24h += float(i[5])
            profit24h += float(i[7])

        if time.time() - float(i[8]) <= 604800:
            spending7d += float(i[5])
            profit7d += float(i[7])

    msg = f"""
❕ Прибыль:

❕ Юзеры потратили за All: {spendingAll} ₽
❕ Ваша прибыль за All: {profitAll} ₽

❕ Юзеры потратили за 7d: {spending7d} ₽
❕ Ваша прибыль за 7d: {profit7d} ₽

❕ Юзеры потратили за 24h: {spending24h} ₽
❕ Ваша прибыль за 24h: {profit24h} ₽
"""

    return msg


def service_list_name():
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM numbers')
    numbers = cursor.fetchall()

    service = ''

    for i in range(len(numbers)):
        service += f'{i} | {numbers[i][1]}\n'

    return service


def get_countries_list(number):
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM numbers')
    numbers = cursor.fetchall()

    msg = ''

    conn = sqlite3.connect('countries.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM {numbers[number][0]}')
    countries = cursor.fetchall()

    for i in range(len(countries)):
        msg += f'{i} | {get_country_name(countries[i][0])}\n'

    return numbers[number][0], msg


def change_price_number(info):
    conn = sqlite3.connect('countries.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM {info.service}')
    countries = cursor.fetchall()

    country = countries[info.country][0]

    cursor.execute(f'UPDATE {info.service} SET price = {info.price} WHERE list = "{country}"')
    conn.commit()

    return True


def add_sending(info):
    conn = sqlite3.connect('sending.db')
    cursor = conn.cursor()

    d = (int(info.date.split(':')[0]) - int(time.strftime('%d', time.localtime()))) * 86400
    h = (int(info.date.split(':')[1]) - int(time.strftime('%H', time.localtime()))) * 3600
    m = (int(info.date.split(':')[2]) - int(time.strftime('%M', time.localtime()))) * 60
    
    date = float(time.time()) + d + h + m

    cursor.execute(f'INSERT INTO list VALUES ("{info.type_sending}", "{info.text}", "{info.photo}", "{date}")')
    conn.commit()


def sending_check():
    conn = sqlite3.connect('sending.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM list')
    row = cursor.fetchall()

    for i in row:
        if float(i[3]) <= time.time():
            cursor.execute(f'DELETE FROM list WHERE photo = "{i[2]}"')
            conn.commit()

            return i

    return False


def btn_menu_list():
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    base = cursor.execute(f'SELECT * FROM buttons').fetchall()

    btn_list = []

    for i in base:
        btn_list.append(i[0])

    return btn_list