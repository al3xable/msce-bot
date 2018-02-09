import json
import os
from shutil import move

import logging

import db_content
import db_user
import schedule

logger = logging.getLogger(__name__)


def is_admin(uid):
    return db_user.get_al(uid) >= 1


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True


def schedule_broadcast_student(bot):
    for user in db_user.get():
        group = db_user.get_sub_student(user)
        if group is not (None or '' or 'NULL'):
            try:
                bot.sendMessage(chat_id=user.id, text=schedule.get_student(group=group))
            except schedule.ScheduleException as ex:
                if ex.code == 201:
                    bot.sendMessage(chat_id=user.id, text='У группы {} нет пар'.format(group))
                else:
                    bot.sendMessage(chat_id=user.id, text='Ошибка {}: {}'.format(ex.code, ex.message))


def schedule_broadcast_teacher(bot):
    for user in db_user.get():
        name = db_user.get_sub_teacher(user)
        if name is not (None or '' or 'NULL'):
            try:
                bot.sendMessage(chat_id=user.id, text=schedule.get_teacher(name=name))
            except schedule.ScheduleException as ex:
                if ex.code == 201:
                    bot.sendMessage(chat_id=user.id, text='У преподавателя {} нет пар'.format(name))
                else:
                    bot.sendMessage(chat_id=user.id, text='Ошибка {}: {}'.format(ex.code, ex.message))


def help(update):
    if is_admin(update.message.from_user.id):
        update.message.reply_text(db_content.get('master_help'))


def stop(update):
    if is_admin(update.message.from_user.id):
        logger.info('User sent stop command! Bot will stopped soon...')
        update.message.reply_text('Bot will stopped soon...')
        os._exit(0)


def text_broadcast(bot, update):
    if is_admin(update.message.from_user.id):
        msg = update.message.text.replace('/tbcast', '', 1)
        if msg == '':
            update.message.reply_text('Please, write text!')
        else:
            for uid in db_user.get():
                bot.sendMessage(chat_id=uid, text=msg)


def schedule_broadcast(bot, update):
    if is_admin(update.message.from_user.id):
        text = update.message.text.replace('/sbcast ', '', 1)
        if text == 'student':
            schedule_broadcast_student(bot)
        elif text == 'teacher':
            schedule_broadcast_teacher(bot)
        elif text == 'all':
            schedule_broadcast_student(bot)
            schedule_broadcast_teacher(bot)
        else:
            update.message.reply_text('Available only student, teacher or all')


def get_config(bot, update):
    if is_admin(update.message.from_user.id):
        bot.sendDocument(chat_id=update.message.from_user.id, document=open('bot.json', 'rb'))


def set_config(bot, update):
    if is_admin(update.message.from_user.id):
        json.loads(open('bot.json', 'r').read())
        move('bot.json', 'bot.json.old')
        bot.getFile(update.message.document.file_id).download('bot.json')
        with open('bot.json', 'r') as cfg:
            data = cfg.read()
            if is_json(data):
                update.message.reply_text('Config is valid')
            else:
                move('bot.json.old', 'bot.json')
                update.message.reply_text('Config is invalid, old config returned')
