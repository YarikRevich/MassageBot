from aiogram.utils.helper import Item, Helper, HelperMode

class AddService(Helper):
    """Special stater for the adding a new service.
    Contains such states as:
    -> CONFIRMING (works when bot asks user whether he wants to add a new service)
    -> NAME (works when user wants to add a name)
    -> DESCRIPTION (keeps active when user wants to add description)
    -> PRICE (when user adds price to the new service)
    -> CURRENCY (keeps active when user wants to add a currency)
    -> PHOTO (when user adds image to his service)
    
    """

    mode = HelperMode.lowerCamelCase

    CONFIRMING = Item()
    NAME = Item()
    DESCRIPTION = Item()
    PRICE = Item()
    CURRENCY = Item()
    PHOTO = Item()