import os
from constants.emoji import EXCLAMATION_POINT


TOKEN = '588048354:AAFgl8K6V4JSoc9Cs3v4PlgNT2zfNHg0XcU'

# CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQaIuizRlU2hODjbpXeydGqq67f5-cU1G7-7xIgMs7m9bpiAMRsO6pt27_gFKozauiudddO4pn_3HA8/pub?output=csv'
CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQaIuizRlU2hODjbpXeydGqq67f5-cU1G7-7xIgMs7m9bpiAMRsO6pt27_gFKozauiudddO4pn_3HA8/pub?gid=0&single=true&output=csv'
FAQ_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQaIuizRlU2hODjbpXeydGqq67f5-cU1G7-7xIgMs7m9bpiAMRsO6pt27_gFKozauiudddO4pn_3HA8/pub?gid=1390482820&single=true&output=csv'

APP_NAME = 'voyage-livre-89482.herokuapp.com'

IMG_PATH = 'imgs/'

SCHEDULE_PATH = 'actual_schedule/schedule.xlsx'

DATABASE_URL = os.environ['DATABASE_URL']

ADMIN_PASSWORD = '0000'

SPREADSHEET_ERROR_MESSAGE = '{0}ВНИМАНИЕ АДМИНИСТРАТОРАМ{0}\nИнформация о некоторых докладах заполнена неверно. ' \
                            'Просьба исправить в срочном порядке, ' \
                            'чтобы продолжить полноценную работу сервиса.'.format(EXCLAMATION_POINT)
