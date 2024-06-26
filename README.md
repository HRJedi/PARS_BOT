# PARS_BOT
## Анализ рынка труда в формате Telegram бота
\
Cервис для получения суммаризованной информации по заданной вакансии (HH.ru) в формате pdf отчёта.\
Реализован в качестве MVP для внутренних заказчиков.
___
Используются общедоступные методы API HH.RU без передачи токена авторизации:

1. Поиск вакансий: **GET/vacancies**
2. Просмотр конккретной вакансии: **GET/vacancies/{vacancy_id}**
3. Получение справочника регионов: **GET/areas**
4. Просмотр конкретной компании: **GET/employers/{employer_id}**
___
**Реализовано:**
1. Взаимодействие с БД (Postgres);
2. State-storage и запись активность пользователей;
3. Получение отчёта по вакансиям HH.ru;
4. Step-by-step interaction - пошаговая инструкция;
5. Упрощенный ввод запроса;
6. Базовая настройка параметров запроса пользователем;
7. Проверка статуса сервиса;
8. Формирование pdf отчёта с основным набором метрик.

*Имеется техническая возможность писать в БД полную информацию о вакансии и работодателе (Скрыта).*
___
**Основные библиотеки:**\
telebot, requests, pandas, numpy, matplotlib, bs4, psycopg2, sqlalchemy.
