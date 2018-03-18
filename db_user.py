import sqlite3

DATABASE_NAME = 'bot.db'


def update(user):
    db = sqlite3.connect(DATABASE_NAME)

    if len(db.execute("SELECT id FROM users WHERE id=?", [user.id]).fetchall()) == 0:
        db.execute("INSERT INTO users (id,first_name,last_name,username) VALUES (?,?,?,?)",
                   [user.id, user.first_name, user.last_name, user.username])
    else:
        db.execute("UPDATE users SET id=?, first_name=?, last_name=?, username=? WHERE id=?",
                   [user.id, user.first_name, user.last_name, user.username, user.id])

    db.commit()
    db.close()


def get():
    db = sqlite3.connect(DATABASE_NAME)
    users = []
    for user in db.execute("SELECT id FROM users").fetchall():
        users.append(user[0])
    db.close()
    return users


def get_al(user_id=None):  # Get user access level
    db = sqlite3.connect(DATABASE_NAME)
    user = db.execute("SELECT al FROM users WHERE id=?", [user_id]).fetchall()
    db.close()

    if len(user) == 0:
        return 0
    else:
        return user[0][0]


def set_action(user_id=None, action=''):  # Set user action
    db = sqlite3.connect(DATABASE_NAME)
    db.execute("UPDATE users SET action=? WHERE id=?", [action, user_id])
    db.commit()
    db.close()


def get_action(user_id=None):
    """Get user's action and params
           Parameters
           ----------
           user_id : int
               User's id
           Returns
           -------
            str
                Action
            list
                Params
           """
    db = sqlite3.connect(DATABASE_NAME)
    user = db.execute("SELECT action FROM users WHERE id=?", [user_id]).fetchall()
    db.close()
    try:
        if user is None or len(user) == 0:
            return '', []
        else:
            splitted = user[0][0].split('/')
            return splitted[0], splitted[1:]
    except:
        return '', []



def set_sub_student(user_id=None, group=''):  # Subscribe to student group
    db = sqlite3.connect(DATABASE_NAME)
    db.execute("UPDATE users SET sub_student=? WHERE id=?", [group, user_id])
    db.commit()
    db.close()


def get_sub_student(user_id=None):  # Get student subscribe group
    db = sqlite3.connect(DATABASE_NAME)
    user = db.execute("SELECT sub_student FROM users WHERE id=?", [user_id]).fetchall()
    db.close()

    if len(user) > 0:
        return user[0][0]
    else:
        return ''


def set_sub_teacher(user_id=None, name=''):  # Subscribe to teacher
    db = sqlite3.connect(DATABASE_NAME)
    db.execute("UPDATE users SET sub_teacher=? WHERE id=?", [name, user_id])
    db.commit()
    db.close()


def get_sub_teacher(user_id=None):  # Get teacher subscribe
    db = sqlite3.connect(DATABASE_NAME)
    user = db.execute("SELECT sub_teacher FROM users WHERE id=?", [user_id]).fetchall()
    db.close()

    if len(user) > 0:
        return user[0][0]
    else:
        return ''
