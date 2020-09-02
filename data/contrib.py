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

    async def test_new_service(self, bot, query: types.CallbackQuery ,new_service_data: dict) -> None:
        """Creates a fake service to check whether user likes everything he has done"""

        photo_to_send = await bot.download_file(new_service_data["photo"].file_path)

        await bot.send_photo(query.message.chat.id, photo=photo_to_send.read())
        await bot.send_message(
            query.message.chat.id,
             text="Информация новой услуги\nНазвание: %s\n%sОписание: %s\n%sЦена: %s %s\n" % (
                new_service_data["name"],
                (("Название на немецком: " + new_service_data["name_de"] + "\n") if new_service_data.get("name_de") else ""),
                new_service_data["description"],
                (("Описание на немецком: " + new_service_data["description_de"] + "\n") if new_service_data.get("description_de") else ""),
                new_service_data["price"],
                new_service_data["currency"]
             ))

    async def create_new_service(self, bot, query: types.CallbackQuery, new_service_data: dict) -> None:
        """Creates a new service"""

        photo_to_save = await bot.download_file(new_service_data["photo"].file_path)

        self.service.create_entry(data={
            "name": new_service_data["name"],
            "name_de": new_service_data["name_de"],
            "description": new_service_data["description"],
            "description": new_service_data["description_de"],
            "price": new_service_data["price"],
            "currency": new_service_data["currency"]
            }, files={
                "photo": (await utils.get_random_id(new_service_data["photo"].file_path.split(".")[-1]), photo_to_save)
            })


class DoctorInfo(SourceSetting):


    async def get_about_text(self, bot, message):
        """Returns some info about doctor and checks whether generally it is"""

        if info_about := self.info.get_data()["results"]:
            await bot.send_message(message.chat.id, "Ваше описание")
            await bot.send_message(message.chat.id, info_about[0]["about_text"])

            return await bot.send_message(
                message.chat.id, "Хотите изменить его?", 
                reply_markup=await create_yesno_keyboard(["CHANGEyes", "CHANGEno"], ["Да", "Нет"]))

        await bot.send_message(message.chat.id, "Ваше описание не заполнено")
        await bot.send_message(
            message.chat.id, "Хотите добавить его?", 
            reply_markup=await create_yesno_keyboard(["ADDABOUTyes", "ADDABOUTno"], ["Да", "Нет"]))


    async def set_about_text(self, bot, query, data):
        """Sets new informations about doctor"""
        
        if result_set := self.info.get_data()["results"]:
            return self.info.update_data(params={"pk":result_set[0]["id"]},json_data=data)
        return self.info.create_entry(data=data)


class VisitImage(SourceSetting):
    """A class to work with visitimage model stated with API"""
    
    async def get_visit_images(self, bot, query):
        """Returns all the images if they are or send the notification absence"""

        if data := self.visitimages.get_data()["results"]:
            for index, entries in enumerate(data):
                image_url = await utils.format_url(entries["visit_image"])
                image_in_bytes = await utils.convert_link_into_image(image_url)
                await query.answer("Изображение №%d" % (index + 1)) 
                current_state = dp.current_state(user=query.from_user.id)
                await current_state.set_state(ChangeVisitImage.EDIT_IMAGE)
                await bot.send_photo(
                    query.chat.id, 
                    image_in_bytes.read(), 
                    reply_markup=await create_yesno_keyboard([entries["id"]], ["Редактировать"]))
            return 
        await query.answer("Пока что нет никаких изображений")


    async def set_visit_image(self, bot, query, data):
        """Sets a new visitimage"""
        
        random_name = await utils.get_random_id(data[query.from_user.id]["visitimage"].file_path.split(".")[-1])
        photo = await bot.download_file(data[query.from_user.id]["visitimage"].file_path)

        self.visitimages.update_data(
            params={"pk":data[query.from_user.id]["pk"]}, 
            files={
                "visit_image":(random_name, photo)
            })

    
    async def delete_visit_image(self, bot, query):
        pass

    