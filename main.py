import aiogram
import asyncio
import os
import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.builtin import CommandHelp,IDFilter
from data.contrib import Record, Service
from tutorial.tutorial import Tutorial
from tutorial.quiz import random_fact
from states import AddService
from validators import TypeValidator

#All the important data for the futher work

TOKEN = os.getenv("TOKEN")
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

#Important instances of classes for the futher work

record = Record()
service = Service()
tutorial = Tutorial()

#A dict for the adding a new service 

new_service = {}

#------------------

@dp.message_handler(IDFilter(user_id=os.getenv("USER_ID")), state="*", commands=["start"])
async def start_func(message: types.Message):
    """Handler for the /start command to start a relationship between user and bot"""    

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(callback_data="TUTORIALyes",text="Да")
    button2 = types.InlineKeyboardButton(callback_data="TUTORIALno",text="Нет")
    markup.add(button1, button2)
    await message.answer("😜Hello!Вас приветствует бот сделаный для администрирования сайта http://emassage.com\nЗдесь Вы можете:\n- Просматривать актуальные записи клиентов\n- Добавлять новые услуги\n- Мониторить статистику\n❗️Бот находится в розработке,его функционал будет расширяться")
    await message.answer("🥺Хотите пройти обучение?",reply_markup=markup)


@dp.message_handler(lambda message: message.text == "Добавить услугу",state="*")
async def start_adding_service(message: types.Message):
    """A handler to start an adding of a new service"""

    current_state = dp.current_state(user=message.from_user.id)
    await current_state.set_state(AddService.CONFIRMING)
    
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(callback_data="CONFIRMINGno", text="Нет")
    button2 = types.InlineKeyboardButton(callback_data="CONFIRMINGyes", text="Да")
    markup.add(button1, button2)

    await message.answer("Вы в разделе добавления услуги. Ви хотите продолжить?", reply_markup=markup)


@dp.message_handler(state=AddService.NAME)
async def add_name_to_service(message: types.Message):
    """Handler to process the adding of a name to a new service"""

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(callback_data="NAMEno", text="Нет,хочу поменять")
    button2 = types.InlineKeyboardButton(callback_data="NAMEyes", text="Да,хочу продолжить.")
    markup.add(button1, button2)
    await message.answer("Вы хотите создать услугу с названием '%s'.Вы уверены?" % (message.text), reply_markup=markup) 


@dp.message_handler(state=AddService.DESCRIPTION)
async def add_description_to_service(message: types.Message):
    """Handler to process the adding of a description to a new service"""

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(callback_data="DESCRIPTIONno", text="Нет,хочу поменять")
    button2 = types.InlineKeyboardButton(callback_data="DESCRIPTIONyes", text="Да,хочу продолжить.")
    markup.add(button1, button2)
    await message.answer("Вы написали '%s'.Вы уверены?" % (message.text), reply_markup=markup) 


@dp.message_handler(state=AddService.PRICE)
async def add_price_to_service(message: types.Message):
    """Handler to process the adding of a price to a new service"""

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(callback_data="PRICEno", text="Нет,хочу поменять")
    button2 = types.InlineKeyboardButton(callback_data="PRICEyes", text="Да,хочу продолжить.")
    markup.add(button1, button2)
    if await TypeValidator.is_digit(message.text):
        return await message.answer("Цена новосозданного услуги '%s'.Продолжим?" % (message.text), reply_markup=markup) 
    await message.answer("Цена не может быть текстом! Напишите правильно!")


@dp.callback_query_handler(lambda query: (query.data in ["EUR", "USD", "UAH", "CHF"]), state="*")
async def add_currency_to_service(query: types.CallbackQuery):
    """Handler to process the adding of a currency to a new service"""
    
    if query.data == "EUR":

        new_service[query.from_user.id]["currency"] = "EUR"
        await bot.delete_message(query.message.chat.id, message_id=query.message.message_id)
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.CURRENCY)
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(callback_data="CURRENCYno", text="Нет,хочу поменять")
        button2 = types.InlineKeyboardButton(callback_data="CURRENCYyes", text="Да,хочу продолжить.")
        markup.add(button1, button2)
        
        return await query.message.answer("Валюта для новой услуги - 'EUR'.Правильно?", reply_markup=markup) 


    elif query.data == "USD":

        new_service[query.from_user.id]["currency"] = "USD"
        await bot.delete_message(query.message.chat.id, message_id=query.message.message_id)
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.CURRENCY)
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(callback_data="CURRENCYno", text="Нет,хочу поменять")
        button2 = types.InlineKeyboardButton(callback_data="CURRENCYyes", text="Да,хочу продолжить.")
        markup.add(button1, button2)
        
        return await query.message.answer("Валюта для новой услуги - 'USD'.Правильно?", reply_markup=markup) 


    elif query.data == "UAH":

        new_service[query.from_user.id]["currency"] = "UAH"
        await bot.delete_message(query.message.chat.id, message_id=query.message.message_id)
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.CURRENCY)
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(callback_data="CURRENCYno", text="Нет,хочу поменять")
        button2 = types.InlineKeyboardButton(callback_data="CURRENCYyes", text="Да,хочу продолжить.")
        markup.add(button1, button2)
        
        return await query.message.answer("Валюта для новой услуги - 'UAH'.Правильно?", reply_markup=markup) 


    elif query.data == "CHF":

        new_service[query.from_user.id]["currency"] = "CHF"
        await bot.delete_message(query.message.chat.id, message_id=query.message.message_id)
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.CURRENCY)
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(callback_data="CURRENCYno", text="Нет,хочу поменять")
        button2 = types.InlineKeyboardButton(callback_data="CURRENCYyes", text="Да,хочу продолжить.")
        markup.add(button1, button2)
        
        return await query.message.answer("Валюта для новой услуги - 'CHF'.Правильно?", reply_markup=markup) 



