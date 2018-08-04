import openpyxl
from sslib import get_spreadsheet
from config import *


class UpdatesHandler:
    def __init__(self, sheet_path, csv_url):
        self._sheet = sheet_path
        self._csv = csv_url
        self._id_map = {}  # id->row
        self._size = 0
        self._init_sheet()

    def _init_sheet(self):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Schedule'

        labels = ['id', 'date', 'start', 'end', 'name', 'lecturer']
        ws.append(labels)

        ss = get_spreadsheet(self._csv)
        i = 2
        for item in ss:
            labels = [item['id'], item['date'], item['start'], item['end'], item['name'], item['lecturer']]
            ws.append(labels)
            self._id_map[item['id']] = i
            i += 1
        self._size = len(ss)

        wb.save(filename=self._sheet)

    @staticmethod
    def _compare_ids(old, new):
        """
        Сравнивает значения списков и возвращает три списка:
        Значение встречающиеся только в old, -||- только в new, пересчение old и new
        """
        l_1, l_2, l_3 = [], [], []
        for item in old:
            if item in new:
                l_3.append(item)
                new.remove(item)
            else:
                l_1.append(item)
        l_2 = new

        return l_1, l_2, l_3

    def check_updates(self):
        """
        Возвращает готовый текст сообщения для дальнейшей его отправки ботом
        """
        ss = get_spreadsheet(self._csv)
        wb = openpyxl.load_workbook(filename=self._sheet)
        ws = wb['Schedule']
        result = []

        old_ids = self._id_map.keys()
        new_ids = [item['id'] for item in ss]
        l_1, l_2, l_3 = self._compare_ids(old_ids, new_ids)

        for item in l_1:
            text = ''  # to do
            result.append(text)

        for item in l_2:
            text = ''  # to do
            result.append(text)

        i = 2

        for item in ss:
            flag = 0
            if item['id'] not in l_3:
                continue
            if item['start'] != ws['C' + str(i)]:
                flag = 1
            if item['lecturer'] != ws['F' + str(i)]:
                if flag == 0:
                    flag = 2
                else:
                    flag = 3

            i += 1
            text = 'Внимание!\n'
            if flag == 0:
                continue
            if flag == 1:
                text += 'Время начала доклада "{0}" изменилось.\n' \
                        'Доклад начнется в {1} и закончится в {2}.'.format(item['name'], item['start'], item['end'])
            if flag == 2:
                text += 'Доклад "{0}" будет читать другой лектор.\n' \
                        'Доклад прочтет {1}'.format(item['name'], item['lecturer'])
            if flag == 3:
                text += 'Время начала доклада "{0}" изменилось.\n' \
                        'Доклад начнется в {1} и закончится в {2}.\n' \
                        'Также изменился изменился докладчик.\n' \
                        'Доклад прочтет {3}'.format(item['name'], item['start'], item['end'], item['lecturer1'])
            result.append(text)

        return result


h = UpdatesHandler(SCHEDULE_PATH, CSV_URL)
