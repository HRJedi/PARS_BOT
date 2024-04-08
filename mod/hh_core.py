# This Python file uses the following encoding: utf-8

import requests
import json as j
import datetime as dt
import uuid
import os
import time
import shutil
import pandas as pd
from statistics import mean
from bs4 import BeautifulSoup as soup
from database import con_db, que


temp_hh_path = '/root/PARS_BOT/temp/hh_res/'

setup = {'page_t': 0.5,
         'drange_t': 60,
         'trans_shutoff': 20,
         'vac_t': 0.25,
         'exc_t': 60,
         'vac_set_t': 20,
         'exc_limit_prew': 5,
         'exc_limit_deep': 5}


# Проверка наличия элемента в словаре - На вход словарь и набор ключей (1-3)
def d_check(d, val_t, default=None):
    try:

        if len(val_t) == 1:
            res = d[val_t[0]]

        elif len(val_t) == 2:
            res = d[val_t[0]][val_t[1]]

        elif len(val_t) == 3:
            res = d[val_t[0]][val_t[1]][val_t[2]]

        else:
            res = default

    except BaseException:
        res = default

    return res


# Получить и преобразовать актуальный перечень регионов
def pick_areas_dict(country='113'):

    res_d = {}

    with requests.get('https://api.hh.ru/areas') as req:
        cont = j.loads(req.content.decode())

    temp = [d for d in cont if d['id'] == country]

    for d in cont:
        if d['id'] == country:
            temp = d
            break

    for reg in temp['areas']:
        res_d[int(reg['id'])] = reg['name']
        temp_lst = []

        for l1 in reg['areas']:
            temp_lst.append(int(l1['id']))

        for elem in temp_lst:
            res_d[elem] = reg['name']

    return res_d


def taged_vac_name(str_vac_name):

    if str_vac_name is None:

        return 'ND'

    ref = str_vac_name.lower()
    res = 'Сотрудник'
    tags_d = {'Junior': ['junior', 'начинающий', 'без опыта', 'джуниор'],
              'Middle': ['middle', 'midle', 'мидл'],
              'Senior': ['senior', 'синьер', 'сеньёр', 'сеньйор'],
              'Lead': ['lead'],
              'Старший/Ведущий': ['старший', 'ведущий', 'главный'],
              'Руководитель': ['начальник', 'руководител', 'директор', 'прораб'],
              'Стажер': ['стажёр', 'стажер', 'стажировка', 'практикант'],
              'Ассистент': ['ассистент', 'асистент', 'помощник', 'помошник']}

    for name, tags in tags_d.items():

        for tag in tags:

            if tag in ref and res != 'Сотрудник':
                res = 'Мультивакансия'
                break

            elif tag in ref:
                res = name
                break

        if res == 'Мультивакансия':
            break

    return res


# Генерация словаря для вставки в БД - замена None и [None]
def dict_for_insert(dic):

    res_d = {}

    for key, val in dic.items():

        if val is None:
            res_d[key] = 'ALL'

        elif val == [None]:
            res_d[key] = ['ALL']

        else:
            res_d[key] = val

    return res_d


# Убрать дубликаты и строки с пустым vac_id из df
def get_pure_df(df, filtred_col='vac_uuid'):

    df = df.drop_duplicates(subset=[filtred_col], keep='last')
    df = df[pd.notnull(df[filtred_col])]

    return df


# Добавить новый запрос в БД
def insert_new_req(u_id, u_dict):

    new_req = pd.DataFrame([u_dict[u_id]['user_req']])
    new_req_atr = pd.DataFrame([dict_for_insert(u_dict[u_id]['hh_req'])])

    with con_db.alch_eng.connect() as connect:

        new_req.to_sql('user_req',
                       connect,
                       schema='PARS_BOT',
                       if_exists='append',
                       index=False)

        new_req_atr.to_sql('hh_req',
                           connect,
                           schema='PARS_BOT',
                           if_exists='append',
                           index=False)

    return


