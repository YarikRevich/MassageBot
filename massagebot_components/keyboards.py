from aiogram import types

async def create_yesno_keyboard(callback_data: list, text: list) -> object:
    """Creates a simple InlineKeyboard with 'no' and 'yes' buttons"""

    markup = types.InlineKeyboardMarkup()
    for index in range(0, len(callback_data)):
        button = types.InlineKeyboardButton(callback_data="%s" % (callback_data[index],), text="%s" % (text[index]))
        markup.add(button)
    return markup


async def create_reply_keyboard(text: list) -> object:
    """Creates a simple ReplyKeyboard"""

    markup = types.ReplyKeyboardMarkup()
    for data in text:
        button = types.KeyboardButton(text=data)
        markup.add(button)
    return markup