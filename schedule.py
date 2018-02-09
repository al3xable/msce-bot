import urllib.request
import urllib.parse
import json
from datetime import datetime


class ScheduleException(Exception):
    def __init__(self, code, message):
        Exception.__init__(self)
        self.code = code
        self.message = message


student_last_date = None
cache_student = {}


def update_student():
    global student_last_date
    last = sorted(get_student_dates(), reverse=True)[0]
    clast = student_last_date
    student_last_date = last
    return clast != last and clast is not None


def get_student_dates():
    data = json.loads(
        urllib.request.urlopen('http://msce.bronydell.xyz/method/getStudentDates').read().decode())

    if data['code'] != 0:
        raise ScheduleException(data['code'], data['message'])

    return data['data']['dates'][-30:]


def get_student_list():
    data = json.loads(
        urllib.request.urlopen('http://msce.bronydell.xyz/method/getStudent').read().decode())

    if data['code'] != 0:
        raise ScheduleException(data['code'], data['message'])

    groups = []

    for group in data['data']['groups']:
        groups.append(group['title'])

    return groups


def get_student_groups(date):
    data = json.loads(
        urllib.request.urlopen('http://msce.bronydell.xyz/method/getStudent?date={}'.format(
                urllib.parse.quote_plus(string=date, encoding='UTF-8'))).read().decode())

    if data['code'] != 0:
        raise ScheduleException(data['code'], data['message'])

    return data['data']['groups']


def get_student(group, date=None):
    if date is None:
        data = json.loads(
            urllib.request.urlopen(
                'http://msce.bronydell.xyz/method/getStudent?group={}'.format(
                    urllib.parse.quote_plus(string=group, encoding='UTF-8'))).read().decode())
    else:
        data = json.loads(
            urllib.request.urlopen(
                'http://msce.bronydell.xyz/method/getStudent?date={}&group={}'.format(
                    urllib.parse.quote_plus(string=date, encoding='UTF-8'),
                    urllib.parse.quote_plus(string=group, encoding='UTF-8'))).read().decode())

    if data['code'] != 0:
        raise ScheduleException(data['code'], data['message'])

    date = '{}, {}'.format(data['data']['date'], get_weekday(data['data']['date']))
    schedule = 'Дата: {}\nГруппа: {}\n\n\n'.format(date, group)
    for lesson in data['data']['groups'][0]['lessons']:
        schedule += '{}. {}\nАудитория(и): {}\n\n'.format(lesson['number'], lesson['lesson'], lesson['audience'])

    return schedule


teacher_last_date = None
cache_teacher = {}


def update_teacher():
    global teacher_last_date
    last = sorted(get_teacher_dates(), reverse=True)[0]
    clast = teacher_last_date
    teacher_last_date = last
    return clast != last and clast is not None


def get_teacher_list():
    data = json.loads(
        urllib.request.urlopen('http://msce.bronydell.xyz/method/getTeacher').read().decode())

    if data['code'] != 0:
        raise ScheduleException(data['code'], data['message'])

    teachers = []

    for group in data['data']['groups']:
        teachers.append(group['title'])

    return teachers


def get_teacher_dates():
    data = json.loads(
        urllib.request.urlopen('http://msce.bronydell.xyz/method/getTeacherDates').read().decode())

    if data['code'] != 0:
        raise ScheduleException(data['code'], data['message'])

    return data['data']['dates'][-30:]


def get_teacher_names(date):
    data = json.loads(
        urllib.request.urlopen('http://msce.bronydell.xyz/method/getTeacher?date={}'.format(
                urllib.parse.quote_plus(string=date, encoding='UTF-8'))).read().decode())

    if data['code'] != 0:
        raise ScheduleException(data['code'], data['message'])

    return data['data']['groups']


def get_teacher(name, date=None):
    if date is None:
        data = json.loads(
            urllib.request.urlopen(
                'http://msce.bronydell.xyz/method/getTeacher?teacher={}'.format(
                    urllib.parse.quote_plus(string=name, encoding='UTF-8'))).read().decode())
    else:
        data = json.loads(
            urllib.request.urlopen(
                'http://msce.bronydell.xyz/method/getTeacher?date={}&teacher={}'.format(
                    urllib.parse.quote_plus(string=date, encoding='UTF-8'),
                    urllib.parse.quote_plus(string=name, encoding='UTF-8'))).read().decode())

    if data['code'] != 0:
        raise ScheduleException(data['code'], data['message'])

    date = '{}, {}'.format(data['data']['date'], get_weekday(data['data']['date']))
    schedule = 'Дата: {}\nПреподаватель: {}\n\n\n'.format(date, name)
    for lesson in data['data']['groups'][0]['lessons']:
        schedule += '{}. {}\nАудитория(и): {}\n\n'.format(lesson['number'], lesson['lesson'], lesson['audience'])

    return schedule


def get_weekday(date):
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    return days[datetime.strptime(date, '%Y-%m-%d').weekday()]
