# This Python file uses the following encoding: utf-8

import telebot
import time
import datetime as dt
from database import con_db, que
from mod import mod, hh_core, infograph
from content import keys, cont


# Перс. данные
token = 'token'

# Бот
bot = telebot.TeleBot(token, num_threads=10)

# Вызовы всплывающих сообщений
alert_list = ('discl_m', )

# Общие текстовые команды выхода
return_list = ('↩️ К началу', '❌ Отмена')

# Лист ожидания
w_ist = {'hh': {},
         'avito': {},
         'sj': {}}

# Временный словарь для запросов
req_stor = {}


# Запуск бота и Регистрация нового пользователя
@bot.message_handler(commands=['start'])
def init(message):

    mod.new_user_reg(message)
    start(message)

    return


# Старт
def start(message):

    u_id = message.chat.id
    m_text = message.text

    con_db.set_val(que.set_state_q,
                   (u_id,
                    'Старт',
                    'ordinary',
                    m_text))
    bot.send_message(u_id,
                     cont.start_mesage,
                     reply_markup=keys.start_m)

    return


# СКВОЗНЫЕ ОБРАБОТЧИКИ
#
# Общий обработчик для всплывающих сообщений
@bot.callback_query_handler(func=lambda call:
                            call.data in alert_list)
def alerts(call):

    if call.data == 'discl_m':
        con_db.set_val(que.new_log_q,
                       (call.u_id,
                        'Дисклеймер',
                        'pop-up message',
                        None))
        bot.answer_callback_query(call.id,
                                  show_alert=True,
                                  text=cont.discl)  # ЗАМЕНИТЬ СООБЩЕНИЕ

    return


# Общий обработчики текстовых команд выхода
@bot.message_handler(func=lambda message:
                     message.text in return_list,
                     content_types=['text'])
def common_return(message):

    u_id = message.chat.id
    m_text = message.text

    if m_text == '↩️ К началу':
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Старт',
                        'return_to_prew',
                        m_text))
        bot.send_message(u_id,
                         '↩️',
                         reply_markup=keys.start_m)

    elif m_text == '❌ Отмена':
        req_stor.pop(u_id, 0)
        w_ist['hh'] = {}
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Старт',
                        'req_cancel',
                        m_text))
        bot.send_message(u_id,
                         'Запрос отменен 🫡',
                         reply_markup=keys.start_m)

    return


# МЕНЮ - Старт
@bot.message_handler(func=lambda message:
                     mod.act_state_msg(message) == 'Старт',
                     content_types=['text'])
def start_main(message):

    u_id = message.chat.id
    m_text = message.text

    # Парсинг - меню
    if m_text == keys.start_b[0]:
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Парсинг',
                        'ordinary',
                        m_text))
        bot.send_message(u_id,
                         cont.pars_t,
                         reply_markup=keys.pars_main_m)

    elif m_text == keys.start_b[1]:

        if len(w_ist['hh']) == 0:
            bot.send_message(u_id,
                             'Сейчас парсер свободен ✅',
                             reply_markup=keys.start_m)

        else:
            bot.send_message(u_id,
                             mod.pars_busy(w_ist['hh']['name'],
                                           w_ist['hh']['cr_dt'],
                                           w_ist['hh']['fc_finish']),
                             reply_markup=keys.start_m)

    # Разделы в разработке
    elif m_text in keys.start_b:
        bot.send_message(u_id,
                         cont.in_process_t,
                         reply_markup=keys.start_m)

    else:
        bot.send_message(u_id,
                         cont.invalid_command_t,
                         reply_markup=keys.start_m)

    return


# МЕНЮ - парсер
@bot.message_handler(func=lambda message:
                     mod.act_state_msg(message) == 'Парсинг',
                     content_types=['text'])
def pars_main(message):

    u_id = message.chat.id
    m_text = message.text

    # Источник парсинга - HH.ru
    if m_text == keys.pars_main_b[0]:
        """bot.send_sticker(u_id,
                         cont.hh_sticker)"""
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Парсинг-hh.ru',
                        'ordinary',
                        m_text))
        bot.send_message(u_id,
                         cont.pars_hh_mode_t,
                         reply_markup=keys.pars_hh_mode_m)

    elif m_text in keys.pars_main_b:
        bot.send_message(u_id,
                         cont.in_process_t,
                         reply_markup=keys.pars_main_m)

    else:
        bot.send_message(u_id,
                         cont.invalid_command_t,
                         reply_markup=keys.pars_main_m)

    return


