from constants.queries import *
from exeptions.custom_exeptions import *
import psycopg2


class EstimatesHandler:
    def __init__(self, db_url):
        self._map = {}
        self._db_url = db_url
        self._init_db()

    def _init_db(self):
        conn = psycopg2.connect(self._db_url, sslmode='require')
        cursor = conn.cursor()
        cursor.execute(IF_DROP_ESTIMATES)
        cursor.execute(CREATE_ESTIMATES)
        conn.commit()
        conn.close()

    def _already_estimated(self, cid, lid):
        if self._map.get(cid) is not None:
            return lid in self._map[cid]
        else:
            self._map[cid] = []
            return False

    def estimate_lecture(self, cid, lid, mark):
        print(self._map)
        if self._already_estimated(cid, lid):
            raise AlreadyEstimatedError

        conn = psycopg2.connect(self._db_url, sslmode='require')
        cursor = conn.cursor()

        cursor.execute(SELECT_BY_ID_ESTIMATES.format(lid))
        data = cursor.fetchall()
        if len(data) == 0:
            cursor.execute(INSERT_ESTIMATES.format(lid, mark, 1))
        else:
            cursor.execute(UPDATE_ESTIMATES.format(lid, data[0][0] + mark, data[0][1] + 1))

        self._map[cid].append(lid)
        conn.commit()
        conn.close()
        print(self._map)

    def get_mark(self, lid):
        conn = psycopg2.connect(self._db_url, sslmode='require')
        cursor = conn.cursor()

        cursor.execute(SELECT_BY_ID_ESTIMATES.format(lid))
        data = cursor.fetchall()
        if len(data) == 0:
            conn.commit()
            conn.close()
            raise NoEstimationsError
        mark = data[0][0] / data[0][1]
        conn.commit()
        conn.close()
        return mark
