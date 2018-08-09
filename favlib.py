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

    cursor.execute(SELECT_BY_ID.format(cid))
    data = cursor.fetchall()
    if len(data) != 0:
        old_ids = data[0][0]
        new_ids = old_ids + ',' + str(lid)
        cursor.execute(UPDATE.format(cid, new_ids))
    else:
        cursor.execute(INSERT.format(cid, lid))
    conn.commit()
    conn.close()


def remove_from_favorite(cid, lid):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    cursor.execute(SELECT_BY_ID.format(cid))
    data = cursor.fetchall()
    if len(data) != 0:
        old_ids = data[0][0].split(',')
        try:
            old_ids.remove(lid)
            if len(old_ids) == 0:
                cursor.execute(DELETE.format(cid))
            else:
                new_ids = ','.join(old_ids)
                cursor.execute(UPDATE.format(cid, new_ids))
        except ValueError:
            pass
    conn.commit()
    conn.close()


def select_by_id(cid):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    cursor.execute(SELECT_BY_ID.format(cid))
    data = cursor.fetchall()

    conn.commit()
    conn.close()
    if len(data) == 0:
        return None
    else:
        return data[0][0].split(',')


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
