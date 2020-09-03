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
from massagebot_components.states import ChangeVisitImage
from massagebot_components.bot_settings import dp
from massagebot_components.keyboards import create_yesno_keyboard


utils = Utils()

class Record(SourceSetting):
    """Class for the work records gotten from web-application"""

    

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

                    await bot.send_message(
                        os.getenv("USER_ID"),
                        await formatter.get_formatted_data,
                        reply_markup=await create_yesno_keyboard([dictionary["id"]], ["Указать как выполненый!"]))
            else:
                pass
            await asyncio.sleep(3)



class Service(SourceSetting):
    """Class for the work with service model from web-application"""

    async def create_new_service(self, data: dict, photo, photo_path: str) -> None:
        """Creates a new service"""

        self.service.create_entry(data=data, files={"photo": (await utils.get_random_id(photo_path.split(".")[-1]), photo)})


class DoctorInfo(SourceSetting):


    async def get_about_text(self) -> bool:
        """Returns some info about doctor and checks whether generally it is"""

        if info_about := self.info.get_data()["results"]:
            return info_about[0]["about_text"]
        return False


    async def set_about_text(self, data) -> bool:
        """Sets new informations about doctor"""
        
        if result_set := self.info.get_data()["results"]:
            return self.info.update_data(params={"pk":result_set[0]["id"]},json_data=data)
        return self.info.create_entry(data=data)


class VisitImage(SourceSetting):
    """A class to work with visitimage model stated with API"""
    
    async def get_visit_images(self) -> bool:
        """Returns all the images if they are or send the notification absence"""

        if data := self.visitimages.get_data()["results"]:
            visit_images = []
            for index, entries in enumerate(data):
                image_url = await utils.format_url(entries["visit_image"])
                image_in_bytes = await utils.convert_link_into_image(image_url)
                visit_images.append((entries["id"], image_in_bytes.read()))
            return visit_images
        return False


    async def set_visit_image(self, data) -> None:
        """Sets a new visitimage"""
        
        random_name = await utils.get_random_id(data["visitimage"].file_path.split(".")[-1])

        self.visitimages.update_data(
            params={"pk":data["pk"]}, 
            files={
                "visit_image":(random_name, data["visitimage"])
            })

    
    async def delete_visit_image(self, param) -> None:
        """Deletes an equal visit image"""

        self.visitimages.delete_data(params=param)

    