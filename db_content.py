from db_models import *


def get(name=None):  # Get user access level
    session = get_session()
    line = session.query(Content).filter_by(name=name).first().content
    session.close()
    if len(line) == 0:
        return 0
    else:
        return line