# Запрос к API HH
def hh_req(user_id, users_req, from_date, to_date, p=0):
    par = {'text': users_req[user_id]['hh_req']['req_title'],
           'area': users_req[user_id]['hh_req']['area'],
           'industry': users_req[user_id]['hh_req']['industry'],
           'employer_id': users_req[user_id]['hh_req']['employer_id'],
           'experience': users_req[user_id]['hh_req']['experience'],
           'employment': users_req[user_id]['hh_req']['employment'],
           'schedule': users_req[user_id]['hh_req']['schedule'],
           'only_with_salary': users_req[user_id]['hh_req']['with_salary'],
           'search_field': users_req[user_id]['hh_req']['search_field'],
           'currency': users_req[user_id]['hh_req']['salary_cur'],
           'date_from': from_date,
           'date_to': to_date,
           'per_page': 50,
           'page': p}

    req = requests.get('https://api.hh.ru/vacancies', par)
    data = j.loads(req.content.decode())
    req.close()
    return data


# Получение страниц и превью вакансий по запросу
def get_hh_pages(user_id, users_req):

    start_time = time.time()
    exept_counter = 0
    range_count = len(users_req[user_id]['date_range'][0])
    compl_res = True

    # Отправка статуса начала анализа и времени
    con_db.set_val(que.set_req_start,
                   (dt.datetime.now(),
                    'prew analysis in process',
                    users_req[user_id]['req_uuid']))

    # Удалить temp если есть и создать новый
    shutil.rmtree(f'{temp_hh_path}{user_id}', ignore_errors=True)
    os.makedirs(f'{temp_hh_path}{user_id}', exist_ok=True)

    # Словарь для формирования DF
    main_d = {'user_req_uuid': [],  # ИЗ СЛОВАРЯ ЗАПРОСА
              'vac_uuid': [],  # Генерация при сборе позиций
              'published_at': [],  # vac['published_at']
              'created_at': [],  # vac['created_at']
              'vac_id': [],  # vac['id']
              'vac_link': [],  # vac['alternate_url']
              'vac_name': [],  # vac['name']
              'vac_name_tag': [],  # Вычисляемое - контекстный анализ
              'premium_vac': [],  # vac['premium']
              'region_name': [],  # ИЗ СЛОВАРЯ ВНУТРИ ФУНКЦИИ
              'city_name': [],  # vac['area']['name']
              'salary_from': [],  # vac['salary']['from']
              'salary_to': [],  # vac['salary']['to']
              'salary_avg': [],  # ВЫЧИСЛЯЕМОЕ ПОЛЕ
              'salary_cur': [],  # vac['salary']['currency']
              'salary_type': [],  # vac['salary']['gross'] НЕОБХОДИМО ПРЕОБРАЗОВАНИЕ
              'employer_id': [],  # vac['employer']['id']
              'employer_link': [],  # vac['employer']['alternate_url']
              'employer_name': [],  # vac['employer']['name']
              'it_accredited': [],  # vac['employer']['accredited_it_employer']
              'exp_criteria': [],  # vac['experience']['name']
              'schedule_type': [],  # vac['schedule']['name']
              'employment_type': [],  # vac['employment']['name']
              'archived_vac': [],  # vac['archived']
              'accept_wo_cv': [],  # vac['accept_incomplete_resumes']
              'with_test': [],  # vac['has_test']
              'with_resp_letter': []}  # vac['response_letter_required']

    # Словарь регионов
    regions = pick_areas_dict()

    for counter, from_date, to_date in zip(range(1, range_count+1),
                                           users_req[user_id]['date_range'][0],
                                           users_req[user_id]['date_range'][1]):

        #  Проверка кол-ва ошибок в рамках иттератора
        if exept_counter >= setup['exc_limit_prew']:
            compl_res = False
            break

        for page in range(0, 40):

            #  Проверка кол-ва ошибок в рамках иттератора
            if exept_counter >= setup['exc_limit_prew']:
                compl_res = False
                break

            try:

                res = hh_req(user_id,
                             users_req,
                             from_date,
                             to_date,
                             p=page)

                if len(res['items']) == 0:
                    break

                for data in res['items']:

                    data['id']

                    main_d['user_req_uuid'].append(users_req[user_id]['req_uuid'])
                    main_d['vac_uuid'].append(str(uuid.uuid4()))

                    date_p = dt.datetime.fromisoformat(data['published_at'].split('+')[0])
                    date_c = dt.datetime.fromisoformat(data['created_at'].split('+')[0])

                    main_d['published_at'].append(date_p)
                    main_d['created_at'].append(date_c)

                    main_d['vac_id'].append(d_check(data,
                                                    ('id',)))
                    main_d['vac_link'].append(d_check(data,
                                                      ('alternate_url', )))

                    vac_name = d_check(data, ('name',))

                    main_d['vac_name'].append(vac_name)
                    main_d['vac_name_tag'].append(taged_vac_name(vac_name))
                    main_d['premium_vac'].append(d_check(data,
                                                         ('premium',),
                                                         False))

                    loc_id = int(d_check(data, ('area', 'id')))

                    main_d['region_name'].append(d_check(regions,
                                                         (loc_id,), 'ND'))
                    main_d['city_name'].append(d_check(data,
                                                       ('area', 'name')))

                    if d_check(data, ('salary',)) is None:
                        main_d['salary_from'].append(None)
                        main_d['salary_to'].append(None)
                        main_d['salary_avg'].append(None)
                        main_d['salary_cur'].append(None)
                        main_d['salary_type'].append(None)

                    else:
                        s_from = d_check(data,
                                         ('salary', 'from'))
                        s_to = d_check(data,
                                       ('salary', 'to'))

                        main_d['salary_from'].append(s_from)
                        main_d['salary_to'].append(s_to)

                        if s_from is s_to is None:
                            main_d['salary_avg'].append(None)

                        elif None not in [s_from, s_to]:
                            main_d['salary_avg'].append(int(mean([s_from, s_to])))

                        elif s_from is None:
                            main_d['salary_avg'].append(int(s_to))
                        else:
                            main_d['salary_avg'].append(int(s_from))

                        main_d['salary_cur'].append(d_check(data,
                                                            ('salary', 'currency')))

                        s_type = d_check(data,
                                         ('salary', 'gross'))

                        if s_type is None:
                            main_d['salary_type'].append('ND')

                        elif s_type:
                            main_d['salary_type'].append('gross')

                        else:
                            main_d['salary_type'].append('net')

                    if d_check(data,
                               ('employer',)) is None:
                        main_d['employer_id'].append(0)
                        main_d['employer_link'].append(None)
                        main_d['employer_name'].append('ND')
                        main_d['it_accredited'].append(False)

                    else:
                        main_d['employer_id'].append(d_check(data,
                                                             ('employer', 'id'),
                                                             0))
                        main_d['employer_link'].append(d_check(data,
                                                               ('employer',
                                                                'alternate_url')))
                        main_d['employer_name'].append(d_check(data,
                                                               ('employer',
                                                                'name'),
                                                               'ND'))
                        main_d['it_accredited'].append(d_check(data,
                                                               ('employer',
                                                                'accredited_it_employer'),
                                                               False))

                    main_d['exp_criteria'].append(d_check(data,
                                                          ('experience', 'name'),
                                                          'ND'))
                    main_d['schedule_type'].append(d_check(data,
                                                           ('schedule', 'name'),
                                                           'ND'))
                    main_d['employment_type'].append(d_check(data,
                                                             ('employment', 'name'),
                                                             'ND'))

                    main_d['archived_vac'].append(d_check(data,
                                                          ('archived',),
                                                          False))
                    main_d['accept_wo_cv'].append(d_check(data,
                                                          ('accept_incomplete_resumes',),
                                                          False))
                    main_d['with_test'].append(d_check(data,
                                                       ('has_test',),
                                                       False))
                    main_d['with_resp_letter'].append(d_check(data,
                                                              ('response_letter_required',),
                                                              False))

                if (res['pages'] - page) <= 1:
                    break

            except BaseException:
                exept_counter += 1
                time.sleep(setup['exc_t'])
                pass

            time.sleep(setup['page_t'])

        if range_count > 1 or range_count != counter:
            time.sleep(setup['drange_t'])

    # DF с основной информацией о вакансии и запись в temp
    df_main = get_pure_df(pd.DataFrame(main_d), filtred_col='vac_id')
    df_main.to_pickle(f"{temp_hh_path}{user_id}/{users_req[user_id]['req_uuid']}.p")

    # Запись статистики запроса
    vac_count = len(df_main.index)
    empl_count = len(df_main['employer_id'].unique())

    users_req[user_id]['hh_req']['prew_exept_count'] = exept_counter
    users_req[user_id]['hh_req']['prew_vac_count'] = vac_count
    users_req[user_id]['hh_req']['prew_complete'] = compl_res
    res_time = int(time.time() - start_time)
    users_req[user_id]['hh_req']['prew_time_sec'] = res_time
    users_req[user_id]['user_req']['total_time_sec'] += res_time

    # Отправка статистики запроса в БД
    con_db.set_val(que.set_req_finish,
                   (dt.datetime.now(),
                    'prew analysis complete',
                    users_req[user_id]['user_req']['total_time_sec'],
                    users_req[user_id]['req_uuid']))

    con_db.set_val(que.set_hh_stat_p,
                   (users_req[user_id]['hh_req']['prew_exept_count'],
                    users_req[user_id]['hh_req']['prew_vac_count'],
                    users_req[user_id]['hh_req']['prew_time_sec'],
                    users_req[user_id]['hh_req']['prew_complete'],
                    users_req[user_id]['req_uuid']))

    if vac_count < 10 or users_req[user_id]['user_req']['req_type'] == 'only prew':
        con_db.set_val(que.archived_req,
                       (True,
                        users_req[user_id]['req_uuid']))

    return (vac_count, empl_count)


