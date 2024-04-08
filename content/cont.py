# This Python file uses the following encoding: utf-8
import datetime as dt


# Инвертировать словарь
def invert_d(d):
    res = {v: k for k, v in d.items()}
    return res


# СТИКЕРЫ
# HH.RU
hh_sticker = 'CAACAgIAAxkBAAECXspldexHoalpD3X8Vx4IBqNcn2QoLQACwjYAAlCZsUv1ovT-mYRjYDME'

# ПАРСИНГ
# Результаты проверки названия запросов
check_req_name = {0: 'Название действительно',
                  1: 'Название более 100 символов',
                  2: 'Название содержит недопустимые символы',
                  3: 'Такое название уже существует'}


# Результаты проверки дат введенных пользователем
check_date_res = {0: 'Дата действительна',
                  1: 'Введите хотя бы одно значение даты в формате ДД.ММ.ГГГГ',
                  2: 'Больше двух дат или использован неверный формат даты',
                  3: 'Неверный разделитель при вводе дат или неверный формат дат(ы)',
                  4: 'Дата / даты еще не наступили',
                  5: 'Несоответствие формату ДД.ММ.ГГГГ в дате/датах',
                  6: 'Диапазон дат не должен превышать 60 дней'}

# Результаты проверки запроса и исключений
check_req_title = {0: 'Запрос действителен',
                   1: 'Длинна запроса / исключений не должна превышать 150 символов',
                   2: 'Запрос содержит недопустимые символы'}


# Справочник режимов анализа
a_mode_g = {'only prew': 'Превью',
            'full': 'Полный'}

a_mode_g_inv = invert_d(a_mode_g)


# Справочник режимов фильтрации
filter_g = {'simple': 'По умолчанию',
            'custom': 'Кастомные'}

filter_g_inv = invert_d(filter_g)


# Справочник режимов поиска
search_g = {None: 'Везде',
            'name': 'В названии'}

search_g_inv = invert_d(search_g)


# Справочник регионов
reg_g = {'113': 'Вся Россия',
         '1': 'Москва',
         '2019': 'Московская обл.',
         '1828': 'Брянская обл.',
         '2': 'Санкт-Петербург',
         '145': 'Ленинградская обл.',
         '1624': 'Респ. Татарстан',
         '1020': 'Калининградская обл.'}

reg_113 = {'113': 'Вся Россия'}

reg_g_inv = invert_d(reg_g)

reg_113_inv = invert_d(reg_113)

reg_distr_preset = {'Дистрибьюция': ['1817', '1823', '1825', '19', '24', '26', '3',
                                     '1232', '88', '41', '1', '2040', '2044', '2019',
                                     '2041', '2085', '2085', '2092', '2039', '66', '1692',
                                     '69', '76', '78', '2', '56', '53', '1454', '8',
                                     '1444', '237', '2120', '1440', '131', '2115', '4',
                                     '95', '104', '83', '99', '1866', '58', '87', '47']}

city_g = {'113': 'Вся Россия',
          '1817': 'Строитель',
          '1823': 'Короча',
          '1825': 'Старый Оскол',
          '19': 'Брянск',
          '24': 'Волгоград',
          '26': 'Воронеж',
          '3': 'Екатеринбург',
          '1232': 'Березовский',
          '88': 'Казань',
          '41': 'Калининград',
          '1': 'Москва',
          '2040': 'Можайск',
          '2044': 'Наро-Фоминск',
          '2019': 'Дубна',
          '2041': 'Мытищи',
          '2085': 'Долгопрудный',
          '2092': 'Лобня',
          '2039': 'Люберцы',
          '66': 'Нижний Новгород',
          '1692': 'Кулебаки',
          '69': 'Вожово',
          '76': 'Ростов-на-Дону',
          '78': 'Самара',
          '2': 'Санкт-Петербург',
          '56': 'Курск',
          '53': 'Краснодар',
          '1454': 'Новороссийск',
          '8': 'Майкоп',
          '1444': 'Геленджик',
          '237': 'Сочи',
          '2120': 'Ялта',
          '1440': 'Анапа',
          '131': 'Симферополь',
          '2115': 'Евпатория',
          '4': 'Новосибирск',
          '95': 'Тюмень',
          '104': 'Челябинск',
          '83': 'Смоленск',
          '99': 'Уфа',
          '1866': 'Киров',
          '58': 'Липецк',
          '87': 'Тамбов',
          '47': 'Кемерово'}

