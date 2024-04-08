# This Python file uses the following encoding: utf-8

import datetime as dt
import uuid
import re
from mod import hh_core as hh
from database import con_db, que

#  time.strftime("%H:%M:%S", time.gmtime(int(total_time)))

req_name_stoplist = '|\/@%*'
req_title_stoplist = ['(', ')']

check_date_dict = {'n': list('0123456789.'),
                   'sep': ['-', '—', '—', ',', ';']}


chunk_size = {5: 2,
              10: 3,
              20: 4,
              25: 5,
              30: 6,
              35: 7,
              40: 8,
              45: 9,
              50: 10,
              55: 11,
              60: 12}


# Новый пользователь
def new_user_reg(message):

    if con_db.get_val(que.init_user_q,
                      (message.chat.id,))[0] == 0:
        uid = message.chat.id
        f_name = message.from_user.first_name
        l_name = message.from_user.last_name
        u_name = message.from_user.username
        con_db.set_val(que.new_user_q,
                       (uid,
                        f_name,
                        l_name,
                        u_name))
    return


# Получить актуальный стейт юзера для сообщений
def act_state_msg(message):
    state = con_db.get_val(que.get_state_q,
                           (message.chat.id,))
    return state[0]


# Получить актуальный стейт юзера для вызова
def act_state_call(call):
    state = con_db.get_val(que.get_state_q,
                           (call.message.chat.id,))[0]
    return state


# ВЗАИМОДЕЙСТВИЕ С ПАРСЕРОМ
# Инициирование нового запроса на парсинг HH
def init_hh_req(user_id, main_d, r_type):

    today = dt.datetime.now()
    next_day = today.date() + dt.timedelta(days=1)
    new_uuid = str(uuid.uuid4())

    main_d[user_id] = {'req_uuid': new_uuid,
                       'date_range': ((today.date().strftime('%Y-%m-%d'),),
                                      (next_day.strftime('%Y-%m-%d'),)),

                       'user_req': {'user_id': user_id,
                                    'req_uuid': new_uuid,
                                    'req_create': today,
                                    'req_type': r_type,
                                    'pars_source': 'HH.RU',
                                    'req_name': 'Новый запрос',
                                    'total_time_sec': 0},

                       'hh_req': {'req_uuid': new_uuid,
                                  'date_from': today.date(),
                                  'date_to': next_day,
                                  'search_field': 'name',
                                  'req_title': '',
                                  'area': ['113'],
                                  'industry': [None],
                                  'employer_id': [None],
                                  'experience': [None],
                                  'employment': [None],
                                  'schedule': [None],
                                  'with_salary': True,
                                  'salary_cur': 'RUR',
                                  'prew_exept_count': 0,
                                  'prew_vac_count': 0,
                                  'prew_time_sec': 0,
                                  'prew_complete': False,
                                  'deep_exept_count': 0,
                                  'deep_vac_count': 0,
                                  'deep_time_sec': 0,
                                  'deep_complete': False}}
    return


# Проверка названия нового запроса - На выходе кортеж:
# [0] - код результата проверки (int),
# [1] - преобразованная строка в нижнем регистре
def check_req_name(str_req_name):
    temp_name = re.sub(r'\s+', ' ', str_req_name.strip()).lower()

    if len(temp_name) > 50:
        return (1, str_req_name)
    elif sum(list(map(lambda sym: int(sym in temp_name), req_name_stoplist))) > 0:
        return (2, str_req_name)
# ДОПОЛНИТЬ - ПРОВЕРКА НАЛИЧИЯ НАЗВАНИЯ В БАЗЕ!

    return (0, temp_name)


# Преобразование строки пользовательского запроса и исключений
# На выходе строка поискового запроса с перечнем стоп-слов
def transform_req_str(req_str, exclusions=''):
    temp_req = re.sub(r'\s+', ' ', req_str.strip()).lower()
    temp_req = temp_req.replace(' и ', ' AND ')
    temp_req = temp_req.replace(' или ', ' OR ')

    if len(exclusions) > 0:
        temp_exclusions = exclusions.replace('.', ';')
        temp_exclusions = ' NOT '.join(temp_exclusions.split(';'))
        temp_exclusions = re.sub(r'\s+', ' ', temp_exclusions.strip())
        return f'({temp_req}) NOT {temp_exclusions}'
    return f'{temp_req}'