@dp.message_handler(state=AddService.PHOTO, content_types=["photo"])
async def add_image_to_service(file :types.InputMediaPhoto):
    """Handler to process the adding of a photo to a new service"""

    photo = await file["photo"][0].get_file()
    photo_to_send = await bot.download_file(photo.file_path)
    await bot.send_photo(file.chat.id, photo=photo_to_send.read())
    new_service[file.from_user.id]["photo"] = photo
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(callback_data="PHOTOno", text="Нет")
    button2 = types.InlineKeyboardButton(callback_data="PHOTOyes", text="Да")
    markup.add(button1, button2)

    await bot.send_message(file.chat.id, text="Точно?", reply_markup=markup)


@dp.message_handler(state=AddService.PHOTO)
async def image_getter(message :types.Message):
    """Handler to notificate user that he needs to a photo not a text"""

    await message.answer(text="Текст - не фото!")


@dp.message_handler(CommandHelp(),IDFilter(user_id=os.getenv("USER_ID")),state="*")
async def help_command(message :types.Message):
    """Sends some information about this bot"""

    await message.answer("❗️Данный бот был розработан специально для сайта http://emassage.name")


@dp.message_handler(state="*")
async def user_is_not_owner(message: types.Message):
    """Handler to send that user is not an owner"""

    await message.answer("😔Ты не владелец данного бота")


@dp.callback_query_handler(lambda query: query.data == "tutorial", state="*")
async def tutorial_callback(query: types.CallbackQuery):
    """Handler for the test confirming button"""

    for index in range(-1,7):
        await bot.delete_message(chat_id=query.message.chat.id,message_id=query.message.message_id+index)
    await query.message.answer(text="😘Молодец!Обучение пройдено!\nА как награду,пуличите интерестный факт!")
    await query.message.answer(text=await random_fact())
    loop = asyncio.get_running_loop()
    loop.create_task(record.start_pooling(bot))
    await query.message.answer(text="☺️Ну,а я,начну отслеживание записей на сиансы!")


@dp.callback_query_handler(lambda query: ( query.data in ["TUTORIALno", "TUTORIALyes"] ), state="*")
async def tutorial_passage(query :types.CallbackQuery):
    """Handler to understand wether user wants to pass a tutorial"""

    if query.data == "TUTORIALyes":
        for index in range(-1,1):
            await bot.delete_message(chat_id=query.message.chat.id,message_id=query.message.message_id+index)
        return await tutorial.send_tutorial(query)

    elif query.data == "TUTORIALno":
        loop = asyncio.get_running_loop()
        loop.create_task(record.start_pooling(bot))
        for index in range(-1,1):
            await bot.delete_message(chat_id=query.message.chat.id,message_id=query.message.message_id+index)

        markup = types.ReplyKeyboardMarkup()
        button1 = types.KeyboardButton(text="Добавить услугу")
        markup.add(button1)

        return await query.message.answer("😔Ну ладно,начну-ко отслеживание записей на сиансы", reply_markup=markup)


@dp.callback_query_handler(lambda query: ( query.data in 
    ["CONFIRMINGno", "CONFIRMINGyes", "NAMEno", "NAMEyes", 
    "DESCRIPTIONno", "DESCRIPTIONyes", "PRICEno", "PRICEyes", 
    "CURRENCYno", "CURRENCYyes", "PHOTOno", "PHOTOyes"]), state="*")
