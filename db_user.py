from db_models import *


def update(user):
    session = get_session()
    if get_user(user.id) is None:
        new_user = Users(id=user.id, first_name=user.first_name, last_name=user.last_name, username=user.username)
        session.add(new_user)
    else:
        upd_user = get_user(user.id)
        upd_user.first_name = user.first_name
        upd_user.last_name = user.last_name
        upd_user.username = user.username
        session.add(upd_user)
    session.commit()
    session.close()


def get():
    session = get_session()
    users = []
    for user in session.query(Users).all():
        users.append(user)
    session.close()
    return users


def get_al(id=None):
    user = get_user(id)
    if user is None:
        return 0
    else:
        return user.al


def get_user(id=None):
    if id is not None:
        session = get_session()
        user = session.query(Users).filter_by(id=id).first()
        session.close()
        return user
    return None


def set_action(id=None, action=''):
    session = get_session()
    user = get_user(id)
    user.action = action
    session.add(user)
    session.commit()
    session.close()


def get_action(id=None):
    user = get_user(id)
    if user is None:
        return ['']
    else:
        return user.action.split('/')


def set_sub_student(id=None, group=''):
    session = get_session()
    user = get_user(id)
    user.sub_student = group
    session.add(user)
    session.commit()
    session.close()


def get_sub_student(user=None):
    user = get_user(user.id)
    if user is not None:
        return user.sub_student
    else:
        return ''


def set_sub_teacher(id=None, name=''):
    session = get_session()
    user = get_user(id)
    user.sub_teacher = name
    session.add(user)
    session.commit()
    session.close()


def get_sub_teacher(user=None):
    user = get_user(user.id)
    if user is not None:
        return user.sub_teacher
    else:
        return ''
