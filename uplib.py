import openpyxl
from sslib import get_spreadsheet


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

    def _reload_sheet(self, ss):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Schedule'

        labels = ['id', 'date', 'start', 'end', 'name', 'lecturer']
        ws.append(labels)

        i = 2
        self._id_map = {}
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

    def _get_info(self, l_id, ss=None):
        if ss is not None:
            for item in ss:
                if item['id'] == l_id:
                    return item
        else:
            wb = openpyxl.load_workbook(filename=self._sheet)
            ws = wb['Schedule']
            row = str(self._id_map[l_id])
            result = {}

            result['id'] = ws['A' + row].value
            result['date'] = ws['B' + row].value
            result['start'] = ws['C' + row].value
            result['end'] = ws['D' + row].value
            result['name'] = ws['E' + row].value
            result['lecturer'] = ws['F' + row].value

            return result

    def _decline_lecture(self, l_id):
        info = self._get_info(l_id)
        text = 'Внимание!\nДоклад "{0}" в {1} отменен.'.format(info['name'], info['start'])
        # self._id_map.pop(l_id)
        # self._size -= 1
        return text

    def _add_lecture(self, l_id, spreadsheet):
        info = self._get_info(l_id, spreadsheet)
        text = 'Внимание!\nВ расписание добавлен новый доклад "{0}", который начнется в {1}. ' \
               'Докладчик: {2}.'.format(info['name'], info['start'], info['lecturer'])
        # self._id_map[l_id] = self._size + 2
        # self._size += 1
        return text

    def _get_item_by_id(self, worksheet, l_id):
        for i in range(2, self._size + 2):
            row = str(i)
            if worksheet['A' + row].value == l_id:
                return {
                    'id': worksheet['A' + row].value,
                    'date': worksheet['B' + row].value,
                    'start': worksheet['C' + row].value,
                    'end': worksheet['D' + row].value,
                    'name': worksheet['E' + row].value,
                    'lecturer': worksheet['F' + row].value
                }

    def get_updates(self):
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
        print(l_1, l_2, l_3)

        for i in l_1:
            result.append(self._decline_lecture(i))

        for i in l_2:
            result.append(self._add_lecture(i, ss))

        for item in ss:
            flag = 0
            if item['id'] not in l_3:
                continue
            old_item = self._get_item_by_id(ws, item['id'])
            if item['start'] != old_item['start']:
                flag = 1
            if item['lecturer'] != old_item['lecturer']:
                if flag == 0:
                    flag = 2
                else:
                    flag = 3

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
                        'Доклад прочтет {3}'.format(item['name'], item['start'], item['end'], item['lecturer'])
            result.append(text)

        self._reload_sheet(ss)  # обновить таблицу

        return result

