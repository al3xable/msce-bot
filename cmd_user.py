import logging
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

import db_content
import db_user
import schedule

logger = logging.getLogger(__name__)


def get_student(bot, update):
    action = db_user.get_action(update.message.from_user.id)
    user = update.message.from_user
    text = update.message.text

    if action[0] == '':  # Выбор даты
        dates = [[KeyboardButton('[ В МЕНЮ ]')]]
        for date in sorted(schedule.get_student_dates(), reverse=True):
            dates.append([KeyboardButton(date + ', ' + schedule.get_weekday(date))])

        update.message.reply_text('Выберите или ввидите дату, за которую нужно посмотреть расписание',
                                  reply_markup=ReplyKeyboardMarkup(dates, one_time_keyboard=True))
        db_user.set_action(id=user.id, action='get_student')

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

            db_user.set_action(id=user.id, action='get_student/' + date)
        else:  # Отправка расписания
            update.message.reply_text(schedule.get_student(date=date, group=text))
            menu(bot, update)


def get_teacher(bot, update):
    action = db_user.get_action(update.message.from_user.id)
    user = update.message.from_user
    text = update.message.text

    if action[0] == '':  # Выбор даты
        dates = [[KeyboardButton('[ В МЕНЮ ]')]]
        for date in sorted(schedule.get_teacher_dates(), reverse=True):
            dates.append([KeyboardButton(date + ', ' + schedule.get_weekday(date))])
        update.message.reply_text('Выберите или ввидите дату, за которую нужно посмотреть расписание',
                                  reply_markup=ReplyKeyboardMarkup(dates, one_time_keyboard=True))
        db_user.set_action(id=user.id, action='get_teacher')

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

            db_user.set_action(id=user.id, action='get_teacher/' + date)
        else:  # Отправка расписания
            update.message.reply_text(schedule.get_teacher(date=date, name=text))
            menu(bot, update)


def sub_student(bot, update):
    action = db_user.get_action(update.message.from_user.id)
    user = update.message.from_user
    text = update.message.text

    if action[0] == 'sub_student':
        if text == '[ ОТПИСАТСЯ ]':
            text = None
            update.message.reply_text('Вы успешно отписаны')
        else:
            update.message.reply_text('Подписка успешно установлена на группу ' + text)

        db_user.set_sub_student(id=user.id, group=text)
        menu(bot, update)
    else:
        groups = [[KeyboardButton('[ В МЕНЮ ]')]]
        for group in schedule.get_student_list():
            groups.append([KeyboardButton(group)])

        sub = db_user.get_sub_student(user.id)
        info = 'Вы сейчас не подписаны'
        if sub is not None:
            info = 'Вы сейчас подписаны на группу ' + sub
            groups[0].append(KeyboardButton('[ ОТПИСАТСЯ ]'))

        update.message.reply_text('Выберите или введите группу, на которую вы хотите подписатся\n' + info,
                                  reply_markup=ReplyKeyboardMarkup(groups, one_time_keyboard=True))

        db_user.set_action(id=user.id, action='sub_student')


def sub_teacher(bot, update):
    action = db_user.get_action(update.message.from_user.id)
    user = update.message.from_user
    text = update.message.text

    if action[0] == 'sub_teacher':
        if text == '[ ОТПИСАТСЯ ]':
            text = None
            update.message.reply_text('Вы успешно отписаны')
        else:
            update.message.reply_text('Подписка успешно установлена на преподавателя ' + text)

        db_user.set_sub_teacher(id=user.id, name=text)
        menu(bot, update)
    else:
        teachers = [[KeyboardButton('[ В МЕНЮ ]')]]
        for teacher in schedule.get_teacher_list():
            teachers.append([KeyboardButton(teacher)])

        sub = db_user.get_sub_teacher(user.id)
        info = 'Вы сейчас не подписаны'
        if sub is not None:
            info = 'Вы сейчас подписаны на преподавателя ' + sub
            teachers[0].append(KeyboardButton('[ ОТПИСАТСЯ ]'))

        update.message.reply_text('Выберите или введите преподавателя, на которого вы хотите подписатся\n' + info,
                                  reply_markup=ReplyKeyboardMarkup(teachers, one_time_keyboard=True))

        db_user.set_action(id=user.id, action='sub_teacher')


def menu(bot, update):  # Start menu
    db_user.set_action(id=update.message.from_user.id, action='')

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


def processor(bot, update):
    user = update.message.from_user
    text = update.message.text
    action = db_user.get_action(user.id)
    db_user.update(user)

    logger.info('{} {} ({}:@{}): {}'.format(user.first_name, user.last_name, user.id, user.username, text))

    if text == '[ В МЕНЮ ]' or text.startswith('/start'):
        menu(bot, update)

    elif text == '[ ЗАКРЫТЬ ]' or text.startswith('/cancel'):
        update.message.reply_text('Меню закрыто.', reply_markup=ReplyKeyboardRemove())
        db_user.set_action(user.id, '')

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
        update.message.reply_text(db_content.get('bells'))
        menu(bot, update)

    elif text == 'ОБ АВТОРЕ':
        update.message.reply_text(db_content.get('about'))
        menu(bot, update)
