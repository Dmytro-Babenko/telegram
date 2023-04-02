from aiogram.types.reply_keyboard import KeyboardButton, ReplyKeyboardMarkup



def make_registration_kb():
    reg_button = KeyboardButton('Надішліть контакт', request_contact=True)
    reg_kb = ReplyKeyboardMarkup([[reg_button]], resize_keyboard=True, one_time_keyboard=True)
    return reg_kb

def make_main_kb():
    write_to_admin_button = KeyboardButton('Написати адміну')
    make_oder = KeyboardButton('Зробити замовлення')
    main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    main_kb.add(make_oder, write_to_admin_button)
    return main_kb

def make_create_order_kb(back=True, cancel=True, confirm=False, cancel_files=False):
    captions = {
        'Назад':back,
        'Скасувати замовлення': cancel, 
        'Підтвердити': confirm,
        'Скасувати відправку файлів': cancel_files
    }
    create_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for b_text, _ in filter(lambda x: x[1], captions.items()):
        create_kb.add(KeyboardButton(b_text))
    return create_kb

    if back:
        create_kb.add(KeyboardButton())
        





