# This Python file uses the following encoding: utf-8

from telebot import types as t
from content import cont


def gen_b(i_obj):
    buttons = [t.KeyboardButton(b) for b in i_obj]
    return tuple(buttons)


def gen_dyn_keys(i_obj, excl_lst, inv_d, ex_but=None, cols=2):

    b_names = []

    for elem in i_obj:
        if inv_d[elem] not in excl_lst:
            b_names.append(elem)

    buttons = [t.KeyboardButton(b) for b in b_names]
    keyboard = t.ReplyKeyboardMarkup(row_width=cols,
                                     resize_keyboard=True)
    if ex_but is None:
        keyboard.add(req_cancel_b, next_filter_b, *buttons)
    else:
        keyboard.add(req_cancel_b, next_filter_b, *ex_but, *buttons)

    return keyboard


# Комманды
hidekey = t.ReplyKeyboardRemove()

# Кнопки - Общие
to_start_b = t.KeyboardButton('↩️ К началу')
next_filter_b = t.KeyboardButton('➡️ Далее')
req_cancel_b = t.KeyboardButton('❌ Отмена')

# Общее меню - возврат
back_m = t.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
back_m.add(to_start_b)

# Общее меню - отмена
req_cancel_m = t.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
req_cancel_m.add(req_cancel_b)

# Информация о языке запросов
req_hh_info_b = t.InlineKeyboardButton(text='ℹ️ HH.RU',
                                       url='https://kazan.hh.ru/article/1175')
req_hh_info_m = t.InlineKeyboardMarkup(row_width=1)
req_hh_info_m.add(req_hh_info_b)

# МЕНЮ - Старт
start_b = ('Парсинг', 'Очередь', 'Мои запросы', 'О боте')
start_m = t.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
start_m.add(*gen_b(start_b))

# МЕНЮ - Парсинг
pars_main_b = ('HH.ru', 'Авито', 'SuperJob')
pars_main_m = t.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
pars_main_m.add(*gen_b(pars_main_b), to_start_b)

# МЕНЮ - Парсинг - режим HH
pars_hh_mode_b = tuple(cont.a_mode_g.values())
pars_hh_mode_m = t.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
pars_hh_mode_m.add(*gen_b(pars_hh_mode_b), req_cancel_b)

# МЕНЮ - Парсинг - даты HH
pars_hh_date_m = t.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
pars_hh_date_m.add(req_cancel_b, *gen_b(cont.date_preset.keys()))

# МЕНЮ - Парсинг - Иключение из запроса
excl_hh_b = ('Без стоп-слов',)
excl_hh_m = t.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
excl_hh_m.add(req_cancel_b, *gen_b(excl_hh_b))

# МЕНЮ - Парсинг - параметры фильтров HH
pars_hh_filter_b = tuple(cont.filter_g.values())
pars_hh_filter_m = t.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
pars_hh_filter_m.add(*gen_b(pars_hh_filter_b), req_cancel_b)

# МЕНЮ - Парсинг - режим поиска
pars_hh_search_b = tuple(cont.search_g.values())
pars_hh_search_m = t.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
pars_hh_search_m.add(*gen_b(pars_hh_search_b), req_cancel_b)


# ПОДТВЕРЖДЕНИЕ ЗАПРОСА HH!
start_pars_hh_b = ('Старт', )
start_pars_hh_m = t.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
start_pars_hh_m.add(req_cancel_b, *gen_b(start_pars_hh_b))