# МЕНЮ - парсер - hh.ru - режимы
@bot.message_handler(func=lambda message:
                     mod.act_state_msg(message) == 'Парсинг-hh.ru',
                     content_types=['text'])
def pars_hh_mode(message):

    u_id = message.chat.id
    m_text = message.text

    if m_text in keys.pars_hh_mode_b and len(req_stor) == 0:

        mod.init_hh_req(u_id, req_stor,
                        cont.a_mode_g_inv[m_text])

        cr_dt = req_stor[u_id]['user_req']['req_create']
        fc_finish = cr_dt + dt.timedelta(minutes=5)

        w_ist['hh'] = {'name': 'Новый запрос',
                       'cr_dt': cr_dt.strftime('%d.%m.%Y г. %H:%M'),
                       'fc_finish': fc_finish.strftime('%d.%m.%Y г. %H:%M')}

        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Парсинг-hh.ru-даты',
                        'ordinary',
                        m_text))
        bot.send_message(u_id,
                         cont.pars_hh_date_t,
                         reply_markup=keys.pars_hh_date_m)

    else:

        if len(req_stor) != 0 and len(w_ist['hh']) != 0:
            bot.send_message(u_id,
                             mod.pars_busy(w_ist['hh']['name'],
                                           w_ist['hh']['cr_dt'],
                                           w_ist['hh']['fc_finish']),
                             reply_markup=keys.start_m)

        else:
            bot.send_message(u_id,
                             cont.invalid_command_t,
                             reply_markup=keys.pars_hh_mode_m)

    return


# МЕНЮ - парсер - hh.ru - диапазон дат
@bot.message_handler(func=lambda message:
                     mod.act_state_msg(message) == 'Парсинг-hh.ru-даты',
                     content_types=['text'])
def pars_hh_date_range(message):

    u_id = message.chat.id
    m_text = message.text

    if req_stor.setdefault(u_id, 0) == 0:
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Старт',
                        'empty_req_error',
                        m_text))
        bot.send_message(u_id,
                         cont.empty_req_error_t,
                         reply_markup=keys.start_m)
        w_ist['hh'] = {}

        return

    if m_text in cont.date_preset:

        if m_text != 'Сегодня':

            dates = cont.date_preset[m_text]

            req_stor[u_id]['date_range'] = mod.date_to_range(dates)
            req_stor[u_id]['hh_req']['date_from'] = dates[0]
            req_stor[u_id]['hh_req']['date_to'] = dates[1]

        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Парсинг-hh.ru-название',
                        'ordinary',
                        m_text))
        bot.send_message(u_id,
                         cont.pars_hh_name_t,
                         reply_markup=keys.req_cancel_m)

    else:

        res = mod.check_date(m_text)

        if res[0] == 0:

            req_stor[u_id]['date_range'] = mod.date_to_range(res)
            req_stor[u_id]['hh_req']['date_from'] = res[1][0]
            req_stor[u_id]['hh_req']['date_to'] = res[1][1]
            bot.send_message(u_id,
                             cont.pars_hh_name_t,
                             reply_markup=keys.req_cancel_m)

            con_db.set_val(que.set_state_q,
                           (u_id,
                            'Парсинг-hh.ru-название',
                            'ordinary',
                            m_text))
            bot.send_message(u_id,
                             cont.pars_hh_name_t,
                             reply_markup=keys.req_cancel_m)

        else:
            bot.send_message(u_id,
                             cont.check_date_res[res[0]],
                             reply_markup=keys.req_cancel_m)
            bot.send_message(u_id,
                             cont.pars_hh_date_reply_t,
                             reply_markup=keys.req_cancel_m)

    return


# МЕНЮ - парсер - hh.ru - название запроса
@bot.message_handler(func=lambda message:
                     mod.act_state_msg(message) == 'Парсинг-hh.ru-название',
                     content_types=['text'])
def pars_hh_req_name(message):

    u_id = message.chat.id
    m_text = message.text

    if req_stor.setdefault(u_id, 0) == 0:
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Старт',
                        'empty_req_error',
                        m_text))
        bot.send_message(u_id,
                         cont.empty_req_error_t,
                         reply_markup=keys.start_m)
        w_ist['hh'] = {}

        return

    # Проверка ввода
    check = mod.check_req_name(m_text)

    if check[0] == 0:
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Парсинг-hh.ru-запрос',
                        'ordinary',
                        m_text))

        req_stor[u_id]['user_req']['req_name'] = check[1]

        w_ist['hh']['name'] = check[1]

        bot.send_message(u_id,
                         cont.pars_hh_title_t,
                         reply_markup=keys.req_cancel_m)

        bot.send_message(u_id,
                         cont.req_hh_info_t,
                         reply_markup=keys.req_hh_info_m)

    else:
        bot.send_message(u_id,
                         cont.check_req_name[check[0]],
                         reply_markup=keys.req_cancel_m)
    return


