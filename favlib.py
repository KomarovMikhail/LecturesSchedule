from constants.queries import *
import psycopg2
from constants.config import DATABASE_URL


def create_favorite_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute(IF_DROP)
    cursor.execute(CREATE)
    conn.commit()
    conn.close()


def add_to_favorite(cid, lid):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    cursor.execute(EXISTS.format(cid))
    data = cursor.fetchall()
    if data[0][0]:
        cursor.execute(SELECT_BY_ID.format(cid))
        data = cursor.fetchall()
        old_ids = data[0][0]
        new_ids = old_ids + ',' + str(lid)
        cursor.execute(UPDATE.format(cid, new_ids))
    else:
        cursor.execute(INSERT.format(cid, lid))
    conn.commit()
    conn.close()

    # cursor.execute(INSERT.format(cid, lid))
    # cursor.execute(EXISTS.format(cid))
    #
    # rows = cursor.fetchall()
    # print("test:")
    # print(rows)
    # for msg in rows:
    #     print(type(msg[0]))
    # conn.commit()
    # conn.close()


def select_by_id(cid):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute(SELECT_BY_ID.format(cid))
    conn.commit()
    conn.close()


def drop_favorite_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute(DROP)
    conn.commit()
    conn.close()


def select_all_test():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute(SELECT_BY_ID.format(1))
    rows = cursor.fetchall()
    print(rows)
    for msg in rows:
        print(msg[0])
    conn.commit()
    conn.close()
