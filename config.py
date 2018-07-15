# -*- coding: utf-8 -*-
TOKEN = '588048354:AAFgl8K6V4JSoc9Cs3v4PlgNT2zfNHg0XcU'

URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQaIuizRlU2hODjbpXeydGqq67f5-cU1G7-7xIgMs7m9bpiAMRsO6pt27_gFKozauiudddO4pn_3HA8/pub?output=xlsx'
XML_PATH = 'files/lectures.xml'
XLSX_PATH = 'files/lectures.xlsx'

WEBHOOK_HOST = 'voyage-livre-89482.herokuapp.com'
WEBHOOK_PORT = 443
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_SSL_CERT = './webhook_cert.pem'
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (TOKEN)