# МЕНЮ - парсер - hh.ru - текстовый запрос
@bot.message_handler(func=lambda message:
                     mod.act_state_msg(message) == 'Парсинг-hh.ru-запрос',
                     content_types=['text'])
def pars_hh_req_title(message):

    u_id = message.chat.id
    m_text = message.text

    if req_stor.setdefault(u_id, 0) == 0:
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Старт',
                        'empty_req_error',
                        m_text))
        bot.send_message(u_id,
                         cont.empty_req_error_t,
                         reply_markup=keys.start_m)
        w_ist['hh'] = {}

        return

    check = mod.check_req_title(m_text)

    if check == 0:
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Парсинг-hh.ru-исключения',
                        'ordinary',
                        m_text))

        new_title = mod.transform_req_str(m_text)
        req_stor[u_id]['hh_req']['req_title'] = new_title
        bot.send_message(u_id,
                         cont.pars_hh_title_excl_t,
                         reply_markup=keys.excl_hh_m)

    else:
        bot.send_message(u_id,
                         cont.check_req_title[check],
                         reply_markup=keys.hidekey)

    return


# МЕНЮ - парсер - hh.ru - исключения из запроса
@bot.message_handler(func=lambda message:
                     mod.act_state_msg(message) == 'Парсинг-hh.ru-исключения',
                     content_types=['text'])
def pars_hh_req_excl(message):

    u_id = message.chat.id
    m_text = message.text

    if req_stor.setdefault(u_id, 0) == 0:
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Старт',
                        'empty_req_error',
                        m_text))
        bot.send_message(u_id,
                         cont.empty_req_error_t,
                         reply_markup=keys.start_m)
        w_ist['hh'] = {}

        return

    if m_text == keys.excl_hh_b[0]:
        check = 0

    else:
        check = mod.check_req_title(m_text)

        if check == 0:

            new_title = mod.transform_req_str(
                req_stor[u_id]['hh_req']['req_title'], m_text)
            req_stor[u_id]['hh_req']['req_title'] = new_title

        else:
            bot.send_message(u_id,
                             cont.check_req_title[check],
                             reply_markup=keys.excl_hh_m)

    if check != 0:
        pass

    # req_stor[u_id]['user_req']['req_type'] == 'only prew':

    else:
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Парсинг-hh.ru-фильтры',
                        'ordinary',
                        m_text))
        hh_core.insert_new_req(u_id, req_stor)
        bot.send_message(u_id,
                         cont.pars_hh_filter_t,
                         reply_markup=keys.pars_hh_filter_m)

    return


# МЕНЮ - парсер - hh.ru - фильтры
@bot.message_handler(func=lambda message:
                     mod.act_state_msg(message) == 'Парсинг-hh.ru-фильтры',
                     content_types=['text'])
def pars_hh_req_filters(message):

    u_id = message.chat.id
    m_text = message.text

    if req_stor.setdefault(u_id, 0) == 0:
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Старт',
                        'empty_req_error',
                        m_text))
        bot.send_message(u_id,
                         cont.empty_req_error_t,
                         reply_markup=keys.start_m)
        w_ist['hh'] = {}

        return

    # Выбор простого фильтра
    if m_text == keys.pars_hh_filter_b[0]:
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Парсинг-hh.ru-старт',
                        'simple_f',
                        m_text))
        bot.send_message(u_id,
                         cont.start_pars_hh_t,
                         reply_markup=keys.start_pars_hh_m)

    # Выбор расширенного фильтра
    elif m_text == keys.pars_hh_filter_b[1]:
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Парсинг-hh.ru-поиск',
                        'custom_f',
                        m_text))
        bot.send_message(u_id,
                         cont.pars_hh_search_t,
                         reply_markup=keys.pars_hh_search_m)

        cur_text = mod.decode_str(req_stor[u_id]['hh_req']['search_field'],
                                  cont.search_g)

        bot.send_message(u_id,
                         f'Текущее значение ⬇️\n{cur_text}',
                         reply_markup=keys.pars_hh_search_m)

    else:
        bot.send_message(u_id,
                         cont.invalid_command_t,
                         reply_markup=keys.pars_hh_filter_m)

    return


# МЕНЮ - парсер - hh.ru - параметры поиска
@bot.message_handler(func=lambda message:
                     mod.act_state_msg(message) == 'Парсинг-hh.ru-поиск',
                     content_types=['text'])
