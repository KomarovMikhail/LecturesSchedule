from constants.queries import *
import psycopg2
from constants.config import DATABASE_URL


def create_favorite_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute(CREATE)
    conn.commit()
    conn.close()


def add_to_favorite(cid, lid):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    cursor.execute(INSERT.format(cid, lid))
    cursor.execute(EXISTS.format(cid))

    rows = cursor.fetchall()
    print("test:")
    print(rows)
    for msg in rows:
        print('Got: ' + msg[0])
    conn.commit()
    conn.close()


def drop_favorite_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute(DROP)
    conn.commit()
    conn.close()

    # cursor.execute(SELECT)
    # rows = cursor.fetchall()
    # for msg in rows:
    #     print(msg[0])
    #
    # cursor.execute(DROP)
    # conn.commit()
    #
    # conn.close()
