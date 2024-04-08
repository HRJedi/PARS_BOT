# This Python file uses the following encoding: utf-8


# Проверить наличие пользователя в БД
init_user_q = '''SELECT
                    COUNT(user_id)
                FROM
                    "PARS_BOT".users
                WHERE
                    user_id = %s;'''


# Добавить нового пользователя
new_user_q = '''INSERT INTO "PARS_BOT".users
                    (user_id, f_name_tg, l_name_tg, username)
                VALUES
                    (%s, %s, %s, %s);'''


# Получить текущий стейт пользователя
get_state_q = '''SELECT
                    state
                FROM
                    "PARS_BOT".user_state
                WHERE
                    user_id = %s;'''


# Изменить текущий стейт пользователя
set_state_q = '''INSERT INTO "PARS_BOT".user_state
                    (user_id, upd_date, state, addition, user_message)
                VALUES
                    (%s, now(), %s, %s, %s)
                ON CONFLICT
                    (user_id)
                DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    upd_date = EXCLUDED.upd_date,
                    state = EXCLUDED.state,
                    addition = EXCLUDED.addition,
                    user_message = EXCLUDED.user_message;'''

# Логировать действие без изменения стейта
new_log_q = '''INSERT INTO "PARS_BOT".user_log
                    (user_id, state, addition, user_message)
                VALUES
                    (%s, %s, %s, %s);'''


# ВЗАИМОДЕЙСТВИЕ С ПАРСЕРОМ
# Обновить статус запроса
new_req_stat = '''UPDATE
                      "PARS_BOT".user_req
                  SET
                      req_status = %s
                  WHERE
                      req_uuid = %s;'''

# Внести время начала анализа и статус
set_req_start = '''UPDATE
                      "PARS_BOT".user_req
                  SET
                      analysis_start = %s,
                      req_status = %s
                  WHERE
                      req_uuid = %s;'''


# Внести статус и время анализа
set_req_finish = '''UPDATE
                      "PARS_BOT".user_req
                  SET
                      analysis_finish = %s,
                      req_status = %s,
                      total_time_sec = %s
                  WHERE
                      req_uuid = %s;'''

# Отметить запрос под архивацию
archived_req = '''UPDATE
                      "PARS_BOT".user_req
                  SET
                      archived = %s
                  WHERE
                      req_uuid = %s;'''

# Внести статистику предварительного анализа HH
set_hh_stat_p = '''UPDATE
                       "PARS_BOT".hh_req
                   SET
                       prew_exept_count = %s,
                       prew_vac_count = %s,
                       prew_time_sec = %s,
                       prew_complete = %s
                   WHERE
                       req_uuid = %s;'''

# Внести статистику глубокого анализа HH
set_hh_stat_d = '''UPDATE
                       "PARS_BOT".hh_req
                   SET
                       deep_exept_count = %s,
                       deep_vac_count = %s,
                       deep_time_sec = %s,
                       deep_complete = %s
                   WHERE
                       req_uuid = %s;'''
