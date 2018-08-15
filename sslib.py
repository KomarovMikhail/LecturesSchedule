from datetime import datetime
import pandas as pd
from exeptions.custom_exeptions import *


def get_spreadsheet(from_path):
    spreadsheet = pd.read_csv(from_path)

    result = []
    for i in range(len(spreadsheet['ID'])):
        buf = {}
        row = spreadsheet.loc[i, :]
        if len(row) != 8:
            raise FieldNumError
        buf['id'] = str(row[0])
        buf['date'] = str(row[1])
        buf['start'] = str(row[2])
        buf['end'] = str(row[3])
        buf['name'] = str(row[4])
        buf['lecturer'] = str(row[5])
        buf['where'] = str(row[6])
        buf['about'] = str(row[7])
        result.append(buf)

    return result


def is_upcoming(lecture):
    try:
        date = lecture['date'].split('.')
        day = int(date[0])
        month = int(date[1])

        lecture_time = lecture['start'].split(':')
        hour = int(lecture_time[0])
        minute = int(lecture_time[1])

        result_time = datetime(datetime.now().year, month, day, hour, minute)
        return result_time > datetime.now()
    except ValueError:
        raise TimeError


def sort_key(lecture):
    try:
        date = lecture['date'].split('.')
        day = int(date[0])
        month = int(date[1])

        lecture_time = lecture['start'].split(':')
        hour = int(lecture_time[0])
        minute = int(lecture_time[1])

        return datetime(datetime.now().year, month, day, hour, minute)
    except ValueError:
        raise TimeError


def get_nearest(csv_url):
    lectures = get_spreadsheet(csv_url)

    upcoming = [lecture for lecture in lectures if is_upcoming(lecture)]
    upcoming = sorted(upcoming, key=sort_key)

    return upcoming[:3]


def get_faq(from_url):
    spreadsheet = pd.read_csv(from_url)

    result = []
    for i in range(len(spreadsheet['Вопрос'])):
        buf = {}
        row = spreadsheet.loc[i, :]
        buf['question'] = str(row[0])
        buf['answer'] = str(row[1])
        result.append(buf)

    return result


class SSHandler:
    """
    Класс для последовательного отображения лекций.
    """
    def __init__(self, csv_url):
        self._map = {}  # cid->step
        self._csv_url = csv_url
        self._prev_len = 0

    def get_lectures(self, cid):
        if self._map.get(cid) is None:
            self._map[cid] = 0

        lectures = get_spreadsheet(self._csv_url)
        lectures = sorted(lectures, key=sort_key)

        step = 0
        if len(lectures) != self._prev_len:
            for key in self._map.keys():
                self._map[key] = 0
        else:
            step = self._map[cid]
            if step >= len(lectures):
                step = 0
                self._map[cid] = 0
        result = lectures[step:step+3]
        self._map[cid] += 3
        self._prev_len = len(lectures)
        return result
