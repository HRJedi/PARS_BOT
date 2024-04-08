# This Python file uses the following encoding: utf-8

import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
from content import cont
from statistics import mean
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
from matplotlib import dates

temp_hh_path = '/root/PARS_BOT/temp/hh_res/'


# Дни недели
week_days = {0: 'Понедельник',
             1: 'Вторник',
             2: 'Среда',
             3: 'Четверг',
             4: 'Пятница',
             5: 'Суббота',
             6: 'Воскресенье'}

# Шрифты заголовка
main_header_font = {'family': 'serif',
                    'weight': None,
                    'size': 14
                    }


# Шрифты подзаголовов
sub_header_font = {'family': 'serif',
                   'color': 'black',
                   'weight': 'bold',
                   'size': 12
                   }

# Шрифты заголовков графиков
title_font = {'family': 'serif',
              'color': 'black',
              'weight': 'bold',
              'size': 9
              }

# Шрифты заголовков графиков - большие
big_title_font = {'family': 'serif',
                  'color': 'black',
                  'weight': 'bold',
                  'size': 12
                  }

# Шрифты дополнительного текста
main_text_font = {'family': 'serif',
                  'color': 'black',
                  'size': 12
                  }

# Шрифты акцентного текста
highlight_font = {'family': 'serif',
                  'color': 'firebrick',
                  'weight': 'bold',
                  'size': 14
                  }

# Шрифты дополнительных подписей
sub_text_font = {'family': 'serif',
                 'color': 'grey',
                 'weight': 'normal',
                 'size': 9,
                 }

# Шрифты подписей (pie)
pie_font = {'family': 'serif',
            'color': 'dimgrey',
            'size': 9
            }

# Шрифты информационного блока
info_font = {'family': 'serif',
             'color': 'dimgrey',
             'weight': 'normal',
             'size': 11
             }

# Шрифты информационного блока (Bold)
info_font_b = {'family': 'serif',
               'color': 'dimgrey',
               'weight': 'bold',
               'size': 10
               }

# Разделители секторов (pie)
pie_wedg = {"linewidth": 1,
            "edgecolor": "white"}


def cm_inch(value):

    return value/2.54


def give_me_your_money(cash):
    str_cash = '{0:,} ₽'.format(round(cash)).replace(',', ' ')
    return str_cash


def text_box(fig, x, y, w, h):
    text_block = fig.add_axes([x, y, w, h])
    text_block.spines['top'].set_visible(False)
    text_block.spines['right'].set_visible(False)
    text_block.spines['left'].set_visible(False)
    text_block.spines['bottom'].set_visible(False)
    text_block.get_xaxis().set_ticks([])
    text_block.get_yaxis().set_ticks([])

    return text_block


def new_page(fig, header, p_num, r_name=None, s_date=None, f_date=None):
    # Заголовок и позиция заголовка
    fig.suptitle(header,
                 fontproperties=main_header_font)
    plt.subplots_adjust(top=0.7)

    # Номер страницы
    page_num = text_box(fig, 0.94, 0.015, 0.02, 0.02)
    page_num.text(0.5, 0.5,
                  p_num,
                  fontdict=sub_text_font,
                  horizontalalignment='center',
                  va='center')

    if r_name is None:
        pass

    else:
        # Информация о запросе
        req_info_text = text_box(fig, 0.36, 0.911, 0.3, 0.03)
        req_info_text.text(0.5, 0.7,
                           r_name,
                           fontdict=sub_text_font,
                           horizontalalignment='center')
        req_info_text.text(0.5, 0.2,
                           f"{s_date} - {f_date}",
                           fontdict=sub_text_font,
                           horizontalalignment='center')

    return


def get_colormap(data_list, mode='n_sort'):
    colors = plt.get_cmap('Reds_r')(np.linspace(0.2, 0.65, len(data_list)))

    if mode == 'sort':
        temp = sorted([v for v in enumerate(data_list)],
                      reverse=True,
                      key=lambda v: v[1])
        res = sorted([(pos[0], col) for pos, col in zip(temp, colors)],
                     key=lambda v: v[0])
        res = tuple([tup[1] for tup in res])

    else:
        res = tuple(colors)

    return res


def pie_preset(pie, labels, header=None):
    pie.set_title(header,
                  fontdict=title_font)
    pie.axis('equal')
    plt.setp(labels,
             color='white',
             fontweight='bold')

    return


def barch_preset(barch, bar, title=None, label_fmt='%.1f%%', l_size=9, f_size=7):
    barch.set_title(title,
                    fontdict=title_font,
                    loc='left')
    barch.bar_label(bar,
                    label_type='edge',
                    color='dimgrey',
                    fontweight='bold',
                    fontsize=l_size,
                    padding=2,
                    fmt=label_fmt)
    barch.tick_params(axis='y',
                      labelsize=f_size,
                      pad=7,
                      colors='dimgrey')
    barch.spines['left'].set_color('dimgrey')
    barch.spines['top'].set_visible(False)
    barch.spines['right'].set_visible(False)
    barch.spines['bottom'].set_visible(False)
    barch.get_xaxis().set_ticks([])
    barch.invert_yaxis()

    return


