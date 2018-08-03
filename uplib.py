import openpyxl
from sslib import get_spreadsheet
from config import *


class UpdatesHandler:
    def __init__(self, sheet_path):
        self._sheet = sheet_path
        self._init_sheet()

    def _init_sheet(self):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Schedule'

        labels = ['id', 'date', 'start', 'end', 'name', 'lecturer']
        ws.append(labels)

        ss = get_spreadsheet(CSV_URL)
        for item in ss:
            labels = [item['id'], item['date'], item['start'], item['end'], item['name'], item['lecturer']]
            ws.append(labels)

        wb.save(filename=self._sheet)

    def check_updates(self):
        """
        Возвращает готовый текст сообщения для дальнейшей его отправки ботом
        """
        ss = get_spreadsheet(CSV_URL)
        wb = openpyxl.load_workbook(filename=self._sheet)
        ws = wb['Schedule']
        result = ''

        # to do

        return result


h = UpdatesHandler(SCHEDULE_PATH)
