from aiogram.utils.helper import Item, Helper, HelperMode

class AddService(Helper):

    mode = HelperMode.lowerCamelCase

    CONFIRMING = Item()
    NAME = Item()
    DESCRIPTION = Item()
    PRICE = Item()
    CURRENCY = Item()
    PHOTO = Item()