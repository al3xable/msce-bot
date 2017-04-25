#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# MSCE Schedule Telegram bot
# by Alexander Zakharenko
#

import json
import logging
from threading import Thread, Event

import time
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import database.user
import schedule

config = json.loads(open('bot.json', 'r').read())
logging.basicConfig(format='[%(asctime)s] [%(levelname)s:%(name)s] %(message)s', level=logging.DEBUG,
                    filename=config['logFileName'])
logger = logging.getLogger()


def get_content(title):
    return open('content/'+title+'.txt', 'r').read()


def get_student(bot, update):
    action = database.user.get_action(update.message.from_user.id)
    user = update.message.from_user
    text = update.message.text

    if action[0] == '':  # Выбор даты
        dates = [[KeyboardButton('[ В МЕНЮ ]')]]
        for date in sorted(schedule.get_student_dates(), reverse=True):
            dates.append([KeyboardButton(date + ', ' + schedule.get_weekday(date))])

        update.message.reply_text('Выберите или ввидите дату, за которую нужно посмотреть расписание',
                                  reply_markup=ReplyKeyboardMarkup(dates, one_time_keyboard=True))
        database.user.set_action(id=user.id, action='get_student')

    if action[0] == 'get_student':
        if len(action) > 1:
            date = action[1]
        else:
            date = text.split(',')[0]

        if len(action) == 1:  # Выбор группы
            groups = [[KeyboardButton('[ В МЕНЮ ]')]]
            for group in schedule.get_student_groups(date):
                groups.append([KeyboardButton(group['title'])])

            update.message.reply_text('Выберите или введите номер группы, для которой нужно посмотреть расписание',
                                      reply_markup=ReplyKeyboardMarkup(groups, one_time_keyboard=True))

            database.user.set_action(id=user.id, action='get_student/' + date)
        else:  # Отправка расписания
            update.message.reply_text(schedule.get_student(date=date, group=text))
            start(bot, update)


def get_teacher(bot, update):
    action = database.user.get_action(update.message.from_user.id)
    user = update.message.from_user
    text = update.message.text

    if action[0] == '':  # Выбор даты
        dates = [[KeyboardButton('[ В МЕНЮ ]')]]
        for date in sorted(schedule.get_teacher_dates(), reverse=True):
            dates.append([KeyboardButton(date + ', ' + schedule.get_weekday(date))])

        update.message.reply_text('Выберите или ввидите дату, за которую нужно посмотреть расписание',
                                  reply_markup=ReplyKeyboardMarkup(dates, one_time_keyboard=True))
        database.user.set_action(id=user.id, action='get_teacher')

    if action[0] == 'get_teacher':
        if len(action) > 1:
            date = action[1]
        else:
            date = text.split(',')[0]

        if len(action) == 1:  # Выбор преподавателя
            teachers = [[KeyboardButton('[ В МЕНЮ ]')]]
            for group in schedule.get_teacher_names(date):
                teachers.append([KeyboardButton(group['title'])])

            update.message.reply_text('Выберите или введите имя преподавателя, для которой нужно посмотреть расписание',
                                      reply_markup=ReplyKeyboardMarkup(teachers, one_time_keyboard=True))

            database.user.set_action(id=user.id, action='get_teacher/' + date)
        else:  # Отправка расписания
            update.message.reply_text(schedule.get_teacher(date=date, name=text))
            start(bot, update)


def sub_student(bot, update):
    action = database.user.get_action(update.message.from_user.id)
    user = update.message.from_user
    text = update.message.text

    if action[0] == 'sub_student':
        if text == '[ ОТПИСАТСЯ ]':
            text = None
            update.message.reply_text('Вы успешно отписаны')
        else:
            update.message.reply_text('Подписка успешно установлена на группу ' + text)

        database.user.set_sub_student(id=user.id, group=text)
        start(bot, update)
    else:
        groups = [[KeyboardButton('[ В МЕНЮ ]')]]
        for group in schedule.get_student_list():
            groups.append([KeyboardButton(group)])

        sub = database.user.get_sub_student(user.id)
        info = 'Вы сейчас не подписаны'
        if sub is not None:
            info = 'Вы сейчас подписаны на группу ' + sub
            groups[0].append(KeyboardButton('[ ОТПИСАТСЯ ]'))

        update.message.reply_text('Выберите или введите группу, на которую вы хотите подписатся\n'+info,
                                  reply_markup=ReplyKeyboardMarkup(groups, one_time_keyboard=True))

        database.user.set_action(id=user.id, action='sub_student')


