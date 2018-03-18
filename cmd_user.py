import logging

from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
import utils
import db_user
import schedule

logger = logging.getLogger(__name__)


def generic_menu(menu_name, update: Update):
    settings = utils.get_settings()
    if menu_name in settings:
        menu = settings[menu_name]
        buttons = []
        for button in menu['keyboard']:
            buttons.append(get_button_text(button))
        buttons = ReplyKeyboardMarkup(utils.generate_markup(buttons))
        update.effective_message.reply_text(menu['text'], reply_markup=buttons)
        db_user.set_action(user_id=update.effective_user.id, action=menu_name)


def get_student(bot, update):
    action, params = db_user.get_action(update.message.from_user.id)
    user = update.message.from_user
    text = update.message.text

    if action == 'get_student':
        if len(params) > 0:
            # If we have more than one param(it's probably date) then print group's schedule with that param
            date = params[0]
            update.message.reply_text(schedule.get_student(date=date, group=text))
            default_menu(bot, update)
        else:
            # If we have none params, then we should save date and let user enter group
            date = text.split(',')[0]
            groups = [[KeyboardButton(utils.get_constant('back_to_menu'))]]
            for group in schedule.get_student_groups(date):
                groups.append([KeyboardButton(group['title'])])

            update.message.reply_text(utils.get_constant('enter_group'),
                                      reply_markup=ReplyKeyboardMarkup(groups, one_time_keyboard=True))

            db_user.set_action(user_id=user.id, action='get_student/{date}'.format(date=date))

    else:
        # Choose date if action isn't "get_student"
        dates = [[KeyboardButton(utils.get_constant('back_to_menu'))]]
        for date in sorted(schedule.get_student_dates(), reverse=True):
            dates.append([KeyboardButton(date + ', ' + schedule.get_weekday(date))])

        update.message.reply_text(utils.get_constant('enter_date'),
                                  reply_markup=ReplyKeyboardMarkup(dates, one_time_keyboard=True))
        db_user.set_action(user_id=user.id, action='get_student')


def get_teacher(bot, update):
    action, params = db_user.get_action(update.message.from_user.id)
    user = update.message.from_user
    text = update.message.text

    if action == 'get_teacher':
        if len(params) > 0:
            # If we have more than one param(it's probably date) then print schedule with that param
            date = params[0]
            update.message.reply_text(schedule.get_teacher(date=date, name=text))
            default_menu(bot, update)
        else:
            # If we have none params, then we should save date and let user enter teacher's name
            date = text.split(',')[0]
            teachers = [[KeyboardButton(utils.get_constant('back_to_menu'))]]
            for teacher in schedule.get_teacher_names(date):
                teachers.append([KeyboardButton(teacher['title'])])

            update.message.reply_text(utils.get_constant('enter_teacher'),
                                      reply_markup=ReplyKeyboardMarkup(teachers, one_time_keyboard=True))

            db_user.set_action(user_id=user.id, action='get_teacher/' + date)
    else:
        # Choose date if action isn't "get_teacher"
        dates = [[KeyboardButton(utils.get_constant('back_to_menu'))]]
        for date in sorted(schedule.get_teacher_dates(), reverse=True):
            dates.append([KeyboardButton(date + ', ' + schedule.get_weekday(date))])

        update.message.reply_text(utils.get_constant('enter_date'),
                                  reply_markup=ReplyKeyboardMarkup(dates, one_time_keyboard=True))
        db_user.set_action(user_id=user.id, action='get_teacher')


def sub_student(bot, update):
    user = update.message.from_user
    action, params = db_user.get_action(user.id)
    text = update.message.text

    if action == 'sub_student':
        if text == utils.get_constant('unsubscribe'):
            text = None
            update.message.reply_text(utils.get_constant('suc_unsubscribe'))
        else:
            update.message.reply_text(utils.get_constant('suc_subscribe_group').format(group=text))

        db_user.set_sub_student(user_id=user.id, group=text)
        default_menu(bot, update)
    else:
        groups = [[KeyboardButton(utils.get_constant('back_to_menu'))]]
        for group in schedule.get_student_list():
            groups.append([KeyboardButton(group)])

        sub = db_user.get_sub_student(user.id)
        info = utils.get_constant('not_subscribed_info')
        if sub is not None:
            info = utils.get_constant('subscribed_info_group').format(group=sub)
            groups[0].append(KeyboardButton(utils.get_constant('unsubscribe')))

        update.message.reply_text(utils.get_constant('subscribe_group').format(info=info),
                                  reply_markup=ReplyKeyboardMarkup(groups, one_time_keyboard=True))

        db_user.set_action(user_id=user.id, action='sub_student')