async def callback(query: types.CallbackQuery):
    """Handler for the creating a new service.
    Contains:
    -> CONFIRMING processor
    -> NAME processor
    -> DESCRIPTION processor
    -> PRICE processor
    -> CURRENCY processor
    -> PHOTO processor
    """

    if query.data == "CONFIRMINGno":
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.reset_state()
        await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
        return await query.message.answer("Ну ладно")

    elif query.data == "CONFIRMINGyes":
        new_service[query.from_user.id] = {}
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.NAME)
        await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
        return await query.message.answer("Ок, начнем с названия")


    elif query.data == "NAMEno":
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.NAME)
        await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
        return await query.message.answer("Напишите другое название")

    elif query.data == "NAMEyes":
        new_service[query.from_user.id]["name"] = query.message.text.split("'")[1]
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.DESCRIPTION)
        await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
        return await query.message.answer("Приступим к описанию")

    elif query.data == "DESCRIPTIONno":

        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.DESCRIPTION)
        await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
        return await query.message.answer("Напишите другое описание")

    elif query.data == "DESCRIPTIONyes":
        new_service[query.from_user.id]["description"] = query.message.text.split("'")[1]
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.PRICE)
        await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
        return await query.message.answer("Напишите цену услуги")

    elif query.data == "PRICEno":
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.PRICE)
        await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
        return await query.message.answer("Напишите другую цену")


    elif query.data == "PRICEyes":

        new_service[query.from_user.id]["price"] = query.message.text.split("'")[1]
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.CURRENCY)
        await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
        await query.message.answer("Приступим к валюте")

        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(callback_data="EUR", text="EUR")
        button2 = types.InlineKeyboardButton(callback_data="USD", text="USD")
        button3 = types.InlineKeyboardButton(callback_data="UAH", text="UAH")
        button4 = types.InlineKeyboardButton(callback_data="CHF", text="CHF")
        markup.add(button1, button2, button3, button4)

        return await query.message.answer("Виберете", reply_markup=markup)


    elif query.data == "CURRENCYno":
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.CURRENCY)
        await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
        return await query.message.answer("Поменяйте валюту")

    elif query.data == "CURRENCYyes":
        new_service[query.from_user.id]["currency"] = query.message.text.split("'")[1]
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.PHOTO)
        await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
        return await query.message.answer("Время фотографии для услуги.")

    elif query.data == "PHOTOno":
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.PHOTO)
        await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
        return await query.message.answer("Ок,поменяйте фото")

    elif query.data == "PHOTOyes":
        current_state = dp.current_state(user=query.from_user.id)
        await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
        await service.test_new_service(bot, query,new_service[query.from_user.id])
        await query.message.answer("Проверте данные новой услуги")

        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(callback_data="ADDyes", text="Да")
        button2 = types.InlineKeyboardButton(callback_data="ADDno", text="Нет")
        markup.add(button1, button2)

        await query.message.answer("Все правильно?", reply_markup=markup)


@dp.callback_query_handler(lambda query: (query.data in ["ADDyes", "ADDno"]), state="*")
async def service_add_confiramtion(query: types.CallbackQuery):
    """Handler to understand wether user wants to add a new service"""

    if query.data == "ADDyes":

        await service.create_new_service(bot, query, new_service[query.from_user.id])
        await bot.delete_message(query.message.chat.id, message_id=query.message.message_id)
        await query.message.answer("Поздравляю!Услуга добавлена")

    elif query.data == "ADDno":

        await bot.delete_message(query.message.chat.id, message_id=query.message.message_id)
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(callback_data="REWRITEyes", text="Да")
        button2 = types.InlineKeyboardButton(callback_data="REWRITEno", text="Нет")
        markup.add(button1, button2)

        await query.message.answer("Ок,хотите переделать?", reply_markup=markup)


@dp.callback_query_handler(lambda query: ( query.data in ["REWRITEyes", "REWRITEno"]), state="*")
async def rewrite_confiramation(query: types.CallbackQuery):
    """Handler to understand whether user wants to rewrite his new service or not"""

    if query.data == "REWRITEyes":
    
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.NAME)
        await query.message.answer("Хорошо начнем с начала.А именно с названия")
        

    elif query.data == "REWRITEno":

        current_state = dp.current_state(user=query.from_user.id)
        await current_state.reset_state()
        await query.message.answer("Ну ладно")
    




@dp.callback_query_handler(lambda query: True, state="*")
async def client_confirmation(query: types.CallbackQuery):
    """A callback hander to make the record inactive and done"""

    author_name = await record.utils.update_data_and_get_author(params={"pk": query.data}, json_data={"status": True})
    await bot.edit_message_text(text=f"✅Заказ для {author_name} - выполнен", 
            message_id=query.message.message_id, 
            chat_id=query.message.chat.id)    


if __name__ == "__main__":
    executor.start_polling(dp, timeout=10, skip_updates=True)
