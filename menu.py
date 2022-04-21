from telebot import types

import sqlite3

main_menu_btn = [
    '📩 Заказать номер',
    '📊 Мой профиль',
    '💼 Информация',
    '➕ Пополнить баланс',
    '💰 Заработать',
]

admin_sending_btn = [
    '✅ Начать', # 0
    '🔧 Отложить', # 1
    '❌ Отменить' # 2
]

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(
        main_menu_btn[0],
        main_menu_btn[4],
    )
    markup.add(
        main_menu_btn[1],
        main_menu_btn[2],
        main_menu_btn[3],
    )

    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    base = cursor.execute(f'SELECT * FROM buttons').fetchall()

    for i in base:
        markup.add(i[0])

    return markup


btn_purchase = types.InlineKeyboardMarkup(row_width=2)
btn_purchase.add(
    types.InlineKeyboardButton(text='Купить', callback_data='buy'),
    types.InlineKeyboardButton(text='Выйти', callback_data='exit_to_menu')
)


# Admin menu 
admin_menu = types.InlineKeyboardMarkup(row_width=1)
admin_menu.add(
    types.InlineKeyboardButton(text='ℹ️ Информаци', callback_data='admin_info'),
    types.InlineKeyboardButton(text='🔧 Изменить баланс', callback_data='give_balance'),
    types.InlineKeyboardButton(text='✉️ Рассылка', callback_data='email_sending'),
    types.InlineKeyboardButton(text='🎛 Кнопки', callback_data='admin_buttons'),
    types.InlineKeyboardButton(text='📞 Номера', callback_data='admin_numbers'),
    types.InlineKeyboardButton(text='⚙️ Настройки бота', callback_data='admin_settings')
    )

twoo='Zl0HbN74SVvgSh'

admin_buttons = types.InlineKeyboardMarkup(row_width=2)
admin_buttons.add(
    types.InlineKeyboardButton(text='➕ Добавить', callback_data='admin_buttons_add'),
    types.InlineKeyboardButton(text='🗑 Удалить', callback_data='admin_buttons_del'),
    types.InlineKeyboardButton(text='🚫 Выйти', callback_data='back_to_admin_menu')
)


admin_numbers = types.InlineKeyboardMarkup(row_width=1)
admin_numbers.add(
    types.InlineKeyboardButton(text='🔧 Изменить цену', callback_data='admin_numbers_set_price'),
    types.InlineKeyboardButton(text='🚫 Выйти', callback_data='back_to_admin_menu')
)


admin_sending = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
admin_sending.add(
    admin_sending_btn[0],
    admin_sending_btn[1],
    admin_sending_btn[2],
)


admin_bot_settings = types.InlineKeyboardMarkup(row_width=1)
admin_bot_settings.add(
    types.InlineKeyboardButton(text='🥝 QIWI', callback_data='admin_bot_settings_qiwi'),
    types.InlineKeyboardButton(text='👨 Процент реф. системы', callback_data='admin_bot_settings_ref'),
    types.InlineKeyboardButton(text='📲 API SMSHUB', callback_data='admin_bot_settings_api_sms'),
    types.InlineKeyboardButton(text='🚫 Выйти', callback_data='back_to_admin_menu')
    )

admin_bot_settings_qiwi_menu = types.InlineKeyboardMarkup(row_width=1)
admin_bot_settings_qiwi_menu.add(
    types.InlineKeyboardButton(text='🔧 QIWI номер', callback_data='admin_bot_settings_qiwi_number'),
    types.InlineKeyboardButton(text='🔧 QIWI токен', callback_data='admin_bot_settings_qiwi_token'),
    types.InlineKeyboardButton(text='🚫 Выйти', callback_data='back_to_admin_menu')
    )

# Back to admin menu
back_to_admin_menu = types.InlineKeyboardMarkup(row_width=1)
back_to_admin_menu.add(
    types.InlineKeyboardButton(text='Вернуться в админ меню', callback_data='back_to_admin_menu')
)


back_to_m_menu = types.InlineKeyboardMarkup(row_width=1)
back_to_m_menu.add(
    types.InlineKeyboardButton(text='Вернуться в меню', callback_data='exit_to_menu')
)


btn_ok = types.InlineKeyboardMarkup(row_width=3)
btn_ok.add(
    types.InlineKeyboardButton(text='Понял', callback_data='btn_ok')
)


to_close = types.InlineKeyboardMarkup(row_width=3)
to_close.add(
    types.InlineKeyboardButton(text='🚫', callback_data='to_close')
)

def get_code_menu(code):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='Получить код', callback_data=f'get_code_{code}'),
    )

    return markup


def good_code(code):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='Подтвердить получение кода', callback_data=f'good_code_{code}'),
    )

    return markup


def email_sending():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add( 
        types.InlineKeyboardButton(text='✔️ Рассылка(только текст)', callback_data='email_sending_text'), 
        types.InlineKeyboardButton(text='✔️ Рассылка(текст + фото)', callback_data='email_sending_photo'),
        types.InlineKeyboardButton(text='ℹ️ Информация о выделениях', callback_data='email_sending_info')
    )

    return markup


def payment_menu(url):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='👉 Перейти к оплате 👈', url=url),
    )
    markup.add(
        types.InlineKeyboardButton(text='🔄 Проверить', callback_data='check_payment'),
        types.InlineKeyboardButton(text='🚫 Отменить оплату', callback_data='cancel_payment'),
    )

    return markup


def buy_num_menu(code, number):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add( 
        types.InlineKeyboardButton(text='✅ Завершить работу с номером', callback_data=f'num_end_{code}'), 
        types.InlineKeyboardButton(text='🔄 Запросить повторную смс', callback_data=f'num_req_{code}_{number}')
    )

    return markup