def pars_hh_req_search(message):

    u_id = message.chat.id
    m_text = message.text

    if req_stor.setdefault(u_id, 0) == 0:
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Старт',
                        'empty_req_error',
                        m_text))
        bot.send_message(u_id,
                         cont.empty_req_error_t,
                         reply_markup=keys.start_m)
        w_ist['hh'] = {}

        return

    if m_text in keys.pars_hh_search_b:

        req_stor[u_id]['hh_req']['search_field'] = cont.search_g_inv[m_text]

        dyn_markup = keys.gen_dyn_keys(cont.reg_g.values(),
                                       req_stor[u_id]['hh_req']['area'],
                                       cont.reg_g_inv,
                                       ex_but=['Дистрибьюция', 'Города'])

        bot.send_message(u_id,
                         cont.pars_hh_set_reg_t,
                         reply_markup=dyn_markup)

        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Парсинг-hh.ru-регион',
                        'custom_f',
                        m_text))

        cur_text = mod.decode_lst(req_stor[u_id]['hh_req']['area'],
                                  cont.reg_g)

        bot.send_message(u_id,
                         f'Текущее значение ⬇️\n{cur_text}',
                         reply_markup=dyn_markup)

    else:
        bot.send_message(u_id,
                         cont.invalid_command_t,
                         reply_markup=keys.pars_hh_search_m)

    return


# МЕНЮ - парсер - hh.ru - регион
@bot.message_handler(func=lambda message:
                     mod.act_state_msg(message) == 'Парсинг-hh.ru-регион',
                     content_types=['text'])
def pars_hh_req_region(message):

    u_id = message.chat.id
    m_text = message.text

    if req_stor.setdefault(u_id, 0) == 0:
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Старт',
                        'empty_req_error',
                        m_text))
        bot.send_message(u_id,
                         cont.empty_req_error_t,
                         reply_markup=keys.start_m)
        w_ist['hh'] = {}

        return

    if m_text == 'Дистрибьюция':
        req_stor[u_id]['hh_req']['area'] = cont.reg_distr_preset[m_text]

        dyn_markup = keys.gen_dyn_keys(cont.reg_113.values(),
                                       req_stor[u_id]['hh_req']['area'],
                                       cont.reg_113_inv)

        bot.send_message(u_id,
                         cont.filter_accept_t,
                         reply_markup=dyn_markup)

        bot.send_message(u_id,
                         'Текущее значение ⬇️\n\n✔️ - Дистрибьюция',
                         reply_markup=dyn_markup)

    elif m_text == 'Города':

        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Парсинг-hh.ru-города',
                        'custom_f',
                        m_text))

        req_stor[u_id]['hh_req']['area'] = ['113']

        dyn_markup = keys.gen_dyn_keys(cont.city_g.values(),
                                       req_stor[u_id]['hh_req']['area'],
                                       cont.city_g_inv,
                                       ex_but=['Регионы'])

        bot.send_message(u_id,
                         cont.filter_accept_t,
                         reply_markup=dyn_markup)

        bot.send_message(u_id,
                         'Текущее значение ⬇️\n\n✔️ - Все города',
                         reply_markup=dyn_markup)

    elif m_text in cont.reg_g.values():

        if cont.reg_g_inv[m_text] == '113' or req_stor[u_id]['hh_req']['area'] == ['113']:
            req_stor[u_id]['hh_req']['area'] = [cont.reg_g_inv[m_text]]

        else:
            req_stor[u_id]['hh_req']['area'].append(cont.reg_g_inv[m_text])

        dyn_markup = keys.gen_dyn_keys(cont.reg_g.values(),
                                       req_stor[u_id]['hh_req']['area'],
                                       cont.reg_g_inv,
                                       ex_but=['Дистрибьюция', 'Города'])

        bot.send_message(u_id,
                         cont.filter_accept_t,
                         reply_markup=dyn_markup)

        cur_text = mod.decode_lst(req_stor[u_id]['hh_req']['area'],
                                  cont.reg_g)

        bot.send_message(u_id,
                         f'Текущее значение ⬇️\n{cur_text}',
                         reply_markup=dyn_markup)

    elif m_text == '➡️ Далее':
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Парсинг-hh.ru-индустрия',
                        'custom_f',
                        m_text))

        dyn_markup = keys.gen_dyn_keys(cont.ind_g.values(),
                                       req_stor[u_id]['hh_req']['industry'],
                                       cont.ind_g_inv)

        bot.send_message(u_id,
                         cont.pars_hh_set_ind_t,
                         reply_markup=dyn_markup)

        cur_text = mod.decode_lst(req_stor[u_id]['hh_req']['industry'],
                                  cont.ind_g)

        bot.send_message(u_id,
                         f'Текущее значение ⬇️\n{cur_text}',
                         reply_markup=dyn_markup)

    else:
        bot.send_message(u_id,
                         cont.invalid_command_t,
                         reply_markup=keys.gen_dyn_keys(cont.reg_g.values(),
                                                        req_stor[u_id]['hh_req']['area'],
                                                        cont.reg_g_inv,
                                                        ex_but=['Дистрибьюция', 'Города']))

    return


