# This Python file uses the following encoding: utf-8


import psycopg2
import psycopg2.extras
from sqlalchemy import engine as alch

con = psycopg2.connect(dbname='postgres',
                       user='postgres',
                       password='password',
                       host='localhost')

alch_eng = alch.create_engine(
    'postgresql+psycopg2://postgres:password@localhost:5432/postgres')


# SET
def set_val(que, ph):
    with con.cursor() as curs:
        curs.execute(que, ph)
        con.commit()
    return


# GET
def get_val(que, ph):
    with con.cursor() as curs:
        curs.execute(que, ph)
        result = curs.fetchone()
        con.commit()
    return result
