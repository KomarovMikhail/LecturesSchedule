from datetime import datetime
import pandas as pd


def get_spreadsheet(from_path):
    spreadsheet = pd.read_csv(from_path)

    result = []
    for i in range(len(spreadsheet['ID'])):
        buf = {}
        row = spreadsheet.loc[i, :]
        buf['id'] = str(row[0])
        buf['date'] = str(row[1])
        buf['start'] = str(row[2])
        buf['end'] = str(row[3])
        buf['name'] = str(row[4])
        buf['lecturer'] = str(row[5])
        result.append(buf)

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


def get_nearest(csv_url):
    lectures = get_spreadsheet(csv_url)

    upcoming = [lecture for lecture in lectures if is_upcoming(lecture)]
    upcoming = sorted(upcoming, key=sort_key)

    return upcoming[:3]
