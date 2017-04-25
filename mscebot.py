#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# MSCE Schedule Telegram bot
# by Alexander Zakharenko
#

import json
import logging
import time
from threading import Thread, Event

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import schedule
import db_user
import cmd_user

config = json.loads(open('bot.json', 'r').read())
logging.basicConfig(format='[%(asctime)s] [%(levelname)s:%(name)s] %(message)s', level=logging.DEBUG,
                    filename=config['logFileName'])
logger = logging.getLogger(__name__)


def schedule_monitor(bot, run):
    logger.debug('Starting schedule monitor...')

    while run.is_set():
        if schedule.update_student():
            for uid in db_user.get():
                group = db_user.get_sub_student(uid)
                if group is not None:
                    bot.sendMessage(chat_id=uid, text=schedule.get_student(group=group))

        if schedule.update_teacher():
            for uid in db_user.get():
                name = db_user.get_sub_teacher(uid)
                if name is not None:
                    bot.sendMessage(chat_id=uid, text=schedule.get_teacher(name=name))

        time.sleep(config['updateSleep'])

    logger.debug('Stopping schedule monitor...')


def main():
    updater = Updater(config['token'])

    updater.dispatcher.add_handler(CommandHandler('start', cmd_user.menu))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, cmd_user.processor))

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