# МЕНЮ - парсер - hh.ru - города
@bot.message_handler(func=lambda message:
                     mod.act_state_msg(message) == 'Парсинг-hh.ru-города',
                     content_types=['text'])
def pars_hh_req_city(message):

    u_id = message.chat.id
    m_text = message.text

    if req_stor.setdefault(u_id, 0) == 0:
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Старт',
                        'empty_req_error',
                        m_text))
        bot.send_message(u_id,
                         cont.empty_req_error_t,
                         reply_markup=keys.start_m)
        w_ist['hh'] = {}

        return

    if m_text == 'Регионы':

        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Парсинг-hh.ru-регион',
                        'custom_f',
                        m_text))

        req_stor[u_id]['hh_req']['area'] = ['113']

        dyn_markup = keys.gen_dyn_keys(cont.reg_g.values(),
                                       req_stor[u_id]['hh_req']['area'],
                                       cont.reg_g_inv,
                                       ex_but=['Дистрибьюция', 'Города'])

        bot.send_message(u_id,
                         cont.filter_accept_t,
                         reply_markup=dyn_markup)

        bot.send_message(u_id,
                         'Текущее значение ⬇️\n\n✔️ - Все Регионы',
                         reply_markup=dyn_markup)

    elif m_text in cont.city_g.values():

        if cont.city_g_inv[m_text] == '113' or req_stor[u_id]['hh_req']['area'] == ['113']:
            req_stor[u_id]['hh_req']['area'] = [cont.city_g_inv[m_text]]

        else:
            req_stor[u_id]['hh_req']['area'].append(cont.city_g_inv[m_text])

        dyn_markup = keys.gen_dyn_keys(cont.city_g.values(),
                                       req_stor[u_id]['hh_req']['area'],
                                       cont.city_g_inv,
                                       ex_but=['Регионы'])

        bot.send_message(u_id,
                         cont.filter_accept_t,
                         reply_markup=dyn_markup)

        cur_text = mod.decode_lst(req_stor[u_id]['hh_req']['area'],
                                  cont.city_g)

        bot.send_message(u_id,
                         f'Текущее значение ⬇️\n{cur_text}',
                         reply_markup=dyn_markup)

    elif m_text == '➡️ Далее':
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Парсинг-hh.ru-индустрия',
                        'custom_f',
                        m_text))

        dyn_markup = keys.gen_dyn_keys(cont.ind_g.values(),
                                       req_stor[u_id]['hh_req']['industry'],
                                       cont.ind_g_inv)

        bot.send_message(u_id,
                         cont.pars_hh_set_ind_t,
                         reply_markup=dyn_markup)

        cur_text = mod.decode_lst(req_stor[u_id]['hh_req']['industry'],
                                  cont.ind_g)

        bot.send_message(u_id,
                         f'Текущее значение ⬇️\n{cur_text}',
                         reply_markup=dyn_markup)

    else:
        bot.send_message(u_id,
                         cont.invalid_command_t,
                         reply_markup=keys.gen_dyn_keys(cont.city_g.values(),
                                                        req_stor[u_id]['hh_req']['area'],
                                                        cont.city_g_inv))

    return


# МЕНЮ - парсер - hh.ru - индустрия
@bot.message_handler(func=lambda message:
                     mod.act_state_msg(message) == 'Парсинг-hh.ru-индустрия',
                     content_types=['text'])