city_g_inv = invert_d(city_g)


# Справочник индустрий
ind_g = {None: 'Все',
         '29': 'Сельское хозяйство',
         '15': 'Автомобильный бизнес',
         '5': 'Перевозки',
         '27': 'Продукты питания'}

ind_g_inv = invert_d(ind_g)


# Справочник работодателей
empl_g = {None: 'Все',
          '17275': 'Мираторг',
          '23186': 'Русагро',
          '1346': 'Черкизово',
          '53797': 'ЭФКО'}

empl_g_inv = invert_d(empl_g)


# Cправочник требуемого стажа
exp_g = {None: 'Все',
         'noExperience': 'Нет опыта',
         'between1And3': 'От 1 года до 3 лет',
         'between3And6': 'От 3 до 6 лет',
         'moreThan6': 'Более 6 лет'}

exp_g_inv = invert_d(exp_g)


# Cправочник типов трудоустройства
employment_g = {None: 'Все',
                'full': 'Полная',
                'part': 'Частичная',
                'project': 'Проектная',
                'volunteer': 'Волонтёрство',
                'probation': 'Стажировка'}

employment_g_inv = invert_d(employment_g)


# Cправочник графиков работы
sched_g = {None: 'Все',
           'fullDay': 'Полный день',
           'shift': 'Сменный график',
           'flexible': 'Гибкий график',
           'remote': 'Удаленная работа',
           'flyInFlyOut': 'Вахтовый метод'}

sched_g_inv = invert_d(sched_g)

# Пресеты дат
today = dt.datetime.now().date()
tomorrow = today + dt.timedelta(days=1)
date_preset = {'Сегодня': (today,
                           tomorrow),
               'Эта неделя': (today - dt.timedelta(days=dt.datetime.weekday(today)),
                              tomorrow),
               'Этот месяц': (today - dt.timedelta(days=int(today.strftime("%d"))-1),
                              tomorrow),
               '7 дней': (today - dt.timedelta(days=7),
                          tomorrow),
               '14 дней': (today - dt.timedelta(days=14),
                           tomorrow),
               '30 дней': (today - dt.timedelta(days=29),
                           tomorrow),
               '60 дней': (today - dt.timedelta(days=59),
                           tomorrow)}


discl = """
Дисклеймер"""

in_process_t = """
Раздел находится в разработке ⚙️"""

invalid_command_t = """
Текстовые комманды недоступны в этом меню - выберите предложенный вариант ⬇️"""

empty_req_error_t = """
Упс, произошла непредвиденная ошибка 🫤
Пожалуйста попробуйте повторить запрос 🔄"""

# Сообщение Старт
start_mesage = """
Главное меню
Предполагается, что тут должен быть полезный и умный текст, но его пока нет
MVP - есть MVP 🩼"""

# Сообщение описание парсинга и источников
pars_t = """
В качестве источников парсинга вакансий потенциально доступны несколько различных платформ 🔎
К сожалению, технически они сильно различаются и на текущий момент возможнен только парсинг вакансий с HH.RU 😶"""

# Сообщение выбор режима парсинга с HH.ru
pars_hh_mode_t = """
Какой режим парсинга необходимо использовать?

Краткий отчёт будет сформирован автоматически в формате pdf, вне зависимости от выбранного режима 📋

🔎 Превью - результаты запроса не будут сохранены.
Этот режим существенно быстрее и удобен для предваритальной оценки ⚡️

📊 Полный (В разработке) - результаты запроса сохраняются в базе данных.
После завершения анализа, подробные результаты будут доступны в интерактивном дашборде 🧮
Процесс парсинга может занимать до нескольких часов 🐌

"""

