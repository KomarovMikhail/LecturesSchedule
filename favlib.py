from constants.queries import *
import psycopg2
from constants.config import DATABASE_URL
from exeptions.custom_exeptions import *


def create_favorite_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute(IF_CREATE_FAVORITE)
    conn.commit()
    conn.close()


def in_favorite(cid, lid):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    cursor.execute(SELECT_BY_ID_FAVORITE.format(cid))
    data = cursor.fetchall()
    result = False
    if len(data) != 0:
        old_ids = data[0][0]
        if lid in old_ids.split(','):
            result = True
    conn.commit()
    conn.close()
    return result


def add_to_favorite(cid, lid):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    cursor.execute(SELECT_BY_ID_FAVORITE.format(cid))
    data = cursor.fetchall()
    if len(data) != 0:
        old_ids = data[0][0]
        if lid in old_ids.split(','):
            conn.commit()
            conn.close()
            raise AlreadyAddedError
        new_ids = old_ids + ',' + str(lid)
        cursor.execute(UPDATE_FAVORITE.format(cid, new_ids))
    else:
        cursor.execute(INSERT_FAVORITE.format(cid, lid))
    conn.commit()
    conn.close()


def remove_from_favorite(cid, lid):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    cursor.execute(SELECT_BY_ID_FAVORITE.format(cid))
    data = cursor.fetchall()
    if len(data) != 0:
        old_ids = data[0][0].split(',')
        try:
            old_ids.remove(lid)
        except ValueError:
            conn.commit()
            conn.close()
            raise AlreadyRemovedError
        if len(old_ids) == 0:
            cursor.execute(DELETE_FAVORITE.format(cid))
        else:
            new_ids = ','.join(old_ids)
            cursor.execute(UPDATE_FAVORITE.format(cid, new_ids))
    else:
        conn.commit()
        conn.close()
        raise AlreadyRemovedError
    conn.commit()
    conn.close()


def select_by_id(cid):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    cursor.execute(SELECT_BY_ID_FAVORITE.format(cid))
    data = cursor.fetchall()

    conn.commit()
    conn.close()
    result = []
    if len(data) != 0:
        result = data[0][0].split(',')
    return result


def drop_favorite_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute(DROP_FAVORITE)
    conn.commit()
    conn.close()


def select_all_test():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute(SELECT_BY_ID_FAVORITE.format(1))
    rows = cursor.fetchall()
    print(rows)
    for msg in rows:
        print(msg[0])
    conn.commit()
    conn.close()