def sub_teacher(bot, update):
    action = database.user.get_action(update.message.from_user.id)
    user = update.message.from_user
    text = update.message.text

    if action[0] == 'sub_teacher':
        if text == '[ ОТПИСАТСЯ ]':
            text = None
            update.message.reply_text('Вы успешно отписаны')
        else:
            update.message.reply_text('Подписка успешно установлена на преподавателя ' + text)

        database.user.set_sub_teacher(id=user.id, name=text)
        start(bot, update)
    else:
        teachers = [[KeyboardButton('[ В МЕНЮ ]')]]
        for teacher in schedule.get_teacher_list():
            teachers.append([KeyboardButton(teacher)])

        sub = database.user.get_sub_teacher(user.id)
        info = 'Вы сейчас не подписаны'
        if sub is not None:
            info = 'Вы сейчас подписаны на преподавателя ' + sub
            teachers[0].append(KeyboardButton('[ ОТПИСАТСЯ ]'))

        update.message.reply_text('Выберите или введите преподавателя, на которого вы хотите подписатся\n'+info,
                                  reply_markup=ReplyKeyboardMarkup(teachers, one_time_keyboard=True))

        database.user.set_action(id=user.id, action='sub_teacher')


def message(bot, update):
    user = update.message.from_user
    text = update.message.text
    action = database.user.get_action(user.id)
    database.user.update(user)

    logger.info('{} {} ({}:@{}): {}'.format(user.first_name, user.last_name, user.id, user.username, text))

    if text == '[ В МЕНЮ ]':
        start(bot, update)

    elif text == '[ ЗАКРЫТЬ ]':
        update.message.reply_text('Меню закрыто.', reply_markup=ReplyKeyboardRemove())
        database.user.set_action(user.id, '')

    elif text == 'РАСПИСАНИЕ ДЛЯ УЧАЩИХСЯ' or action[0] == 'get_student':
        try:
            get_student(bot, update)
        except schedule.ScheduleException as ex:
            if ex.code == 200:
                update.message.reply_text('Нет расписания за эту дату')
            elif ex.code == 201:
                update.message.reply_text('Нет расписания для этой группы за этот день')
            else:
                update.message.reply_text('Ошибка {}: {}'.format(ex.code, ex.message))

    elif text == 'РАСПИСАНИЕ ДЛЯ ПРЕПОДАВАТЕЛЕЙ' or action[0] == 'get_teacher':
        try:
            get_teacher(bot, update)
        except schedule.ScheduleException as ex:
            if ex.code == 200:
                update.message.reply_text('Нет расписания за эту дату')
            elif ex.code == 201:
                update.message.reply_text('Нет расписания для этого преподавателя за этот день')
            else:
                update.message.reply_text('Ошибка {}: {}'.format(ex.code, ex.message))

    elif text == 'ПОДПИСАТСЯ НА ГРУППУ' or action[0] == 'sub_student':
        sub_student(bot, update)

    elif text == 'ПОДПИСАТСЯ НА ПРЕПОДАВАТЕЛЯ' or action[0] == 'sub_teacher':
        sub_teacher(bot, update)

    elif text == 'РАСПИСАНИЕ ЗВОНКОВ':
        update.message.reply_text(get_content('bells'))
        start(bot, update)

    elif text == 'ОБ АВТОРЕ':
        update.message.reply_text(get_content('about'))
        start(bot, update)


def start(bot, update):  # Start menu
    database.user.set_action(id=update.message.from_user.id, action='')

    menu = [
        [KeyboardButton("РАСПИСАНИЕ ДЛЯ УЧАЩИХСЯ")],
        [KeyboardButton("РАСПИСАНИЕ ДЛЯ ПРЕПОДАВАТЕЛЕЙ")],
        [KeyboardButton("РАСПИСАНИЕ ЗВОНКОВ")],
        [KeyboardButton("ПОДПИСАТСЯ НА ГРУППУ")],
        [KeyboardButton("ПОДПИСАТСЯ НА ПРЕПОДАВАТЕЛЯ")],
        [KeyboardButton("ОБ АВТОРЕ")],
        [KeyboardButton('[ ЗАКРЫТЬ ]')]
    ]

    update.message.reply_text('Главное меню. Выберите нужное действие.',
                              reply_markup=ReplyKeyboardMarkup(menu, one_time_keyboard=True))


def schedule_monitor(bot, run):
    logger.debug('Starting schedule monitor...')

    while run.is_set():
        if schedule.update_student():
            for uid in database.user.get():
                group = database.user.get_sub_student(uid)
                if group is not None:
                    bot.sendMessage(chat_id=uid, text=schedule.get_student(group=group))

        if schedule.update_teacher():
            for uid in database.user.get():
                name = database.user.get_sub_teacher(uid)
                if name is not None:
                    bot.sendMessage(chat_id=uid, text=schedule.get_teacher(name=name))

        time.sleep(config['updateSleep'])

    logger.debug('Stopping schedule monitor...')


def main():
    updater = Updater(config['token'])

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, message))

    updater.start_polling(timeout=config['poolTimeout'])

    run = Event()
    run.set()

    th = Thread(target=schedule_monitor, args=(updater.bot, run))
    th.start()

    updater.idle()

    # Stopping thread
    run.clear()
    th.join()


if __name__ == '__main__':
    main()
