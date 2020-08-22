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


TOKEN = os.getenv("TOKEN")
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

record = Record()
service = Service()

tutorial = Tutorial()
new_service = {}


@dp.message_handler(IDFilter(user_id=os.getenv("USER_ID")), state="*", commands=["start"])
async def start_func(message: types.Message):

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(callback_data="TUTORIALyes",text="Да")
    button2 = types.InlineKeyboardButton(callback_data="TUTORIALno",text="Нет")
    markup.add(button1, button2)
    await message.answer("😜Hello!Вас приветствует бот сделаный для администрирования сайта http://emassage.com\nЗдесь Вы можете:\n- Просматривать актуальные записи клиентов\n- Добавлять новые услуги\n- Мониторить статистику\n❗️Бот находится в розработке,его функционал будет расширяться")
    await message.answer("🥺Хотите пройти обучение?",reply_markup=markup)


@dp.message_handler(lambda message: message.text == "Добавить услугу",state="*")
async def start_adding_service(message: types.Message):

    current_state = dp.current_state(user=message.from_user.id)
    await current_state.set_state(AddService.CONFIRMING)
    
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(callback_data="CONFIRMINGno", text="Нет")
    button2 = types.InlineKeyboardButton(callback_data="CONFIRMINGyes", text="Да")
    markup.add(button1, button2)

    await message.answer("Вы в разделе добавления услуги. Ви хотите продолжить?", reply_markup=markup)


@dp.message_handler(state=AddService.NAME)
async def add_name_service(message: types.Message):

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(callback_data="NAMEno", text="Нет,хочу поменять")
    button2 = types.InlineKeyboardButton(callback_data="NAMEyes", text="Да,хочу продолжить.")
    markup.add(button1, button2)
    await message.answer("Вы хотите создать услугу с названием '%s'.Вы уверены?" % (message.text), reply_markup=markup) 


@dp.message_handler(state=AddService.DESCRIPTION)
async def add_description_service(message: types.Message):

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(callback_data="DESCRIPTIONno", text="Нет,хочу поменять")
    button2 = types.InlineKeyboardButton(callback_data="DESCRIPTIONyes", text="Да,хочу продолжить.")
    markup.add(button1, button2)
    await message.answer("Вы написали '%s'.Вы уверены?" % (message.text), reply_markup=markup) 


@dp.message_handler(state=AddService.PRICE)
async def add_description_service(message: types.Message):

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(callback_data="PRICEno", text="Нет,хочу поменять")
    button2 = types.InlineKeyboardButton(callback_data="PRICEyes", text="Да,хочу продолжить.")
    markup.add(button1, button2)
    await message.answer("Цена новосозданного услуги '%s'.Продолжим?" % (message.text), reply_markup=markup) 


@dp.message_handler(state=AddService.PHOTO, content_types=["photo"])
async def image_getter(file :types.InputMediaPhoto):

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
    await message.answer(text="Текст - не фото!")


@dp.message_handler(CommandHelp(),IDFilter(user_id=os.getenv("USER_ID")),state="*")
async def help_command(message :types.Message):
    await message.answer("❗️Данный бот был розработан специально для сайта http://emassage.name")


@dp.message_handler(state="*")
async def user_is_not_owner(message: types.Message):
    await message.answer("😔Ты не владелец данного бота")


@dp.callback_query_handler(lambda query: (query.data in ["EUR", "USD", "UAH", "CHF"]), state="*")
async def currency_callback(query: types.CallbackQuery):
    
    if query.data == "EUR":

        new_service[query.from_user.id]["currency"] = "EUR"
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.CURRENCY)
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(callback_data="CURRENCYno", text="Нет,хочу поменять")
        button2 = types.InlineKeyboardButton(callback_data="CURRENCYyes", text="Да,хочу продолжить.")
        markup.add(button1, button2)
        
        return await query.message.answer("Валюта для новой услуги - 'EUR'.Правильно?", reply_markup=markup) 


    elif query.data == "USD":

        new_service[query.from_user.id]["currency"] = "USD"
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.CURRENCY)
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(callback_data="CURRENCYno", text="Нет,хочу поменять")
        button2 = types.InlineKeyboardButton(callback_data="CURRENCYyes", text="Да,хочу продолжить.")
        markup.add(button1, button2)
        
        return await query.message.answer("Валюта для новой услуги - 'USD'.Правильно?", reply_markup=markup) 


    elif query.data == "UAH":

        new_service[query.from_user.id]["currency"] = "UAH"
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.CURRENCY)
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(callback_data="CURRENCYno", text="Нет,хочу поменять")
        button2 = types.InlineKeyboardButton(callback_data="CURRENCYyes", text="Да,хочу продолжить.")
        markup.add(button1, button2)
        
        return await query.message.answer("Валюта для новой услуги - 'UAH'.Правильно?", reply_markup=markup) 


    elif query.data == "CHF":

        new_service[query.from_user.id]["currency"] = "CHF"
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.CURRENCY)
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(callback_data="CURRENCYno", text="Нет,хочу поменять")
        button2 = types.InlineKeyboardButton(callback_data="CURRENCYyes", text="Да,хочу продолжить.")
        markup.add(button1, button2)
        
        return await query.message.answer("Валюта для новой услуги - 'CHF'.Правильно?", reply_markup=markup) 


@dp.callback_query_handler(lambda query: query.data == "tutorial", state="*")
async def tutorial_callback(query: types.CallbackQuery):

    for index in range(-1,7):
        await bot.delete_message(chat_id=query.message.chat.id,message_id=query.message.message_id+index)
    await query.message.answer(text="😘Молодец!Обучение пройдено!\nА как награду,пуличите интерестный факт!")
    await query.message.answer(text=await random_fact())
    loop = asyncio.get_running_loop()
    loop.create_task(record.start_pooling(bot))
    await query.message.answer(text="☺️Ну,а я,начну отслеживание записей на сиансы!")


@dp.callback_query_handler(lambda query: ( query.data in ["TUTORIALno", "TUTORIALyes"] ), state="*")
async def tutorial_passage(query :types.CallbackQuery):

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
        await query.message.answer("Хотите добавить?")


@dp.callback_query_handler(lambda query: True, state="*")
async def client_confirmation(query: types.CallbackQuery):

    author_name = await record.utils.update_data_and_get_author(params={"pk": query.data}, json_data={"status": True})
    await bot.edit_message_text(text=f"✅Заказ для {author_name} - выполнен", 
            message_id=query.message.message_id, 
            chat_id=query.message.chat.id)    


if __name__ == "__main__":
    executor.start_polling(dp, timeout=10, skip_updates=True)