pars_hh_date_t = """
Введите дату(ы) в одном из форматов 📆

✔️ - ДД.ММ.ГГГГ - ДД.ММ.ГГГГ
✔️ - ДД.ММ.ГГГГ; ДД.ММ.ГГГГ
✔️ - ДД.ММ.ГГГГ, ДД.ММ.ГГГГ
✔️ - ДД.ММ.ГГГГ

Интервал между датами не должен превышать 60 дней!

Или выберите предложенный диапазон ⬇️"""

pars_hh_date_reply_t = """
Повторите ввод даты или выберите необходимый пресет 📅"""

pars_hh_name_t = """
Введите название запроса  #️⃣
Не более 100 символов

Название запроса указывается в заголовках краткого отчёта, а также сохраняется в базе данных для удобства навигации в дашборде 📁 
"""

pars_hh_title_t = """
Введите названия вакнансий так, как если бы вы вводили их в поисковую строку HH.ru 🔎
Важно! Указывайте в сообщении только целевые вакансии, исключения будут запрошены в следующем меню 📍

В запросе можно указать несколько вакансий или разные варианты написания одной вакансии 🔗
Для того, чтобы такой запрос работал корректно, необходимо разделить позиции союзами "И" / "ИЛИ" ✂️
"""

req_hh_info_t = """ Подробнее о языке запросов HH.RU ⬇️"""

pars_hh_title_excl_t = """
При необходимости, вы можете указать слова или словосочетания, которые будут исключены из запроса ⛔️

Слова или словосочетания должны разделяться символом ";" или "."
"""

# Сообщение выбор режима фильтрации парсера HH.ru
pars_hh_filter_t = """
Запрос можно дополнить фильтрами по различным параметрам:

✔️ - Режим поиска
✔️ - Регион поиска
✔️ - Индустрия работодателей
✔️ - Поиск по вакансиям компаний
✔️ - Требуемый стаж
✔️ - Предлагаемый график
✔️ - Формат трудоустройства

По умолчанию - алгоритм ищет вакансии во всех регионах России 🇷🇺,
а в выдачу попадают только позиции с указанной зарплатой в рублях 🤑 
Других ограничений не применяются

Какие фильтры необходимо использовать? ✋🏻"""

filter_accept_t = """
Параметр добавлен 👌🏻"""

# Сообщение выбор режима фильтрации парсера HH.ru
pars_hh_search_t = """
Где будем искать?"""

# Сообщение выбор регионов парсинга HH.ru
pars_hh_set_reg_t = """
Выберите регион / регионы для поиска вакансий 🌏"""

# Сообщение выбор целевых индустрии парсинга HH.ru
pars_hh_set_ind_t = """
Выберите интересующие индустрии 👨🏻‍💻👷🏻‍♂️"""

# Сообщение выбор целевых компаний парсинга HH.ru
pars_hh_set_empl_t = """
Выберите целевые компании 💼️"""

# Сообщение выбор требуемого опыта парсинга HH.ru
pars_hh_set_exp_t = """
Выберите требуемый опыт сотрудников 👨🏻‍🦳👶🏻"""

# Сообщение выбор типа трудоустройства парсинга HH.ru
pars_hh_set_employment_t = """
Выберите интересующие форматы трудоустройства 📆️"""

# Сообщение выбор типа графика парсинга HH.ru
pars_hh_set_sched_t = """
Выберите предлагаемые типы графика 🕓"""

# Запуск парсера
start_pars_hh_t = """
Для запуска парсинга нажмите Старт"""

short_df_except_t = """
Найдено менее 10 вакансий - анализ невозможен 🥲
Попробуйте изменить параметры запроса и запустить новый парсинг"""