def pars_hh_req_industry(message):

    u_id = message.chat.id
    m_text = message.text

    if req_stor.setdefault(u_id, 0) == 0:
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Старт',
                        'empty_req_error',
                        m_text))
        bot.send_message(u_id,
                         cont.empty_req_error_t,
                         reply_markup=keys.start_m)
        w_ist['hh'] = {}

        return

    if m_text in cont.ind_g.values():

        if cont.ind_g_inv[m_text] is None or req_stor[u_id]['hh_req']['industry'] == [None]:
            req_stor[u_id]['hh_req']['industry'] = [cont.ind_g_inv[m_text]]

        else:
            req_stor[u_id]['hh_req']['industry'].append(cont.ind_g_inv[m_text])

        dyn_markup = keys.gen_dyn_keys(cont.ind_g.values(),
                                       req_stor[u_id]['hh_req']['industry'],
                                       cont.ind_g_inv)

        bot.send_message(u_id,
                         cont.filter_accept_t,
                         reply_markup=keys.gen_dyn_keys(cont.ind_g.values(),
                                                        req_stor[u_id]['hh_req']['industry'],
                                                        cont.ind_g_inv))

        cur_text = mod.decode_lst(req_stor[u_id]['hh_req']['industry'],
                                  cont.ind_g)

        bot.send_message(u_id,
                         f'Текущее значение ⬇️\n{cur_text}',
                         reply_markup=dyn_markup)

    elif m_text == '➡️ Далее':
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Парсинг-hh.ru-компании',
                        'custom_f',
                        m_text))

        dyn_markup = keys.gen_dyn_keys(cont.empl_g.values(),
                                       req_stor[u_id]['hh_req']['employer_id'],
                                       cont.empl_g_inv)

        bot.send_message(u_id,
                         cont.pars_hh_set_empl_t,
                         reply_markup=dyn_markup)

        cur_text = mod.decode_lst(req_stor[u_id]['hh_req']['employer_id'],
                                  cont.empl_g)

        bot.send_message(u_id,
                         f'Текущее значение ⬇️\n{cur_text}',
                         reply_markup=dyn_markup)

    else:
        bot.send_message(u_id,
                         cont.invalid_command_t,
                         reply_markup=keys.gen_dyn_keys(cont.ind_g.values(),
                                                        req_stor[u_id]['hh_req']['industry'],
                                                        cont.ind_g_inv))

    return


# МЕНЮ - парсер - hh.ru - компании
@bot.message_handler(func=lambda message:
                     mod.act_state_msg(message) == 'Парсинг-hh.ru-компании',
                     content_types=['text'])
def pars_hh_req_employer(message):

    u_id = message.chat.id
    m_text = message.text

    if req_stor.setdefault(u_id, 0) == 0:
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Старт',
                        'empty_req_error',
                        m_text))
        bot.send_message(u_id,
                         cont.empty_req_error_t,
                         reply_markup=keys.start_m)
        w_ist['hh'] = {}

        return

    if m_text in cont.empl_g.values():

        if cont.empl_g_inv[m_text] == [None] or req_stor[u_id]['hh_req']['employer_id'] == [None]:
            req_stor[u_id]['hh_req']['employer_id'] = [cont.empl_g_inv[m_text]]

        else:
            req_stor[u_id]['hh_req']['employer_id'].append(cont.empl_g_inv[m_text])

        dyn_markup = keys.gen_dyn_keys(cont.empl_g.values(),
                                       req_stor[u_id]['hh_req']['employer_id'],
                                       cont.empl_g_inv)

        bot.send_message(u_id,
                         cont.filter_accept_t,
                         reply_markup=dyn_markup)

        cur_text = mod.decode_lst(req_stor[u_id]['hh_req']['employer_id'],
                                  cont.empl_g)

        bot.send_message(u_id,
                         f'Текущее значение ⬇️\n{cur_text}',
                         reply_markup=dyn_markup)

    elif m_text == '➡️ Далее':
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Парсинг-hh.ru-опыт',
                        'custom_f',
                        m_text))

        dyn_markup = keys.gen_dyn_keys(cont.exp_g.values(),
                                       req_stor[u_id]['hh_req']['experience'],
                                       cont.exp_g_inv)

        bot.send_message(u_id,
                         cont.pars_hh_set_exp_t,
                         reply_markup=dyn_markup)

        cur_text = mod.decode_lst(req_stor[u_id]['hh_req']['experience'],
                                  cont.exp_g)

        bot.send_message(u_id,
                         f'Текущее значение ⬇️\n{cur_text}',
                         reply_markup=dyn_markup)

    else:
        bot.send_message(u_id,
                         cont.invalid_command_t,
                         reply_markup=keys.keys.gen_dyn_keys(cont.empl_g.values(),
                                                             req_stor[u_id]['hh_req']['employer_id'],
                                                             cont.empl_g_inv))

    return


# МЕНЮ - парсер - hh.ru - требуемый опыт
@bot.message_handler(func=lambda message:
                     mod.act_state_msg(message) == 'Парсинг-hh.ru-опыт',
                     content_types=['text'])
