import json
import os
from shutil import move

import logging

import db_content
import db_user

logger = logging.getLogger(__name__)


def is_admin(uid):
    return db_user.get_al(uid) >= 1


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True


def help(bot, update):
    if is_admin(update.message.from_user.id):
        update.message.reply_text(db_content.get('master_help'))


def stop(bot, update):
    if is_admin(update.message.from_user.id):
        logger.info('User sent stop command! Bot will stopped soon...')
        update.message.reply_text('Bot will stopped soon...')
        os._exit(0)


def broadcast(bot, update):
    if is_admin(update.message.from_user.id):
        msg = update.message.text.replace('/broadcast', '', 1)
        if msg == '':
            update.message.reply_text('Please, write text!')
        else:
            for uid in db_user.get():
                bot.sendMessage(chat_id=uid, text=msg)


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
