import sqlite3


def update(user):
    db = sqlite3.connect('bot.db')

    if len(db.execute("SELECT id FROM users WHERE id=?", [user.id]).fetchall()) == 0:
        db.execute("INSERT INTO users (id,first_name,last_name,username) VALUES (?,?,?,?)",
                   [user.id, user.first_name, user.last_name, user.username])
    else:
        db.execute("UPDATE users SET id=?, first_name=?, last_name=?, username=? WHERE id=?",
                   [user.id, user.first_name, user.last_name, user.username, user.id])

    db.commit()
    db.close()


def get():
    db = sqlite3.connect('bot.db')
    users = []
    for user in db.execute("SELECT id FROM users").fetchall():
        users.append(user[0])
    db.close()
    return users


def get_al(id=None):  # Get user access level
    db = sqlite3.connect('bot.db')
    user = db.execute("SELECT al FROM users WHERE id=?", [id]).fetchall()
    db.close()

    if len(user) == 0:
        return 0
    else:
        return user[0][0]


def set_action(id=None, action=''):  # Set user action
    db = sqlite3.connect('bot.db')
    db.execute("UPDATE users SET action=? WHERE id=?", [action, id])
    db.commit()
    db.close()


def get_action(id=None):  # Get user action
    db = sqlite3.connect('bot.db')
    user = db.execute("SELECT action FROM users WHERE id=?", [id]).fetchall()
    db.close()

    if len(user) == 0:
        return ['']
    else:
        return user[0][0].split('/')


def set_sub_student(id=None, group=''):  # Subscribe to student group
    db = sqlite3.connect('bot.db')
    db.execute("UPDATE users SET sub_student=? WHERE id=?", [group, id])
    db.commit()
    db.close()


def get_sub_student(id=None):  # Get student subscribe group
    db = sqlite3.connect('bot.db')
    user = db.execute("SELECT sub_student FROM users WHERE id=?", [id]).fetchall()
    db.close()

    if len(user) > 0:
        return user[0][0]
    else:
        return ''


def set_sub_teacher(id=None, name=''):  # Subscribe to teacher
    db = sqlite3.connect('bot.db')
    db.execute("UPDATE users SET sub_teacher=? WHERE id=?", [name, id])
    db.commit()
    db.close()


def get_sub_teacher(id=None):  # Get teacher subscribe
    db = sqlite3.connect('bot.db')
    user = db.execute("SELECT sub_teacher FROM users WHERE id=?", [id]).fetchall()
    db.close()

    if len(user) > 0:
        return user[0][0]
    else:
        return ''
