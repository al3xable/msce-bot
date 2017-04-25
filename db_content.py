import sqlite3


def get(name=None):  # Get user access level
    db = sqlite3.connect('bot.db')
    user = db.execute("SELECT content FROM content WHERE name=?", [name]).fetchall()
    db.close()

    if len(user) == 0:
        return 0
    else:
        return user[0][0]