def pars_hh_req_exp(message):

    u_id = message.chat.id
    m_text = message.text

    if req_stor.setdefault(u_id, 0) == 0:
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Старт',
                        'empty_req_error',
                        m_text))
        bot.send_message(u_id,
                         cont.empty_req_error_t,
                         reply_markup=keys.start_m)
        w_ist['hh'] = {}

        return

    if m_text in cont.exp_g.values():

        if cont.exp_g_inv[m_text] == [None] or req_stor[u_id]['hh_req']['experience'] == [None]:
            req_stor[u_id]['hh_req']['experience'] = [cont.exp_g_inv[m_text]]

        else:
            req_stor[u_id]['hh_req']['experience'].append(cont.exp_g_inv[m_text])

        dyn_markup = keys.gen_dyn_keys(cont.exp_g.values(),
                                       req_stor[u_id]['hh_req']['experience'],
                                       cont.exp_g_inv)

        bot.send_message(u_id,
                         cont.filter_accept_t,
                         reply_markup=dyn_markup)

        cur_text = mod.decode_lst(req_stor[u_id]['hh_req']['experience'],
                                  cont.exp_g)

        bot.send_message(u_id,
                         f'Текущее значение ⬇️\n{cur_text}',
                         reply_markup=dyn_markup)

    elif m_text == '➡️ Далее':
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Парсинг-hh.ru-трудоустройство',
                        'custom_f',
                        m_text))

        dyn_markup = keys.gen_dyn_keys(cont.employment_g.values(),
                                       req_stor[u_id]['hh_req']['employment'],
                                       cont.employment_g_inv)

        bot.send_message(u_id,
                         cont.pars_hh_set_employment_t,
                         reply_markup=dyn_markup)

        cur_text = mod.decode_lst(req_stor[u_id]['hh_req']['employment'],
                                  cont.employment_g)

        bot.send_message(u_id,
                         f'Текущее значение ⬇️\n{cur_text}',
                         reply_markup=dyn_markup)

    else:
        bot.send_message(u_id,
                         cont.invalid_command_t,
                         reply_markup=keys.keys.gen_dyn_keys(cont.exp_g.values(),
                                                             req_stor[u_id]['hh_req']['experience'],
                                                             cont.exp_g_inv))

    return


# МЕНЮ - парсер - hh.ru - формат трудоустройства
@bot.message_handler(func=lambda message:
                     mod.act_state_msg(message) == 'Парсинг-hh.ru-трудоустройство',
                     content_types=['text'])
def pars_hh_req_employment(message):

    u_id = message.chat.id
    m_text = message.text

    if req_stor.setdefault(u_id, 0) == 0:
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Старт',
                        'empty_req_error',
                        m_text))
        bot.send_message(u_id,
                         cont.empty_req_error_t,
                         reply_markup=keys.start_m)
        w_ist['hh'] = {}

        return

    if m_text in cont.employment_g.values():

        if cont.employment_g_inv[m_text] == [None] or req_stor[u_id]['hh_req']['employment'] == [None]:
            req_stor[u_id]['hh_req']['employment'] = [cont.employment_g_inv[m_text]]

        else:
            req_stor[u_id]['hh_req']['employment'].append(cont.employment_g_inv[m_text])

        dyn_markup = keys.gen_dyn_keys(cont.employment_g.values(),
                                       req_stor[u_id]['hh_req']['employment'],
                                       cont.employment_g_inv)

        bot.send_message(u_id,
                         cont.filter_accept_t,
                         reply_markup=dyn_markup)

        cur_text = mod.decode_lst(req_stor[u_id]['hh_req']['employment'],
                                  cont.employment_g)

        bot.send_message(u_id,
                         f'Текущее значение ⬇️\n{cur_text}',
                         reply_markup=dyn_markup)

    elif m_text == '➡️ Далее':
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Парсинг-hh.ru-график',
                        'custom_f',
                        m_text))

        dyn_markup = keys.gen_dyn_keys(cont.sched_g.values(),
                                       req_stor[u_id]['hh_req']['schedule'],
                                       cont.sched_g_inv)

        bot.send_message(u_id,
                         cont.pars_hh_set_sched_t,
                         reply_markup=dyn_markup)

        cur_text = mod.decode_lst(req_stor[u_id]['hh_req']['schedule'],
                                  cont.sched_g)

        bot.send_message(u_id,
                         f'Текущее значение ⬇️\n{cur_text}',
                         reply_markup=dyn_markup)

    else:
        bot.send_message(u_id,
                         cont.invalid_command_t,
                         reply_markup=keys.gen_dyn_keys(cont.employment_g.values(),
                                                        req_stor[u_id]['hh_req']['employment'],
                                                        cont.employment_g_inv))

    return