# Получение и запись в БД подробной информации о вакансии и работодателе
def get_hh_vac(user_id, users_req):

    # Обновить статус запроса
    con_db.set_val(que.new_req_stat,
                   ('deep analysis start',
                    users_req[user_id]['req_uuid']))

    start_time = time.time()
    time.sleep(setup['trans_shutoff'])
    exept_counter = 0
    vac_counter = 0
    compl_res = True

    # Дополнительные атрибуты вакансии
    atr_d = {'vac_uuid': [],  # ИЗ DF ЗАПРОСА
             'bill_type': [],  # vac['billing_type']['name']
             'branded_vac': [],  # vac['branded_description'] - true, если не None
             'accept_for_invalid': [],  # vac['accept_handicapped']
             'accept_for_kids': [],  # vac['accept_kids']
             'accept_for_temp_w': [],  # vac['accept_temporary']
             'quick_responses_vac': []}  # vac['quick_responses_allowed']

    # Описание вакансии
    desc_d = {'vac_uuid': [],  # ИЗ DF ЗАПРОСА
              'desc': []}  # vac['description']

    # Ключевые навыки вакансии
    ks_d = {'vac_uuid': [],  # ИЗ DF ЗАПРОСА
            'key_skill': []}  # vac['key_skills']['name']

    # Профессиональные роли вакансии
    roles_d = {'vac_uuid': [],  # ИЗ DF ЗАПРОСА
               'role': []}  # vac['professional_roles']['name']

    # Языки вакансии
    lang_d = {'vac_uuid': [],  # ИЗ DF ЗАПРОСА
              'lang': []}  # vac['languages']['name']

    # Водительское удостоверение вакансии
    dl_d = {'vac_uuid': [],  # ИЗ DF ЗАПРОСА
            'dl_type': []}  # vac['driver_license_types']['id']

    # Работодатель
    empl_d = {'vac_uuid': [],  # ИЗ DF ЗАПРОСА
              'empl_id': [],  # ИЗ DF ЗАПРОСА
              'type': []}  # vac['type']

    # Сферы деятельности работодателя
    empl_ind_d = {'vac_uuid': [],  # ИЗ DF ЗАПРОСА
                  'empl_id': [],  # ИЗ DF ЗАПРОСА
                  'industry': []}  # vac['industries']['name']

    temp_df = pd.read_pickle(
        f"{temp_hh_path}{user_id}/{users_req[user_id]['req_uuid']}.p")

    for ind, row in enumerate(temp_df.itertuples(index=False), 1):

        #  Проверка кол-ва ошибок в рамках иттератора
        if exept_counter >= setup['exc_limit_deep']:
            compl_res = False
            break

        # Отсечка - время ожидания
        if ind % 50 == 0:
            time.sleep(setup['vac_set_t'])

        try:
            with requests.get(f'https://api.hh.ru/vacancies/{row.vac_id}') as r:
                data = j.loads(r.content.decode())

            data['id']

            atr_d['vac_uuid'].append(row.vac_uuid)
            atr_d['bill_type'].append(d_check(data,
                                              ('billing_type', 'name')))
            atr_d['branded_vac'].append(d_check(data,
                                                ('branded_description',)) is not None)
            atr_d['accept_for_invalid'].append(d_check(data,
                                                       ('accept_handicapped',),
                                                       False))
            atr_d['accept_for_kids'].append(d_check(data,
                                                    ('accept_kids',),
                                                    False))
            atr_d['accept_for_temp_w'].append(d_check(data,
                                                      ('accept_temporary',),
                                                      False))
            atr_d['quick_responses_vac'].append(d_check(data,
                                                        ('quick_responses_allowed',),
                                                        False))

            if len(data['key_skills']) > 0:
                for elem in data['key_skills']:
                    ks_d['vac_uuid'].append(row.vac_uuid)
                    ks_d['key_skill'].append(elem['name'])

            if len(data['professional_roles']) > 0:
                for elem in data['professional_roles']:
                    roles_d['vac_uuid'].append(row.vac_uuid)
                    roles_d['role'].append(elem['name'])

            if len(data['languages']) > 0:
                for elem in data['languages']:
                    lang_d['vac_uuid'].append(row.vac_uuid)
                    lang_d['lang'].append(elem['name'])

            if len(data['driver_license_types']) > 0:
                for elem in data['driver_license_types']:
                    dl_d['vac_uuid'].append(row.vac_uuid)
                    dl_d['dl_type'].append(elem['id'])

            try:
                desc_d['desc'].append(soup(data['description'],
                                           'html.parser').text)
                desc_d['vac_uuid'].append(row.vac_uuid)

            except BaseException:
                desc_d['desc'].append('Bad description')
                desc_d['vac_uuid'].append(row.vac_uuid)

            vac_counter += 1
            time.sleep(setup['vac_t'])

        except BaseException:
            exept_counter += 1
            time.sleep(setup['exc_t'])
            pass

        if row.employer_id not in empl_d['empl_id'] and row.employer_id != 0:
            try:
                with requests.get(f'https://api.hh.ru/employers/{row.employer_id}') as r:
                    data = j.loads(r.content.decode())

                data['id']

                empl_d['vac_uuid'].append(row.vac_uuid)
                empl_d['empl_id'].append(row.employer_id)
                empl_d['type'].append(d_check(data, ('type',), 'ND'))

                if len(data['industries']) > 0:
                    for elem in data['industries']:
                        empl_ind_d['vac_uuid'].append(row.vac_uuid)
                        empl_ind_d['empl_id'].append(row.employer_id)
                        empl_ind_d['industry'].append(d_check(elem, ('name',), 'ND'))

                time.sleep(setup['vac_t'])

            except BaseException:
                exept_counter += 1
                time.sleep(setup['exc_t'])
                pass

    if exept_counter < setup['exc_limit_deep']:

        # Датафрейм для таблицы vac_atr
        df_atr = get_pure_df(pd.DataFrame(atr_d), 'vac_uuid')

        # Датафрейм для таблицы vac_desc
        df_desc = get_pure_df(pd.DataFrame(desc_d), 'vac_uuid')

        # Датафрейм для таблицы vac_key_skills
        df_ks = pd.DataFrame(ks_d)

        # Датафрейм для таблицы vac_roles
        df_r = pd.DataFrame(roles_d)

        # Датафрейм для таблицы vac_langs
        df_l = pd.DataFrame(lang_d)

        # Датафрейм для таблицы vac_driver_licenses
        df_dl = pd.DataFrame(dl_d)

        # Датафрейм для таблицы vac_empl
        df_empl = get_pure_df(pd.DataFrame(empl_d), 'vac_uuid')

        # Датафрейм для таблицы empl_industries
        df_empl_ind = pd.DataFrame(empl_ind_d)

        # Иморт df в бд

        with con_db.alch_eng.connect() as connect:

            temp_df.to_sql('hh_vac_main',
                           connect,
                           schema='PARS_BOT',
                           if_exists='append',
                           index=False)

            df_atr.to_sql('hh_vac_atr',
                          connect,
                          schema='PARS_BOT',
                          if_exists='append',
                          index=False)

            df_desc.to_sql('hh_vac_desc',
                           connect,
                           schema='PARS_BOT',
                           if_exists='append',
                           index=False)

            df_ks.to_sql('hh_vac_ks',
                         connect,
                         schema='PARS_BOT',
                         if_exists='append',
                         index=False)

            df_r.to_sql('hh_vac_roles',
                        connect,
                        schema='PARS_BOT',
                        if_exists='append',
                        index=False)

            df_l.to_sql('hh_vac_langs',
                        connect,
                        schema='PARS_BOT',
                        if_exists='append',
                        index=False)

            df_dl.to_sql('hh_vac_dl',
                         connect,
                         schema='PARS_BOT',
                         if_exists='append',
                         index=False)

            df_empl.to_sql('hh_vac_empl',
                           connect,
                           schema='PARS_BOT',
                           if_exists='append',
                           index=False)

            df_empl_ind.to_sql('hh_empl_ind',
                               connect,
                               schema='PARS_BOT',
                               if_exists='append',
                               index=False)

        #  shutil.rmtree(f'{temp_hh_path}{user_id}', ignore_errors=True)

    # Запись статистики запроса
    users_req[user_id]['hh_req']['deep_exept_count'] = exept_counter
    users_req[user_id]['hh_req']['deep_vac_count'] = vac_counter
    users_req[user_id]['hh_req']['deep_complete'] = compl_res
    res_time = int(time.time() - start_time)
    users_req[user_id]['hh_req']['deep_time_sec'] = res_time
    users_req[user_id]['user_req']['total_time_sec'] += res_time

    # Отправка статистики запроса в БД
    con_db.set_val(que.set_req_finish,
                   (dt.datetime.now(),
                    'deep analysis complete',
                    users_req[user_id]['user_req']['total_time_sec'],
                    users_req[user_id]['req_uuid']))

    con_db.set_val(que.set_hh_stat_d,
                   (users_req[user_id]['hh_req']['deep_exept_count'],
                    users_req[user_id]['hh_req']['deep_vac_count'],
                    users_req[user_id]['hh_req']['deep_time_sec'],
                    users_req[user_id]['hh_req']['deep_complete'],
                    users_req[user_id]['req_uuid']))

    return