def draw_line(f, x, y, w, h, color="r", l_size=0.2, mode='h'):
    elem = f.add_axes([x, y, w, h])

    if mode == 'h':
        dot1 = [0, 1]
        dot2 = [0.5, 0.5]
    else:
        dot1 = [0.5, 0.5]
        dot2 = [0, 1]

    elem.add_line(Line2D(dot1, dot2,
                         color=color,
                         linewidth=l_size,
                         fillstyle='none'))
    elem.spines['top'].set_visible(False)
    elem.spines['right'].set_visible(False)
    elem.spines['left'].set_visible(False)
    elem.spines['bottom'].set_visible(False)
    elem.get_xaxis().set_ticks([])
    elem.get_yaxis().set_ticks([])

    return elem


def f_reg(string):

    replace_d = {'регион': 'Рег.',
                 'область': 'Обл.',
                 'республика': 'Респ.',
                 'Регион': 'Рег.',
                 'Область': 'Обл.',
                 'Республика': 'Респ.'}
    res = string

    for key, val in replace_d.items():
        if key in res:
            res = res.replace(key, val)
            break

    return res


def gen_sal_cat(df, median_sal):

    # Словарь условий генерации
    ref_cond = {50000: (20000, 20000, 5),
                75000: (20000, 25000, 5),
                100000: (20000, 30000, 5),
                125000: (20000, 35000, 5),
                150000: (20000, 40000, 5),
                1000000: (20000, 50000, 5)}  # Start #Step #Clusters

    for med, cond in ref_cond.items():

        if median_sal < med:
            res = {f'Менее {cond[0]} ₽': len(df[df['salary_avg'] < cond[0]])}
            s_from = cond[0]
            for clust in range(cond[2]):
                s_to = s_from + cond[1]
                c_name = f'От {s_from} ₽\nДо {s_to} ₽'
                c_d = len(df[(df['salary_avg'] >= s_from) & (df['salary_avg'] < s_to)])
                res[c_name] = c_d
                s_from = s_to

            res[f'Свыше {s_from} ₽'] = len(df[df['salary_avg'] >= s_from])
            break

    return res


def radar_chart(fig, x, y, w, h, vals, labs):

    labels = np.array(labs)

    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
    stats = np.concatenate((vals, [vals[0]]))
    angles = np.concatenate((angles, [angles[0]]))

    r_chart = fig.add_axes([x, y, w, h], polar=True)

    # Ночь
    r_chart.fill(angles, [max(vals)]*3 + [0]*15 + [max(vals)]*7, color='grey', alpha=0.25)
    r_chart.plot(angles, stats, color='red', linewidth=1)
    r_chart.fill(angles, stats, color='red', alpha=0.25)
    r_chart.set_thetagrids(angles * 180/np.pi, labels=labs+(labs[0],))
    r_chart.grid(True, color='whitesmoke')
    r_chart.set_theta_offset(np.pi / 2)
    r_chart.set_yticklabels([])
    r_chart.spines['polar'].set_color('silver')
    r_chart.tick_params(axis='x',
                        labelsize=12,
                        pad=3,
                        colors='dimgrey')

    return


# Преобразовать словарь запроса в текстовый формат
def transform_req_d(user_id, req_d, empl_c):

    temp_r = {'date_range': req_d[user_id]['date_range']}

    for k, v in list(req_d[user_id]['user_req'].items()) + list(req_d[user_id]['hh_req'].items()):
        temp_r[k] = v

    temp_t = temp_r['req_title'].split(') ')

    new_req_t = temp_t[0].strip('()')
    new_req_t = new_req_t.replace(' AND ', ' И ')
    new_req_t = new_req_t.replace(' OR ', ' ИЛИ ')

    if len(new_req_t) > 50:
        new_req_t = new_req_t[:50] + '-\n- ' + new_req_t[50:]
        if len(new_req_t) > 105:
            new_req_t = new_req_t[:105] + '-\n- ' + new_req_t[105:]

    req_excl = temp_t[1].replace('NOT ', 'НЕ ') if len(temp_t) > 1 else 'Без исключений'

    if len(req_excl) > 50:
        req_excl = req_excl[:50] + '-\n- ' + req_excl[50:]
        if len(req_excl) > 105:
            req_excl = req_excl[:105] + '-\n- ' + req_excl[105:]

    total_time = time.strftime("%H:%M:%S", time.gmtime(int(temp_r['total_time_sec'])))

    def d_str(lst, r_di, li=4):
        try:
            res = ['\n'+r_di[elem] if n % li == 0 else r_di[elem]
                   for n, elem in enumerate(lst, 1)]
        except BaseException:
            return 'Недопустимое количество символов'

        return ' ,'.join(res)

    res = {'i_1': {'ID инициатора:': temp_r['user_id'],
                   'Источник данных:': temp_r['pars_source'],
                   'Тип анализа:': cont.a_mode_g[temp_r['req_type']],
                   'Время начала:': temp_r['req_create'].strftime('%d.%m.%Y г. %H:%M'),
                   'Время окончания:': dt.datetime.now().strftime('%d.%m.%Y г. %H:%M')},

           'i_2': {'Вакансий': temp_r['prew_vac_count'],
                   'Компаний': empl_c,
                   'Общее время': total_time,
                   'Ошибок': temp_r['prew_exept_count'],
                   'Прервано': 'Нет' if temp_r['prew_complete'] else 'Да'},

           'req_p1': {'UUID запроса:': temp_r['req_uuid'],
                      'Имя запроса:': temp_r['req_name'],
                      'Публикации ОТ:': temp_r['date_from'].strftime('%d.%m.%Y г.'),
                      'Публикации ДО:': temp_r['date_to'].strftime('%d.%m.%Y г.')},

           'req_p2': {'Текст запроса:': new_req_t,
                      'Исключая слова:': req_excl,
                      'Поля поиска:': cont.search_g[temp_r['search_field']],
                      'Указана зарплата:': 'Да' if temp_r['with_salary'] else 'Нет',
                      'Валюта вакансий:': temp_r['salary_cur'],
                      'Регион поиска:': d_str(temp_r['area'], cont.reg_g),
                      'Целевая индустрия:': d_str(temp_r['industry'], cont.ind_g),
                      'Фильтр компаний:': d_str(temp_r['employer_id'], cont.empl_g),
                      'Требуемый опыт:': d_str(temp_r['experience'], cont.exp_g),
                      'Тип занятости:': d_str(temp_r['employment'], cont.employment_g),
                      'График:': d_str(temp_r['schedule'], cont.sched_g)}}

    return res