# Проверка даты - На выходе кортеж:
# [0] - код результата проверки (int),
# [1] кортеж - одна или две даты по возрастанию
def check_date(str_date):
    temp_str = ''

    for elem in str_date.lower():

        if elem in check_date_dict['n']:
            temp_str += elem

        elif elem in check_date_dict['sep']:
            temp_str += '-'

    if len(temp_str) < 8:
        return (1, (str_date,))

    elif len(temp_str) > 21:
        return (2, (str_date,))

    elif len(temp_str) > 10 and temp_str.count('-') != 1:
        return (3, (str_date,))

    temp_date = ''
    temp_lst = []

    for pos in temp_str.split('-'):

        try:
            temp_date = dt.datetime.strptime(pos, '%d.%m.%Y').date()

            if dt.datetime.today().date() + dt.timedelta(days=1) > temp_date:
                temp_lst.append(temp_date)
            else:
                return (4, (str_date,))

        except ValueError:
            return (5, (str_date,))

    if len(temp_lst) > 1 and max(temp_lst) - min(temp_lst) > dt.timedelta(days=60):
        return (6, (str_date,))

    res = (0, tuple(sorted(temp_lst)))
    return res


# На выходе кортеж с двумя кортежами из дат в формате ISO (str):
# [0] - От даты
# [1] - До даты
def date_to_range(date_tuple):

    if len(date_tuple) == 1:
        st_date = (date_tuple[0].strftime('%Y-%m-%d'),)
        fin_date = ((date_tuple[0] + dt.timedelta(days=1)).strftime('%Y-%m-%d'),)
        return (st_date, fin_date)

    elif date_tuple[1] - date_tuple[0] < dt.timedelta(days=5):
        st_date = (date_tuple[0].strftime('%Y-%m-%d'),)
        fin_date = (date_tuple[1].strftime('%Y-%m-%d'),)
        return (st_date, fin_date)

    date_dif = (date_tuple[1] - date_tuple[0]).days
    chunk = chunk_size[min(list(chunk_size), key=lambda x: abs(x-date_dif))]
    st_lst = []
    fin_lst = []
    part_size = int(date_dif / chunk)

    for part in range(chunk+1):
        if part + 1 == 1:
            st_lst.append(date_tuple[0])
            fin_lst.append(date_tuple[0] + dt.timedelta(days=part_size))
        elif part == chunk:

            if max(fin_lst) < date_tuple[1]:
                st_lst.append(max(fin_lst))
                fin_lst.append(date_tuple[1])

        else:
            st_lst.append(max(fin_lst))
            fin_lst.append(max(st_lst) + dt.timedelta(days=part_size))

    st_date = tuple(map(lambda d: d.strftime('%Y-%m-%d'), sorted(st_lst)))
    fin_date = tuple(map(lambda d: d.strftime('%Y-%m-%d'), sorted(fin_lst)))

    return (st_date, fin_date)


# Проверка запроса или стоп-слов - На выходе кортеж:
# [0] - код результата проверки (int),
# [1] исходная строка
def check_req_title(str_title):

    res = 0

    if len(str_title) > 150:
        res = 1

    for sym in req_title_stoplist:

        if sym in str_title:
            res = 2
            break

    return res

# Парсер занят


def pars_busy(name, st_dt, finish_dt):
    res = f"""
Парсер HH.ru занят, пожалуйста попробуйте позже ⏳

Запрос: 
✅ {name}

Запрос инициирован:
⏲ {st_dt}

Ожидаемое время завершения:
⏲ {finish_dt}
"""
    return res


# Расшифровка названия кодов для списков
# На выходе расшифрованные элементы списка с переносами строки
def decode_lst(lst, gloss):
    decoded_d = [gloss[key] for key in lst]
    res = '\n✔️ - ' + '\n✔️ - '.join(decoded_d)
    return res

# Расшифровка названия кодов для строки
# На выходе расшифрованная строка с переносом


def decode_str(string, gloss):
    decoded_str = gloss[string]
    res = '\n✔️ - ' + decoded_str
    return res


# Ожидаемая длительность предварительного анализа
# На выходе кортеж: [0] - секунд минимум, [1] - секунд максимум
def prew_time_forecast(d_count):

    timeout = hh.setup['drange_t'] * (d_count-1) + 3
    p_timeout = hh.setup['page_t'] + 0.25
    # except_timeout = hh.setup['exc_t'] * hh.setup['exc_limit_prew']
    min_time = timeout + (d_count * p_timeout)
    max_time = timeout + (40 * d_count * p_timeout) + (2*11)

    return (min_time, max_time)


# Ожидаемая длительность глубокого анализа
# На выходе кортеж: [0] - секунд минимум, [1] - секунд максимум
def deep_time_forecast(vac_count, empl_count):

    timeout = hh.setup['vac_set_t'] * (vac_count // 50) + 10 + hh.setup['trans_shutoff']
    v_timeout = hh.setup['vac_t'] + 0.1
    except_timeout = hh.setup['exc_t'] * hh.setup['exc_limit_deep']
    min_time = timeout + (vac_count * v_timeout) + (empl_count * v_timeout)
    max_time = min_time + except_timeout

    return (min_time, max_time)
