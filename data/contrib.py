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
from massagebot_components.bot_settings import dp, bot
from massagebot_components.keyboards import create_yesno_keyboard
from massagebot_components.decorators import check_connection


utils = Utils()


class Record(SourceSetting):
    """Class for the work records gotten from web-application"""

    async def start_pooling(self):
        """Func for the listening to new records.
        Firstly it checks for the new records(as said before)
        and updates them to 'seen'.After, it sends a message
        where said that a new client has made a record
        """

        while True:
            await asyncio.sleep(5)
            if await utils.test_request(): 
                info = await self.record.get_and_update_json(json_data={"seen":True},filters={"seen":False},patch_method=True)
                if info:
                    for dictionary in info:
                        formatter = FormattedInfo(dictionary)
                        await bot.send_message(
                            os.getenv("USER_ID"),
                            await formatter.get_formatted_data,
                            reply_markup=await create_yesno_keyboard([dictionary["id"]], ["Указать как выполненый!"]))
                await asyncio.sleep(3)
            else:
                await utils.connection_revise()
                
                    
class Service(SourceSetting):
    """Class for the work with service model from web-application"""

    @check_connection
    async def create_new_service(self, data: dict, photo, photo_path: str) -> None:
        """Creates a new service"""

        await self.service.create_entry(data=data, files={"photo": (await utils.get_random_id(photo_path.split(".")[-1]), photo)})


class DoctorInfo(SourceSetting):


    @check_connection
    async def get_about_text(self) -> bool:
        """Returns some info about doctor and checks whether generally it is"""

        if info_about := await self.info.get_data():
            return info_about[0]["about_text"]
        return False


    @check_connection
    async def set_about_text(self, data) -> bool:
        """Sets new informations about doctor"""
        
        if result_set := await self.info.get_data():
            return await self.info.update_data(params={"pk":result_set[0]["id"]},json_data=data)
        return await self.info.create_entry(data=data)


class VisitImage(SourceSetting):
    """A class to work with visitimage model stated with API"""
    
    @check_connection
    async def get_visit_images(self) -> bool:
        """Returns all the images if they are or send the notification absence"""

        if data := await self.visitimages.get_data():
            visit_images = []
            for index, entries in enumerate(data):
                image_url = await utils.format_url(entries["visit_image"])
                image_in_bytes = await utils.convert_link_into_image(image_url)
                if image_in_bytes is not None:
                    visit_images.append((entries["id"], image_in_bytes.read()))
            return visit_images
        return False


    @check_connection
    async def set_visit_image(self, data) -> None:
        """Sets a new visitimage"""
        
        random_name = await utils.get_random_id(data["visitimage_path"].split(".")[-1])

        await self.visitimages.update_data(
            params={"pk":data["pk"]}, 
            files={
                "visit_image":(random_name, data["visitimage"].read())
            })

    
    @check_connection
    async def delete_visit_image(self, param) -> None:
        """Deletes an equal visit image"""

        await self.visitimages.delete_data(params=param)

    
    @check_connection
    async def add_new_visit_image(self, photo_path, photo) -> None:
        """Adds new visit image"""

        random_name = await utils.get_random_id(photo_path.split(".")[-1])
        await self.visitimages.create_entry(files={"visit_image":(random_name, photo.read())})