def create_hh_report(user_id, users_req):

    target_df = pd.read_pickle(
        f"{temp_hh_path}{user_id}/{users_req[user_id]['req_uuid']}.p")

    # Название запроса
    req_name = users_req[user_id]['user_req']['req_name']

    # Диапазон анализа
    start_date_title = users_req[user_id]['hh_req']['date_from'].strftime('%d.%m.%Y')
    finish_date_title = users_req[user_id]['hh_req']['date_to'].strftime('%d.%m.%Y')

    # Извлечение эллементов из даты и времени публикации
    target_df['pub_date'] = target_df['published_at'].dt.date
    target_df['pub_wd'] = target_df['published_at'].dt.dayofweek
    target_df['pub_hour'] = target_df['published_at'].dt.hour

    # ДАННЫЕ - кол-во вакансий
    vac_d = len(dict(target_df['vac_id'].value_counts()))

    # ДАННЫЕ - Кол-во компаний
    comp_d = len(dict(target_df['employer_id'].value_counts()))

    # ДАННЫЕ - Доля активных вакансий
    archived_d = dict(target_df['archived_vac'].value_counts())
    active_part = archived_d.get(False, 0)

    if active_part == 0:
        active_part = 0

    else:
        active_part = (active_part / sum(tuple(archived_d.values())))*100

    # ДАННЫЕ - Теги вакансий (Доля)
    tags_d = dict(target_df['vac_name_tag'].value_counts(normalize=True))

    if len(tags_d) <= 5:
        labs_tags = tuple(tags_d.keys())
        vals_tags = tuple(map(lambda v: v*100,
                              tags_d.values()))
    else:
        labs_tags = tuple(tags_d.keys())[:5] + ('Другие теги',)
        vals_tags = tuple(map(lambda v: v*100,
                              tags_d.values()))[:5] + (sum(tuple(map(lambda v: v*100,
                                                                     tags_d.values()))[5:]),)

    # ДАННЫЕ - Доля вакансий доступных с неполным резюме
    wo_cv_d = dict(target_df['accept_wo_cv'].value_counts())
    labs_wo_cv = tuple(map(lambda v: 'Да' if v else 'Нет',
                           wo_cv_d.keys()))
    vals_wo_cv = tuple(wo_cv_d.values())

    # ДАННЫЕ - Доля вакансий с обязательным сопроводительным письмом
    resp_let_d = dict(target_df['premium_vac'].value_counts())
    labs_resp_let = tuple(map(lambda v: 'Да' if v else 'Нет',
                              resp_let_d.keys()))
    vals_resp_let = tuple(resp_let_d.values())

    # ДАННЫЕ - Доля вакансий с тестовым заданием
    test_d = dict(target_df['with_test'].value_counts())
    labs_test = tuple(map(lambda v: 'Да' if v else 'Нет',
                          test_d.keys()))
    vals_test = tuple(test_d.values())

    # ДАННЫЕ - Доля вакансий по типу зарплаты
    st_d = dict(target_df['salary_type'].value_counts())
    labs_st = tuple(map(lambda v: v.upper(),
                        st_d.keys()))
    vals_st = tuple(st_d.values())

    # ДАННЫЕ - Требования к стажу (Доля)
    exp_d = dict(target_df['exp_criteria'].value_counts(normalize=True))
    labs_exp = tuple(map(lambda v: v.replace(' до', '\nдо'),
                         exp_d.keys()))
    vals_exp = tuple(map(lambda v: v*100,
                         exp_d.values()))

    # ДАННЫЕ - Предлагаемый тип занятости (Доля)
    empl_d = dict(target_df['employment_type'].value_counts(normalize=True))
    labs_empl = tuple(map(lambda v: v.replace(' ', '\n', 1),
                          empl_d.keys()))
    vals_empl = tuple(map(lambda v: v*100,
                          empl_d.values()))

    # ДАННЫЕ - Предлагаемый тип графика (Доля)
    sched_d = dict(target_df['schedule_type'].value_counts(normalize=True))
    labs_sched = tuple(map(lambda v: v.replace(' ', '\n', 1),
                           sched_d.keys()))
    vals_sched = tuple(map(lambda v: v*100,
                           sched_d.values()))

    # ДАННЫЕ - Регионы (Абсолют)
    reg_d = dict(target_df['region_name'].value_counts())

    if len(reg_d) <= 9:
        labs_reg = tuple(map(lambda v: f_reg(v),
                             reg_d.keys()))
        vals_reg = tuple(reg_d.values())

    else:
        temp_labels = tuple(reg_d.keys())[:9]
        labs_reg = tuple(map(lambda v: f_reg(v),
                             temp_labels)) + ('Другие регионы',)
        vals_reg = tuple(reg_d.values())[:9] + (sum(tuple(reg_d.values())[9:]),)

    # ДАННЫЕ - Города (Абсолют)
    city_d = dict(target_df['city_name'].value_counts())

    if len(city_d) <= 9:
        labs_city = tuple(map(lambda v: v.split(' (')[0], city_d.keys()))
        vals_city = tuple(city_d.values())

    else:
        labs_city = tuple(map(lambda v: v.split(
            ' (')[0], tuple(city_d.keys())[:9])) + ('Другие города',)
        vals_city = tuple(city_d.values())[:9] + (sum(tuple(city_d.values())[9:]),)

    # ДАННЫЕ - все суммы
    s_lim = np.percentile(target_df['salary_avg'], [2, 98])

    # ДАННЫЕ - Средние значения ЗП
    avg_sal = dict(target_df[['salary_from', 'salary_to', 'salary_avg']].mean())

    # ДАННЫЕ - Медианные значения ЗП
    med_sal = dict(target_df[['salary_from', 'salary_to', 'salary_avg']].median())

    # ДАННЫЕ - Максимальные значения ЗП
    max_sal = dict(target_df[['salary_from', 'salary_to', 'salary_avg']].max())

    # ДАННЫЕ - Минимальные значения ЗП
    min_sal = dict(target_df[['salary_from', 'salary_to', 'salary_avg']].min())

    # ДАННЫЕ - Кластерный анализ ЗП
    sal_clust_d = gen_sal_cat(target_df, med_sal['salary_avg'])
    labs_sal_clust = tuple(sal_clust_d.keys())
    vals_sal_clust = tuple(map(lambda v: v/vac_d*100,
                               sal_clust_d.values()))

    # ДАННЫЕ - Наибольшая медианная зарплата по стажу
    exp_med_sal_d = dict(target_df.groupby('exp_criteria')[
        'salary_avg'].median().sort_values(ascending=False))
    labs_exp_med_sal = tuple(exp_med_sal_d.keys())
    vals_exp_med_sal = tuple(exp_med_sal_d.values())

    # ДАННЫЕ - Наибольшая медианная зарплата по тегу
    tags_med_sal_d = dict(target_df.groupby('vac_name_tag')[
        'salary_avg'].median().sort_values(ascending=False))

    if len(tags_med_sal_d) <= 6:
        labs_tags_med_sal = tuple(tags_med_sal_d.keys())
        vals_tags_med_sal = tuple(tags_med_sal_d.values())

    else:
        labs_tags_med_sal = tuple(tags_med_sal_d.keys())[:6] + ('Другие теги',)
        vals_tags_med_sal = tuple(tags_med_sal_d.values())[
            :6] + (mean(tuple(tags_med_sal_d.values())[6:]),)

    # ДАННЫЕ - Наибольшая медианная зарплата по компаниям
    comp_med_sal_d = dict(target_df.groupby('employer_name')[
        'salary_avg'].median().sort_values(ascending=False))

    if len(comp_med_sal_d) <= 12:
        temp = tuple(map(lambda v: v[:22] + '...' if len(v)
                     > 22 else v, comp_med_sal_d.keys()))
        labs_comp_med_sal = temp + ('Медиана выборки',)
        vals_comp_med_sal = tuple(comp_med_sal_d.values()) + (med_sal['salary_avg'],)

    else:
        temp = tuple(map(lambda v: v[:22] + '...' if len(v) >
                     22 else v, tuple(comp_med_sal_d.keys())[:12]))
        labs_comp_med_sal = temp + ('Медиана выборки',)
        vals_comp_med_sal = tuple(comp_med_sal_d.values())[:12] + (med_sal['salary_avg'],)

    # ДАННЫЕ - Наибольшая медианная зарплата по регионам
    reg_med_sal_d = dict(target_df.groupby('region_name')[
        'salary_avg'].median().sort_values(ascending=False))

    if len(reg_med_sal_d) <= 9:
        labs_reg_med_sal = tuple(map(lambda v: f_reg(v),
                                     reg_med_sal_d.keys())) + ('Медиана выборки',)
        vals_reg_med_sal = tuple(reg_med_sal_d.values()) + (med_sal['salary_avg'],)

    else:
        temp_labels = tuple(reg_med_sal_d.keys())[:9]
        labs_reg_med_sal = tuple(
            map(lambda v: f_reg(v),
                temp_labels)) + ('Медиана выборки',)
        vals_reg_med_sal = tuple(reg_med_sal_d.values())[:9] + (med_sal['salary_avg'],)

    # ДАННЫЕ - Наибольшая медианная зарплата по городам
    city_med_sal_d = dict(target_df.groupby('city_name')[
        'salary_avg'].median().sort_values(ascending=False))

    if len(city_med_sal_d) <= 9:
        labs_city_med_sal = tuple(map(lambda v: v.split(
            ' (')[0], city_med_sal_d.keys())) + ('Медиана выборки',)
        vals_city_med_sal = tuple(city_med_sal_d.values()) + (med_sal['salary_avg'],)

    else:
        labs_city_med_sal = tuple(map(lambda v: v.split(
            ' (')[0], tuple(city_med_sal_d.keys())[:9])) + ('Медиана выборки',)
        vals_city_med_sal = tuple(city_med_sal_d.values())[:9] + (med_sal['salary_avg'],)

    # ДАННЫЕ - Частота публикации по часам
    pub_hour_d = dict(target_df['pub_hour'].value_counts(normalize=True))
    pub_hour_d = {h: pub_hour_d.setdefault(
        h, 0) * 100 if h != 24 else pub_hour_d.setdefault(0, 0) for h in range(24, 0, - 1)}
    labs_pub_hour = tuple(pub_hour_d.keys())
    vals_pub_hour = tuple(pub_hour_d.values())

    # ДАННЫЕ - Частота публикации по дням недели
    pub_wd_d = dict(target_df['pub_wd'].value_counts(normalize=True))
    pub_wd_d = {week_days[wd]: pub_wd_d.setdefault(wd, 0) * 100 for wd in range(7)}
    labs_wd = tuple(pub_wd_d.keys())
    vals_wd = tuple(pub_wd_d.values())

    # ДАННЫЕ - Частота публикации по дням
    pub_date_d = dict(target_df['pub_date'].value_counts())
    pub_date_d = dict(sorted(pub_date_d.items(), key=lambda d: d[0]))
    labs_pub_date = tuple(pub_date_d.keys())
    vals_pub_date = tuple(pub_date_d.values())

    with PdfPages(f"{temp_hh_path}{user_id}/{users_req[user_id]['req_uuid']}.pdf") as pdf:

        # Страница 1
        # Область
        fig = plt.figure(figsize=(cm_inch(21), cm_inch(29.7)))

        # Заголовки, номера страниц
        new_page(fig,
                 '\nОсновная информация по запросу',
                 1,
                 req_name,
                 start_date_title,
                 finish_date_title)

        # Текстовый блок
        text_block = text_box(fig, 0.08, 0.75, 0.5, 0.15)

        temp_dict = {'вакансий найдено': vac_d,
                     'актуальных': f'{round(active_part,1)}%',
                     'компаний': f'От {comp_d}',
                     'регионах': f'В {len(reg_d)}',
                     'городов': f'Из {len(city_d)}'}
        start_y_loc = 0.9

        for key, val in temp_dict.items():

            text_block.text(0.2, start_y_loc,
                            val,
                            fontdict=highlight_font,
                            horizontalalignment='right',
                            va='center')
            text_block.text(0.22, start_y_loc,
                            key,
                            fontdict=main_text_font,
                            va='center')

            start_y_loc -= 0.2

        # Доля вакансий по тегу
        barch = fig.add_axes([0.735, 0.9 - len(labs_tags) * 0.025,
                              0.16, len(labs_tags) * 0.025])
        bar = barch.barh(np.arange(len(labs_tags)),
                         vals_tags,
                         linewidth=2.0,
                         edgecolor='w',
                         color=get_colormap(labs_tags),
                         align='center',
                         tick_label=labs_tags)
        barch_preset(barch,
                     bar,
                     f_size=10,
                     l_size=10)

        # Разделить основного блока
        draw_line(fig, 0.03, 0.73, 0.94, 0.01)

        # Генерация круговых диаграмм
        temp_dict = {'Отклик\nбез резюме:': (labs_wo_cv,
                                             vals_wo_cv),
                     'Обязательное\nсопр. письмо:': (labs_resp_let,
                                                     vals_resp_let),
                     'Обязательное\nтестовое задание:': (labs_test,
                                                         vals_test),
                     'Тип начисления\nзаработной платы:': (labs_st,
                                                           vals_st)}
        start_x_loc = 0.07

        for key, val in temp_dict.items():
            new_pie = fig.add_axes([start_x_loc, 0.51, 0.17, 0.17])
            patch, text, pcts = new_pie.pie(val[1],
                                            colors=get_colormap(val[1]),
                                            labels=val[0],
                                            labeldistance=1.2,
                                            autopct='%1.0f%%',
                                            textprops=pie_font,
                                            shadow=True,
                                            wedgeprops=pie_wedg,
                                            startangle=90)

            pie_preset(new_pie, pcts, key)

            start_x_loc += 0.23  # Шаг

        # Генерация барчартов второго уровня
        temp_dict = {'Стаж:\n': (labs_exp,
                                 vals_exp),
                     'Занятость:\n': (labs_empl,
                                      vals_empl),
                     'График:\n': (labs_sched,
                                   vals_sched)}
        start_x_loc = 0.15

        for key, val in temp_dict.items():

            barch = fig.add_axes([start_x_loc, 0.47 - len(val[1]) * 0.027,
                                  0.135, len(val[1]) * 0.027])
            bar = barch.barh(np.arange(len(val[1])),
                             val[1],
                             linewidth=2.0,
                             edgecolor='w',
                             color=get_colormap(val[1]),
                             align='center',
                             tick_label=val[0])
            barch_preset(barch,
                         bar,
                         key)

            start_x_loc += 0.315  # Шаг

        # Разделитель гео-блока
        geo_line = draw_line(fig, 0.03, 0.3, 0.94, 0.01)
        geo_line.text(0.5, -1.5,
                      'География:',
                      fontdict=sub_header_font,
                      horizontalalignment='center',
                      va='center')
        geo_line.text(0.5, -3.5,
                      'Количество опубликованных вакансий в городах и регионах.',
                      fontdict=sub_text_font,
                      horizontalalignment='center')

        # Генерация барчартов третьего уровня
        temp_dict = {'Регионы': (labs_reg,
                                 vals_reg),
                     'Города': (labs_city,
                                vals_city)}

        start_x_loc = 0.26

        for key, val in temp_dict.items():

            barch = fig.add_axes([start_x_loc,  0.235 - len(val[1]) * 0.02,
                                  0.165, len(val[1]) * 0.02])
            bar = barch.barh(np.arange(len(val[1])),
                             val[1],
                             linewidth=2.0,
                             edgecolor='w',
                             color=get_colormap(val[1]),
                             align='center',
                             tick_label=val[0])
            barch_preset(barch, bar, label_fmt='%.0f')

            start_x_loc += 0.46

        # Внутренний разделитель гео-блока
        draw_line(fig, 0.5, 0.033, 0.01, 0.21, mode='v')

        pdf.savefig()
        plt.close()

        # Страница 2
        # Область
        fig = plt.figure(figsize=(cm_inch(21), cm_inch(29.7)))

        # Заголовки, номера страниц
        new_page(fig,
                 '\nАнализ условий оплаты труда',
                 2,
                 req_name,
                 start_date_title,
                 finish_date_title)

        # Текстовый блок
        text_block = text_box(fig, 0.08, 0.75, 0.84, 0.15)

        # Показатели по итоговым суммам
        temp_tuple = ('Низ вилки:', 'Верх вилки:', 'Уср. вилка:')
        temp_dict = {'AVG:': tuple(avg_sal.values()),
                     'MED:': tuple(med_sal.values()),
                     'MAX:': tuple(max_sal.values()),
                     'MIN:': tuple(min_sal.values())}

        start_x_loc = 0.077

        for pos, header in enumerate(temp_tuple):
            text_block.text(start_x_loc, 0.9,
                            header,
                            fontdict=big_title_font,
                            va='center')

            start_y_loc = 0.7

            for key, val in temp_dict.items():

                text_block.text(start_x_loc - 0.08, start_y_loc,
                                key,
                                fontdict=main_text_font,
                                va='center')
                text_block.text(start_x_loc, start_y_loc,
                                give_me_your_money(val[pos]),
                                fontdict=highlight_font,
                                horizontalalignment='left',
                                va='center')
                start_y_loc -= 0.2
            start_x_loc += 0.37

        # Вертикальные разделители
        draw_line(fig, 0.345, 0.75, 0.01, 0.12, mode='v')
        draw_line(fig, 0.65, 0.75, 0.01, 0.12, mode='v')

        # Разделитель структурного анализа
        struct = draw_line(fig, 0.03, 0.73, 0.94, 0.01)
        struct.text(0.5, -1.5,
                    'Структурный анализ заявленной оплаты труда:',
                    fontdict=sub_header_font,
                    horizontalalignment='center',
                    va='center')
        struct.text(0.5, -3.5,
                    'Группы по усредненной вилке | Медиана по усредненной вилке.',
                    fontdict=sub_text_font,
                    horizontalalignment='center')

        # Анализ ЗП по категориям
        barch = fig.add_axes([0.26,  0.66 - len(sal_clust_d) * 0.045,
                              0.16, len(sal_clust_d) * 0.045])
        bar = barch.barh(np.arange(len(vals_sal_clust)),
                         vals_sal_clust,
                         linewidth=2.0,
                         edgecolor='w',
                         color=get_colormap(vals_sal_clust, 'sort'),
                         align='center',
                         tick_label=labs_sal_clust)
        barch_preset(barch,
                     bar,
                     f_size=11,
                     l_size=11)

        # Генерация барчартов второго уровня
        temp_dict = {'Стаж': (labs_exp_med_sal,
                              vals_exp_med_sal),
                     'Тег': (labs_tags_med_sal,
                             vals_tags_med_sal)}

        start_y_loc = 0.445

        for key, val in temp_dict.items():

            barch = fig.add_axes([0.735,  start_y_loc - len(val[1]) * 0.024,
                                  0.155, len(val[1]) * 0.024])
            bar = barch.barh(np.arange(len(val[1])),
                             val[1],
                             linewidth=2.0,
                             edgecolor='w',
                             color=get_colormap(val[1]),
                             align='center',
                             tick_label=val[0])
            barch_preset(barch,
                         bar,
                         label_fmt='%.0f',
                         f_size=10,
                         l_size=10)

            start_y_loc += 0.225

        # Внутренний разделитель структурного анализа
        draw_line(fig, 0.5, 0.33, 0.01, 0.34, mode='v')

        # Разделитель частотного анализа
        freq_anal = draw_line(fig, 0.03, 0.3, 0.94, 0.01)
        freq_anal.text(0.5, -1.5,
                       'Частотный анализ заявленной оплаты труда:',
                       fontdict=sub_header_font,
                       horizontalalignment='center',
                       va='center')
        freq_anal.text(0.5, -3.5,
                       'Исключены значения: <2-процентиля и >98 процентиля. По усредненной вилке.',
                       fontdict=sub_text_font,
                       horizontalalignment='center')

        # Гистограмма частотного анализа
        hst = fig.add_axes([0.05, 0.075, 0.9, 0.165])
        hst.spines['top'].set_visible(False)
        hst.spines['left'].set_visible(False)
        hst.spines['right'].set_visible(False)
        hst.get_yaxis().set_ticks([])

        if vac_d > 99:
            hst.hist(target_df['salary_avg'],
                     bins=25,
                     range=s_lim,
                     edgecolor='white',
                     color=get_colormap('1'))
            hst.spines['bottom'].set_color('dimgrey')
            hst.tick_params(axis='x',
                            labelsize=9,
                            pad=2,
                            colors='dimgrey')
        else:
            hst.text(0.5, 0.5,
                     'Частотный анализ не репрезентативен,\nПри выборке <100 вакансий.',
                     fontdict=highlight_font,
                     horizontalalignment='center',
                     va='center')
            hst.spines['bottom'].set_visible(False)
            hst.get_xaxis().set_ticks([])

        pdf.savefig()
        plt.close()

        # Страница 3
        # Область
        fig = plt.figure(figsize=(cm_inch(21), cm_inch(29.7)))

        # Заголовки, номера страниц
        new_page(fig,
                 '\nРейтинг условий оплаты труда',
                 3,
                 req_name,
                 start_date_title,
                 finish_date_title)

        # Текстовый блок
        text_block = text_box(fig, 0.08, 0.75, 0.84, 0.15)

        # Разделитель рейтинга компаний
        comp_rate = draw_line(fig, 0.03, 0.73, 0.94, 0.01)
        comp_rate.text(0.5, -1.5,
                       'Рейтинг организаций по заявленной оплате труда:',
                       fontdict=sub_header_font,
                       horizontalalignment='center',
                       va='center')
        comp_rate.text(0.5, -3.5,
                       'Наибольшая заявленная медианная оплата труда. По усредненной вилке.',
                       fontdict=sub_text_font,
                       horizontalalignment='center')

        # Рейтинг организаций
        barch = fig.add_axes([0.35,  0.66 - len(labs_comp_med_sal) * 0.025,
                              0.53, len(labs_comp_med_sal) * 0.025])
        bar = barch.barh(np.arange(len(labs_comp_med_sal)),
                         vals_comp_med_sal,
                         linewidth=2.0,
                         edgecolor='w',
                         color=get_colormap(labs_comp_med_sal)[0:-1] + ('silver',),
                         align='center',
                         tick_label=labs_comp_med_sal)
        barch_preset(barch,
                     bar,
                     label_fmt='%.0f',
                     f_size=11,
                     l_size=11)

        # Разделитель гео-блока
        geo_line = draw_line(fig, 0.03, 0.3, 0.94, 0.01)
        geo_line.text(0.5, -1.5,
                      'География:',
                      fontdict=sub_header_font,
                      horizontalalignment='center',
                      va='center')
        geo_line.text(0.5, -3.5,
                      'Наибольшая заявленная медианная оплата труда. По усредненной вилке.',
                      fontdict=sub_text_font,
                      horizontalalignment='center')

        # Генерация барчартов третьего уровня
        temp_dict = {'Регионы': (labs_reg_med_sal,
                                 vals_reg_med_sal),
                     'Города': (labs_city_med_sal,
                                vals_city_med_sal)}

        start_x_loc = 0.26

        for key, val in temp_dict.items():

            barch = fig.add_axes([start_x_loc,  0.235 - len(val[1]) * 0.02,
                                  0.165, len(val[1]) * 0.02])
            bar = barch.barh(np.arange(len(val[1])),
                             val[1],
                             linewidth=2.0,
                             edgecolor='w',
                             color=get_colormap(val[1])[0:-1] + ('silver',),
                             align='center',
                             tick_label=val[0])
            barch_preset(barch,
                         bar,
                         label_fmt='%.0f')

            start_x_loc += 0.46

        # Внутренний разделитель гео-блока
        draw_line(fig, 0.5, 0.033, 0.01, 0.21, mode='v')

        pdf.savefig()
        plt.close()

        # Страница 4
        # Область
        fig = plt.figure(figsize=(cm_inch(21), cm_inch(29.7)))

        # Заголовки, номера страниц
        new_page(fig,
                 '\nПериоды и частота публикаций',
                 4,
                 req_name,
                 start_date_title,
                 finish_date_title)

        # Текстовый блок
        text_block = text_box(fig, 0.08, 0.75, 0.84, 0.15)

        # Разделитель частоты публикаций
        comp_rate = draw_line(fig, 0.03, 0.73, 0.94, 0.01)
        comp_rate.text(0.5, -1.5,
                       'Относительная оценка частоты публикаций:',
                       fontdict=sub_header_font,
                       horizontalalignment='center',
                       va='center')
        comp_rate.text(0.5, -3.5,
                       'Доля по дням недели и часам. Обновления вакансии учитываются по последней дате.',
                       fontdict=sub_text_font,
                       horizontalalignment='center')

        # Частота публикаций по дням недели
        barch = fig.add_axes([0.26,  0.66 - len(labs_wd) * 0.045,
                              0.16, len(labs_wd) * 0.045])
        bar = barch.barh(np.arange(len(vals_wd)),
                         vals_wd,
                         linewidth=2.0,
                         edgecolor='w',
                         color=get_colormap(vals_wd[:5], 'sort') + ('silver', 'silver'),
                         align='center',
                         tick_label=labs_wd)
        barch_preset(barch,
                     bar,
                     f_size=11,
                     l_size=11)

        # Частота публикаций по времени
        radar_chart(fig, 0.58, 0.32, 0.35, 0.35, vals_pub_hour, labs_pub_hour)

        # Внутренний разделитель периода публикаций
        draw_line(fig, 0.5, 0.33, 0.01, 0.34, mode='v')

        # Разделитель частоты публикаций по датам
        freq_in_date = draw_line(fig, 0.03, 0.3, 0.94, 0.01)
        freq_in_date.text(0.5, -1.5,
                          'Абсолютная оценка частоты публикаций:',
                          fontdict=sub_header_font,
                          horizontalalignment='center',
                          va='center')
        freq_in_date.text(0.5, -3.5,
                          'Количество публикаций по дням. Обновления вакансии учитываются по последней дате.',
                          fontdict=sub_text_font,
                          horizontalalignment='center')

        # Частота публикаций по датам
        pub_in_date = fig.add_axes([0.05, 0.075, 0.9, 0.165])

        pub_in_date.spines['top'].set_visible(False)
        pub_in_date.spines['left'].set_visible(False)
        pub_in_date.spines['right'].set_visible(False)
        pub_in_date.get_yaxis().set_ticks([])

        if len(labs_pub_date) > 10:
            pub_in_date.plot(labs_pub_date,
                             vals_pub_date,
                             color='red',
                             lw=1)
            pub_in_date.fill_between(
                labs_pub_date, 0, vals_pub_date, color='red', alpha=0.25)

            pub_in_date.tick_params(rotation=45,
                                    axis='x',
                                    labelsize=9,
                                    pad=2,
                                    colors='dimgrey')
            pub_in_date.xaxis.set_major_formatter(dates.DateFormatter('%d-%m'))
            pub_in_date.spines['bottom'].set_color('dimgrey')

        else:
            pub_in_date.text(0.5, 0.5,
                             'Анализ частоты публикаций по дням не применим\nпри периоде оценки менее 7 дней.',
                             fontdict=highlight_font,
                             horizontalalignment='center',
                             va='center')
            pub_in_date.spines['bottom'].set_visible(False)
            pub_in_date.get_xaxis().set_ticks([])

        pdf.savefig()
        plt.close()

        # Страница 5
        # Область
        fig = plt.figure(figsize=(cm_inch(21), cm_inch(29.7)))

        # Заголовки, номера страниц
        new_page(fig,
                 '\nДетализация запроса',
                 5,
                 req_name,
                 start_date_title,
                 finish_date_title)

        result = transform_req_d(user_id, users_req, comp_d)

        # Текстовый блок - детализация
        text_block = text_box(fig, 0.08, 0.75, 0.4, 0.15)

        start_y_loc = 0.9
        for key, val in result['i_1'].items():

            text_block.text(0.45, start_y_loc,
                            key,
                            fontdict=info_font,
                            horizontalalignment='right')

            text_block.text(0.47, start_y_loc,
                            val,
                            fontdict=info_font_b,
                            horizontalalignment='left')
            start_y_loc -= 0.2

        # Текстовый блок - детализация 2
        text_block = text_box(fig, 0.52, 0.75, 0.4, 0.15)

        start_y_loc = 0.9
        for key, val in result['i_2'].items():

            text_block.text(0.65, start_y_loc,
                            key,
                            fontdict=info_font,
                            horizontalalignment='right')

            text_block.text(0.67, start_y_loc,
                            val,
                            fontdict=info_font_b,
                            horizontalalignment='left')
            start_y_loc -= 0.2

        # Внутренний разделитель блоков детализации
        draw_line(fig, 0.5, 0.75, 0.01, 0.15, mode='v')

        # Разделитель условий парсинга
        req_details = draw_line(fig, 0.03, 0.73, 0.94, 0.01)
        req_details.text(0.5, -1.5,
                         'Условия парсинга',
                         fontdict=sub_header_font,
                         horizontalalignment='center',
                         va='center')
        req_details.text(0.5, -3.5,
                         'Полный перечень применяемых параметров',
                         fontdict=sub_text_font,
                         horizontalalignment='center')

        # Текстовый блок - условия парсинга 1
        text_block = text_box(fig, 0.08, 0.05, 0.84, 0.62)

        start_y_loc = 0.99
        for key, val in result['req_p1'].items():

            text_block.text(0.25, start_y_loc,
                            key,
                            fontdict=info_font,
                            va='center',
                            horizontalalignment='right')

            text_block.text(0.27, start_y_loc,
                            val,
                            fontdict=info_font_b,
                            va='center',
                            horizontalalignment='left')
            start_y_loc -= 0.03

        # Текстовый блок - условия парсинга 2

        start_y_loc = 0.82

        for key, val in result['req_p2'].items():

            text_block.text(0.25, start_y_loc,
                            key,
                            fontdict=info_font,
                            va='center',
                            horizontalalignment='right')

            text_block.text(0.27, start_y_loc,
                            val,
                            fontdict=info_font_b,
                            va='center',
                            horizontalalignment='left')
            start_y_loc -= 0.08

        pdf.savefig()
        plt.close()

    return f"{temp_hh_path}{user_id}/{users_req[user_id]['req_uuid']}.pdf"