# МЕНЮ - парсер - hh.ru - типы графика
@bot.message_handler(func=lambda message:
                     mod.act_state_msg(message) == 'Парсинг-hh.ru-график',
                     content_types=['text'])
def pars_hh_req_sched(message):

    u_id = message.chat.id
    m_text = message.text

    if req_stor.setdefault(u_id, 0) == 0:
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Старт',
                        'empty_req_error',
                        m_text))
        bot.send_message(u_id,
                         cont.empty_req_error_t,
                         reply_markup=keys.start_m)
        w_ist['hh'] = {}

        return

    if m_text in cont.sched_g.values():

        if cont.sched_g_inv[m_text] == [None] or req_stor[u_id]['hh_req']['schedule'] == [None]:
            req_stor[u_id]['hh_req']['schedule'] = [cont.sched_g_inv[m_text]]

        else:
            req_stor[u_id]['hh_req']['schedule'].append(cont.sched_g_inv[m_text])

        dyn_markup = keys.gen_dyn_keys(cont.sched_g.values(),
                                       req_stor[u_id]['hh_req']['schedule'],
                                       cont.sched_g_inv)

        bot.send_message(u_id,
                         cont.filter_accept_t,
                         reply_markup=dyn_markup)

        cur_text = mod.decode_lst(req_stor[u_id]['hh_req']['schedule'],
                                  cont.sched_g)

        bot.send_message(u_id,
                         f'Текущее значение ⬇️\n{cur_text}',
                         reply_markup=dyn_markup)

    elif m_text == '➡️ Далее':
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Парсинг-hh.ru-старт',
                        'custom_f',
                        m_text))
        bot.send_message(u_id,
                         cont.start_pars_hh_t,
                         reply_markup=keys.start_pars_hh_m)

    else:
        bot.send_message(u_id,
                         cont.invalid_command_t,
                         reply_markup=keys.gen_dyn_keys(cont.sched_g.values(),
                                                        req_stor[u_id]['hh_req']['schedule'],
                                                        cont.sched_g_inv))

    return


# МЕНЮ - парсер - hh.ru - запуск парсера
@bot.message_handler(func=lambda message:
                     mod.act_state_msg(message) == 'Парсинг-hh.ru-старт',
                     content_types=['text'])
def pars_hh_start(message):

    u_id = message.chat.id
    m_text = message.text

    if req_stor.setdefault(u_id, 0) == 0:
        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Старт',
                        'empty_req_error',
                        m_text))
        bot.send_message(u_id,
                         cont.empty_req_error_t,
                         reply_markup=keys.start_m)
        w_ist['hh'] = {}

        return

    if m_text in keys.start_pars_hh_b:

        fc = mod.prew_time_forecast(len(req_stor[u_id]['date_range'][0]))

        fc_from = time.strftime("%H:%M:%S", time.gmtime(int(fc[0])))
        fc_to = time.strftime("%H:%M:%S", time.gmtime(int(fc[1])))

        fc_finish = dt.datetime.now() + dt.timedelta(seconds=fc[1])

        w_ist['hh']['fc_finish'] = fc_finish.strftime('%d.%m.%Y г. %H:%M')

        bot.send_message(u_id,
                         f'Длительность:\nОт: {fc_from}\nДо: {fc_to}',
                         reply_markup=keys.start_m)

        con_db.set_val(que.set_state_q,
                       (u_id,
                        'Старт',
                        'ordinary',
                        m_text))

        res = hh_core.get_hh_pages(u_id, req_stor)

        if res[0] > 9:
            path = infograph.create_hh_report(u_id, req_stor)

            bot.send_message(u_id,
                             f'Обработано вакансий: {res[0]}\nОт {res[1]} компаний',
                             reply_markup=keys.back_m)

            bot.send_document(u_id,
                              open(r''+path, 'rb'))

            if req_stor[u_id]['user_req']['req_type'] == 'full':
                hh_core.get_hh_vac(u_id, req_stor)

            req_stor.pop(u_id, 0)
            w_ist['hh'] = {}

        else:
            bot.send_message(u_id,
                             cont.short_df_except_t,
                             reply_markup=keys.back_m)
            req_stor.pop(u_id, 0)
            w_ist['hh'] = {}

    else:
        bot.send_message(u_id,
                         cont.invalid_command_t,
                         keys.start_pars_hh_m)

    return


# Обращение к серверу
bot.polling(none_stop=True)
