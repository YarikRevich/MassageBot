import os
import asyncio
from data.utils import Utils
from massagebot_components.bot_settings import bot

utils = Utils()

def freeze_check(func: object) -> object:
    """Checks whther bot is freezed"""

    def wrapper(*args, **kwargs):
        if os.getenv("FREEZE"):
            loop = asyncio.get_event_loop()
            return loop.create_task(utils.send_freeze_error_message())
        return func(*args)
    return wrapper


def check_connection(func: object) -> object:
    """Checks a connection status with a server"""

    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        request = loop.create_task(utils.test_request())
        if request:
            return func(*args, **kwargs)
        return loop.create_task(utils.connection_revise())
    return wrapper