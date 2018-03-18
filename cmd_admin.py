import json
import os
from shutil import move
from functools import wraps
from telegram.error import Unauthorized, RetryAfter
import logging

import db_user
import utils
import schedule

logger = logging.getLogger(__name__)


def admin_only(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if not is_admin(user_id):
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


def is_admin(uid):
    return db_user.get_al(uid) >= 1


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True


def schedule_broadcast_student(bot):
    for uid in db_user.get():
        group = db_user.get_sub_student(uid)
        if group is not None:
            try:
                bot.sendMessage(chat_id=uid, text=schedule.get_student(group=group))
            except schedule.ScheduleException as ex:
                if ex.code == 201:
                    bot.sendMessage(chat_id=uid, text='У группы {} нет пар'.format(group))
                else:
                    bot.sendMessage(chat_id=uid, text='Ошибка {}: {}'.format(ex.code, ex.message))
            except Unauthorized:
                pass


def schedule_broadcast_teacher(bot):
    for uid in db_user.get():
        name = db_user.get_sub_teacher(uid)
        if name is not None:
            try:
                bot.sendMessage(chat_id=uid, text=schedule.get_teacher(name=name))
            except schedule.ScheduleException as ex:
                if ex.code == 201:
                    bot.sendMessage(chat_id=uid, text='У преподавателя {} нет пар'.format(name))
                else:
                    bot.sendMessage(chat_id=uid, text='Ошибка {}: {}'.format(ex.code, ex.message))
            except Unauthorized:
                pass


@admin_only
def help(bot, update):
    update.message.reply_text(utils.get_text('master_help.txt'))


@admin_only
def stop(bot, update):
    logger.info('User sent stop command! Bot will stopped soon...')
    update.message.reply_text('Bot will stopped soon...')
    os._exit(0)


def text_broadcast(bot, update):
    if is_admin(update.message.from_user.id):
        msg = update.message.text.replace('/tbcast ', '', 1)
        if msg == '':
            update.message.reply_text('Please, write text!')
        else:
            for uid in db_user.get():
                try:
                    bot.sendMessage(chat_id=uid, text=msg)
                except Unauthorized:
                    pass


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
