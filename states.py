from aiogram.utils.helper import Helper,HelperMode,ListItem,Item,ItemsList



class BotStates(Helper):
    mode = HelperMode.snake_case

    START = Item()
    TRAKING = Item()
    END = Item()