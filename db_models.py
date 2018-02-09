# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_URI = 'sqlite:///bot_database.db'
Base = declarative_base()
engine = create_engine(DB_URI, echo=False)


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, unique=True)
    first_name = Column(String, default='NULL')
    last_name = Column(String, default='NULL')
    username = Column(String, default='NULL')
    al = Column(Integer, default=0)
    action = Column(String, default='')
    sub_student = Column(String, default='NULL')
    sub_teacher = Column(String, default='NULL')

    def __init__(self, id, username, first_name, last_name):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return "<User('%s', '%s', '%s')>" % (self.username, self.first_name, self.last_name)


class Content(Base):
    __tablename__ = 'content'
    name = Column(String, primary_key=True, unique=True)
    content = Column(String)

    def __init__(self, name, content):
        self.name = name
        self.content = content

    def __repr__(self):
        return "<Content object('%s', '%s')>" % (self.name, self.content)


def get_session():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    about = Content(name='about',
                    content='Если у вас есть замечания или предложения, то я с удовольствием готов их выслушать в лс :)\nРазработчик бота - @al3xable\nДоработал бота - @wh1tef0x')
    bells = Content(name='bells',
                    content='🏛 Расписание звонков на Казинца:\nПН-ПТ:\n1 пара: 9.00 – 9.45, 9.55 – 10.40\n2 пара: 10.50 – 11.35, 11.55 – 12.40\n3 пара: 13.00– 13.45, 13.55 – 14.40\n4 пара: 14.50 – 15.35, 15.45 – 16.30\nСУББОТА:\n1 пара: 9.00 – 10.20\n2 пара: 10.40 –11.25, 11.45 – 12.30\n3 пара: 12.40- 14.00\n4 пара: 14.10 – 15.30\n\n🏛 Расписание звонков на Кнорина:\nПН-ПТ:\n1 пара: 09:00 – 09:45, 09:55 – 10:40\n2 пара: 11:00 – 11:45, 12:05 – 12:50\n3 пара: 13:10 – 13:55, 14:05 – 14:50\n4 пара: 15:00 – 15:45, 15:55 – 16:40\nСУББОТА:\n1 пара: 09:00 – 10:20\n2 пара: 10:30 – 11:20, 11:35 – 12:20\n3 пара: 12:35 – 13:55\n4 пара: 14:05 – 15:25')
    master_help = Content(name='master_help',
                          content='List of available commands:\n/help -- list of available commands\n/tbcast <text> -- text broadcast\n/sbcast <student|teacher|all> -- schedule broadcast\n/stop -- stop bot\n/get_config -- get current config\nYou can upload .json file to change config')
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(about)
    session.add(bells)
    session.add(master_help)
    session.commit()
    session.close()
