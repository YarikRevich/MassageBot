import requests
import asyncio
import random
import json
import os
import datetime
from aiogram import types
from .notification_formatter import FormattedInfo
from RJAPI.contrib import RJAPI
from data.source_settings import SourceSetting
from .utils import Utils

class Record(SourceSetting):
    """Class for the work records gotten from web-application"""

    utils = Utils()

    async def start_pooling(self, bot):
        """Func for the listening to new records.
        Firstly it checks for the new records(as said before)
        and updates them to 'seen'.After, it sends a message
        where said that a new client has made a record
        """

        while True:
            await asyncio.sleep(3)
            info = self.record.get_and_update_json(json_data={"seen":True},filters={"seen":False},patch_method=True)
            if info:
                for dictionary in info["results"]:
                    formatter = FormattedInfo(dictionary)

                    markup = types.InlineKeyboardMarkup()
                    button1 = types.InlineKeyboardButton("Указать как выполненый!",callback_data=dictionary["id"])
                    markup.add(button1)

                    await bot.send_message(os.getenv("USER_ID"),await formatter.get_formatted_data,reply_markup=markup)
            else:
                pass
            await asyncio.sleep(3)



class Service(SourceSetting):
    """Class for the work with service model from web-application"""

    utils = Utils()

    async def test_new_service(self, bot, query: types.CallbackQuery ,new_service_data: dict) -> None:
        """Creates a fake service to check whether user likes everything he has done"""

        photo_to_send = await bot.download_file(new_service_data["photo"].file_path)

        await bot.send_photo(query.message.chat.id, photo=photo_to_send.read())
        await bot.send_message(
            query.message.chat.id,
             text="Информация новой услуги\nНазвание: %s\nОписание: %s\nЦена: %s %s\n" % (
                new_service_data["name"],
                new_service_data["description"],
                new_service_data["price"],
                new_service_data["currency"]
             ))

    async def create_new_service(self, bot, query: types.CallbackQuery, new_service_data: dict) -> None:
        """Creates a new service"""

        photo_to_save = await bot.download_file(new_service_data["photo"].file_path)

        self.service.create_entry(data={
            "name": new_service_data["name"],
            "description": new_service_data["description"],
            "price": new_service_data["price"],
            "currency": new_service_data["currency"]
            }, files={
                f"photo": (await self.utils.get_random_id(
                        new_service_data["photo"].file_path.split(".")[-1]
                ), photo_to_save)
            })
