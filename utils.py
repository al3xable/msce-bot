import json


def get_settings():
    with open('locale.json', encoding='UTF-8') as data_file:
        data = json.load(data_file)
    return data


def get_config():
    with open('bot.json', encoding='UTF-8') as data_file:
        data = json.load(data_file)
    return data


def get_constant(constant_name):
    if constant_name in get_settings()['constants']:
        return get_settings()['constants'][constant_name]


def get_text(filename):
    with open('./text/{filename}'.format(filename=filename), encoding='UTF-8') as file:
        return file.read()


def generate_markup(buttons,
                    n_cols=1,
                    header_buttons=None,
                    footer_buttons=None
                    ):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu
