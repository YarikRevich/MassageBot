import requests
import asyncio
import json
import os
from aiogram import types
from notification_formatter import FormattedInfo
from RJAPI.contrib import RJAPI
import datetime

class Data(RJAPI):

    class Meta:
        url = "http://localhost:8000/ru/api/records/"
        auth_data = (os.getenv("USERNAME"),os.getenv("PASS"))

data = Data()

async def start_pooling(bot):

    while True:
        await asyncio.sleep(3)
        info = data.get_and_update_json(json_data={"seen":True},filters={"seen":False},put_method=True)
        if info:
            for dictionary in info["results"]:
                formatter = FormattedInfo(dictionary)

                markup = types.InlineKeyboardMarkup()
                button1 = types.InlineKeyboardButton("Указать как выполненый!",callback_data=dictionary["id"])
                markup.add(button1)

                await bot.send_message(os.getenv("USER_ID"),formatter.get_info,reply_markup=markup)
        else:
            pass
        await asyncio.sleep(3)
        
class Tutorial:

    @property
    async def get_test_record(self) -> str:
        test_data = {
            "author":"Василий",
            "name":"Массаж спины",
            "description":"Прошу массаж помягче",
            "time":"2020-08-18T11:52:44.236541+03:00",
            "phone":"0632260575",
        }
        formatter = FormattedInfo(test_data)
        return formatter.get_info

    @property
    async def get_tutorial_description_message(self) -> str:
        return "🤗 Приветсвую Вас в обучении!\nНиже Вы видете тестовую запись клиента на сеанс,изучите её!"

    @property
    async def get_record_user_name_review(self) -> str:
        return "1️⃣ На первой строке Вы видете Имя клиента сделавшего запись(Тут,думаю,ничего сложного нет)"

    @property
    async def get_record_service_name(self) -> str:
        return "2️⃣ На второй строчке Вы видете название услуги,которую выбрал клиент"

    @property
    async def record_description_review(self) -> str:
        return "3️⃣ На третей строке Вы виделет описание которое сделал клиент для того что бы уведомить Вас о чем-то нетриввиальном"

    @property
    async def record_time_review(self) -> str:
        return "4️⃣ На четвертой строчке Вы видете время,когда клиент сделал запись"

    @property
    async def record_phone_review(self) -> str:
        return "5️⃣ Ну и на последней строке Вы можете наблюдать номер телефона клиента с помощью которого Вы можете коммуницировать с ним"

    @property
    async def answer_review(self) -> str:
        return "✅ Под тестовой записью Вы можете увидеть кнопку.Нажав на неё Вы укажете,что данный заказ был выполнен\nНу,а сейчас,для теста,нажмите на кнопку и Вы увидете сюрприз!"

async def send_tutorial(query: types.InlineQuery) -> str:

    tutorial = Tutorial()

    all_messages = [
        await tutorial.get_tutorial_description_message,
        await tutorial.get_test_record,
        await tutorial.get_record_user_name_review,
        await tutorial.get_record_service_name,
        await tutorial.record_description_review,
        await tutorial.record_time_review,
        await tutorial.record_phone_review,
        await tutorial.answer_review

    ]
    
    for message in all_messages:
        if message == await tutorial.get_test_record:
            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton("Указать как выполненый!",callback_data="tutorial")
            markup.add(button1)
            await query.message.answer(message, reply_markup=markup)
        else:
            await query.message.answer(message)