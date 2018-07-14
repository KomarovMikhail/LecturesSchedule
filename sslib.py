import urllib.request
import xlrd
from lxml import etree
from datetime import datetime


def download_spreadsheet(from_path, to_path):
    with urllib.request.urlopen(from_path) as url:
        spreadsheet = url.read()
    file = open(to_path, "wb")
    file.write(spreadsheet)
    file.close()


def convert_to_xml(from_path, to_path):
    root = etree.Element('lectures')
    wb = xlrd.open_workbook(from_path)
    sh = wb.sheet_by_index(0)

    for row in range(1, sh.nrows):
        val = sh.row_values(row)
        element = etree.SubElement(root, 'lecture')
        element.set('id', str(int(val[0])))
        element.set('date', str(val[1]))
        element.set('start', str(val[2]))
        element.set('end', str(val[3]))
        element.set('name', str(val[4]))
        element.set('lecturer', str(val[5]))

    with open(to_path, 'wb') as out:
        out.write(etree.tostring(root, pretty_print=True, encoding='UTF-8'))


def parse_xml(path):
    with open(path) as file:
        xml = file.read()

    result = []

    root = etree.fromstring(xml)
    for child in root.getchildren():
        result.append(child.attrib)
    return result


def is_upcoming(lecture):
    date = lecture['date'].split('.')
    day = int(date[0])
    month = int(date[1])

    lecture_time = lecture['start'].split(':')
    hour = int(lecture_time[0])
    minute = int(lecture_time[1])

    result_time = datetime(datetime.now().year, month, day, hour, minute)

    return result_time > datetime.now()


def sort_key(lecture):
    date = lecture['date'].split('.')
    day = int(date[0])
    month = int(date[1])

    lecture_time = lecture['start'].split(':')
    hour = int(lecture_time[0])
    minute = int(lecture_time[1])

    return datetime(datetime.now().year, month, day, hour, minute)


def get_nearest(xml_file):
    lectures = parse_xml(xml_file)

    upcoming = [lecture for lecture in lectures if is_upcoming(lecture)]
    upcoming = sorted(upcoming, key=sort_key)

    return upcoming[:3]