def sub_teacher(bot, update):
    user = update.message.from_user
    action, params = db_user.get_action(user.id)
    text = update.message.text

    if action == 'sub_teacher':
        if text == utils.get_constant('unsubscribe'):
            text = None
            update.message.reply_text(utils.get_constant('suc_unsubscribe'))
        else:
            update.message.reply_text(utils.get_constant('suc_subscribe_teacher').format(teacher=text))
        db_user.set_sub_teacher(user_id=user.id, name=text)
        default_menu(bot, update)
    else:
        teachers = [[KeyboardButton(utils.get_constant('back_to_menu'))]]
        for teacher in schedule.get_teacher_list():
            teachers.append([KeyboardButton(teacher)])

        sub = db_user.get_sub_teacher(user.id)
        info = utils.get_constant('not_subscribed_info')
        if sub is not None:
            info = utils.get_constant('subscribed_info_teacher').format(teacher=sub)
            teachers[0].append(KeyboardButton(utils.get_constant('unsubscribe')))

        update.message.reply_text('Выберите или введите преподавателя, на которого вы хотите подписатся\n'+info,
                                  reply_markup=ReplyKeyboardMarkup(teachers, one_time_keyboard=True))

        db_user.set_action(user_id=user.id, action='sub_teacher')


def default_menu(bot, update):
    settings = utils.get_settings()
    generic_menu(menu_name=settings['default_menu'], update=update)


def action_manager(bot, update, action):
    if action == 'get_student':
        try:
            get_student(bot, update)
        except schedule.ScheduleException as ex:
            if ex.code == 200:
                update.message.reply_text(utils.get_constant('no_schedule_for_date'))
            elif ex.code == 201:
                update.message.reply_text(utils.get_constant('no_group_schedule'))
            else:
                update.message.reply_text(utils.get_constant('unknown_error').format(code=ex.code,
                                                                                     message=ex.message))
    elif action == 'get_teacher':
        try:
            get_teacher(bot, update)
        except schedule.ScheduleException as ex:
            if ex.code == 200:
                update.message.reply_text(utils.get_constant('no_schedule_for_date'))
            elif ex.code == 201:
                update.message.reply_text(utils.get_constant('no_teacher_schedule'))
            else:
                update.message.reply_text(utils.get_constant('unknown_error').format(code=ex.code,
                                                                                     message=ex.message))
    elif action == 'sub_student':
        sub_student(bot, update)
    elif action == 'sub_teacher':
        sub_teacher(bot, update)
    elif action == 'close_keyboard':
        close_keyboard(bot, update)
    elif action == 'default_menu':
        default_menu(bot, update)
    return


def close_keyboard(bot, update):
    update.message.reply_text(utils.get_constant('menu_closed'), reply_markup=ReplyKeyboardRemove())
    db_user.set_action(update.effective_user.id, '')


def get_button_text(button):
    if 'text' in button:
        return button['text']
    elif 'constant' in button:
        return utils.get_constant(button['constant'])
    return ''


def behave(button, bot, update):
    if 'menu' in button:
        generic_menu(button['menu'], update)
    elif 'action' in button:
        action_manager(bot, update, button['action'])
    elif 'text_file' in button:
        update.effective_message.reply_text(utils.get_text(button['text_file']))
    elif 'text' in button:
        update.effective_message.reply_text(button['text'])


# bot's entry point
def processor(bot, update):
    user = update.message.from_user
    text = update.message.text
    action, params = db_user.get_action(user.id)
    settings = utils.get_settings()
    db_user.update(user)

    # Check if it is group chat
    if update.message.chat.id < 0:
        if text.startswith('/'):
            update.message.reply_text(utils.get_constant('not_chat'))
        return

    # logging
    logger.info('{} {} ({}:@{}): {}'.format(user.first_name, user.last_name, user.id, user.username, text))

    # Constant behavior
    for button in settings['constant_behavior']:
        if utils.get_constant(button) == text:
            behave(settings['constant_behavior'][button], bot, update)
            return

    # Checking menu
    if action in settings:
        for button in settings[action]['keyboard']:
            if get_button_text(button) == text:
                behave(button, bot, update)
    else:
        action_manager(bot, update, action)


