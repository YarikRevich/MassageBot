import aiogram
import asyncio
import os
import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.builtin import CommandHelp,IDFilter
from data.contrib import Record, Service, DoctorInfo, VisitImage
from tutorial.tutorial import Tutorial
from tutorial.quiz import random_fact
from massagebot_components.states import AddService, AddChangeInfo, ChangeVisitImage
from massagebot_components.validators import TypeValidator
from massagebot_components.keyboards import create_yesno_keyboard, create_reply_keyboard
from massagebot_components.bot_settings import bot, dp


#Important instances of classes for the futher work

record = Record()
service = Service()
info = DoctorInfo()
visitimages = VisitImage()
tutorial = Tutorial()

#A dict for the adding a new service 

new_service = {}
new_info = {}
new_visit_image = {}

#------------------

@dp.message_handler(IDFilter(user_id=os.getenv("USER_ID")), state="*", commands=["start"])
async def start_func(message: types.Message):
    """Handler for the /start command to start a relationship between user and bot"""    

    await message.answer("😜Hello!Вас приветствует бот сделаный для администрирования сайта http://emassage.com\nЗдесь Вы можете:\n- Просматривать актуальные записи клиентов\n- Добавлять новые услуги\n- Мониторить статистику\n❗️Бот находится в розработке,его функционал будет расширяться")
    await message.answer(
        "🥺Хотите пройти обучение?",
        reply_markup=await create_yesno_keyboard(["TUTORIALyes", "TUTORIALno"], ["Да", "Нет"]))


@dp.message_handler(lambda message: message.text == "Добавить услугу",state="*")
async def start_adding_service(message: types.Message):
    """A handler to start an adding of a new service""" 

    current_state = dp.current_state(user=message.from_user.id)
    await current_state.set_state(AddService.CONFIRMING)
    
    await message.answer(
        "Вы в разделе добавления услуги. Ви хотите продолжить?", 
        reply_markup=await create_yesno_keyboard(["CONFIRMING/yes", "CONFIRMING/no"], ["Да", "Нет"]))


@dp.message_handler(lambda message: (message.text == "Изменить информацию про себя"), state="*")
async def start_editing_info_about_me(message: types.Message):
    await info.get_about_text(bot, message)


@dp.message_handler(lambda message: (message.text == "Изменить изображения на начальной странице"))
async def start_editing_visit_images(message: types.Message):
    await visitimages.get_visit_images(bot, message)


@dp.callback_query_handler(lambda query: (query.data in ["CHANGEyes", "CHANGEno"]))
async def change_about_text(query: types.InlineQuery):

    if query.data == "CHANGEyes":
        for index in range(-1,1):
            await bot.delete_message(query.message.chat.id, message_id=query.message.message_id + index)
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddChangeInfo.INFO)
        await query.message.answer("Введите новую информацию")
    else:
        for index in range(-1,1):
            await bot.delete_message(query.message.chat.id, message_id=query.message.message_id + index)
        await query.message.answer("Ок")


@dp.callback_query_handler(lambda query: (query.data in ["ADDABOUTyes", "ADDABOUTno"]))
async def change_about_text(query: types.InlineQuery):

    if query.data == "ADDABOUTyes":
        for index in range(-1,1):
            await bot.delete_message(query.message.chat.id, message_id=query.message.message_id + index)
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddChangeInfo.INFO)
        await query.message.answer("Введите информацию")
    else:
        for index in range(-1,1):
            await bot.delete_message(query.message.chat.id, message_id=query.message.message_id + index)
        await query.message.answer("Ок")


@dp.message_handler(state=AddChangeInfo.INFO)
async def set_new_text(message: types.Message):
    
    if message.text:
        await message.answer(message.text)

        new_info[message.from_user.id] = {"about_text": message.text}
        current_state = dp.current_state(user=message.from_user.id)
        await current_state.set_state(AddChangeInfo.CONFIRMING)

        return await message.answer(
            "Вам все нравиться?", 
            reply_markup=await create_yesno_keyboard(["CHANGEINFOyes", "CHANGEINFOno"], ["Да", "Нет"]))
    await message.answer("Вы ничего не ввели")


@dp.callback_query_handler(lambda query: (query.data in ["CHANGEINFOyes", "CHANGEDINFOno"]),state=AddChangeInfo.CONFIRMING)
async def agree_with_changed_text(query: types.InlineQuery):
    
    if query.data == "CHANGEINFOyes":
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddChangeInfo.AGGRE_WITH_START_ADD_DE_VERSION)

        await query.message.answer(
            "Хотите добавить версию на немецком язике?", 
            reply_markup=await create_yesno_keyboard(["ADDDEVERSIONyes", "ADDDEVERSIONno"], ["Да", "Нет"]))
    else:
        del new_info[query.from_user.id]

        await query.message.answer(
            "Желаете изменить информацию?",
            reply_markup=await create_yesno_keyboard(["AGREEWITHCHANGEyes", "AGREEWITHCHANGEno"], ["Да", "Нет"]))


@dp.callback_query_handler(lambda query: (query.data in ["ADDDEVERSIONyes", "ADDDEVERSIONno"]), state=AddChangeInfo.AGGRE_WITH_START_ADD_DE_VERSION)
async def add_de_version(query: types.InlineQuery):

    current_state = dp.current_state(user=query.from_user.id)
    if query.data == "ADDDEVERSIONyes":
        await current_state.set_state(AddChangeInfo.ADD_DE_VERSION)
        await query.message.answer("Введите информацию")

    else:
        await info.set_about_text(bot, query, new_info[query.from_user.id])
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.reset_state()
        del new_info[query.from_user.id]
        await query.message.answer("Ок.Поздравляю информация добавлена!")


@dp.message_handler(state=AddChangeInfo.ADD_DE_VERSION)
async def confirm_adding_de_version(message: types.Message):

    if message.text:
        new_info[message.from_user.id]["about_text_de"] = message.text
        await message.answer(message.text)
        current_state = dp.current_state(user=message.from_user.id)
        await current_state.set_state(AddChangeInfo.ADD_DE_VERSION_CONFIRMING)    

        return await message.answer(
            "Вам все нравиться?", 
            reply_markup=await create_yesno_keyboard(["AGREEWITHDEyes", "AGREEWITHDEno"], ["Да", "Нет"]))

    await message.answer("Информация не может быть пустой")


@dp.callback_query_handler(lambda query: (query.data in ["AGREEWITHDEyes", "AGREEWITHDEno"]), state = AddChangeInfo.ADD_DE_VERSION_CONFIRMING)
async def confirming_de_version(query: types.InlineQuery):

    if query.data == "AGREEWITHDEyes":
        
        await info.set_about_text(bot, query, new_info[query.from_user.id])
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.reset_state()
        del new_info[query.from_user.id]
        await query.message.answer("Поздравляю! Информация добавлена")
    else:
        await query.message.answer(
            "Желаете переделать?",
            reply_markup=await create_yesno_keyboard(["WANNACHANGEyes", "WANNACHANGEno"], ["Да", "Нет"]))


@dp.callback_query_handler(lambda query: (query.data in ["WANNACHANGEyes", "WANNACHANGEno"]))
async def wanna_change_de_version(query: types.InlineQuery):

    if query.data == "WANNACHANGEyes":
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddChangeInfo.ADD_DE_VERSION)
        await query.message.answer("Введите информацию?")
    else:
        del new_info[query.from_user.id]["about_text_de"]
        await info.set_about_text(bot, query, new_info[query.from_user.id])
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.reset_state()
        await query.message.answer("Ок, перевод не добавлен")


@dp.callback_query_handler(lambda query: (query.data in ["AGREEWITHCHANGEyes", "AGREEWITHCHANGEno"]))
async def change_filled_text(query: types.InlineQuery):
    if query.data == "AGREEWITHCHANGEyes":
        await query.message.answer("Введите другую информацию")
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddChangeInfo.INFO)
    else:
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.reset_state()
        await query.message.answer("Информация не была применена")


@dp.message_handler(state=AddService.NAME)
async def add_name_to_service(message: types.Message):
    """Handler to process the adding of a name to a new service"""

    await message.answer(
        "Вы хотите создать услугу с названием '%s'.Вы уверены?" % (message.text), 
        reply_markup=await create_yesno_keyboard(["NAME/yes", "NAME/no"], ["Да,хочу продолжить", "Нет,хочу поменять"])) 


@dp.message_handler(state=AddService.NAME_DE)
async def add_name_to_service(message: types.Message):
    """Handler to process the adding of a name to a new service"""

    await message.answer(
        "Вы хотите создать услугу с названием на немецком '%s'.Вы уверены?" % (message.text), 
        reply_markup=await create_yesno_keyboard(["NAME_DE_/yes", "NAME_DE_/no"], ["Да,хочу продолжить", "Нет,хочу поменять"])) 


@dp.message_handler(state=AddService.DESCRIPTION)
async def add_description_to_service(message: types.Message):
    """Handler to process the adding of a description to a new service"""

    await message.answer(
        "Вы написали '%s'.Вы уверены?" % (message.text), 
        reply_markup=await create_yesno_keyboard(["DESCRIPTION/yes", "DESCRIPTION/no"], ["Да,хочу продолжить", "Нет,хочу поменять"])) 


@dp.message_handler(state=AddService.DESCRIPTION_DE)
async def add_description_to_service(message: types.Message):
    """Handler to process the adding of a description to a new service"""

    await message.answer(
        "Вы написали такое описание на немецком '%s'.Вы уверены?" % (message.text), 
        reply_markup=await create_yesno_keyboard(["DESCRIPTION_DE_/yes", "DESCRIPTION_DE_/no"], ["Да,хочу продолжить", "Нет,хочу поменять"])) 


@dp.message_handler(state=AddService.PRICE)
async def add_price_to_service(message: types.Message):
    """Handler to process the adding of a price to a new service"""

    if await TypeValidator.is_digit(message.text):
        return await message.answer(
            "Цена новосозданного услуги '%s'.Продолжим?" % (message.text), 
            reply_markup=await create_yesno_keyboard(["PRICE/yes", "PRICE/no"], ["Да,хочу продолжить", "Нет,хочу поменять"])) 
    await message.answer("Цена не может быть текстом! Напишите правильно!")


@dp.callback_query_handler(lambda query: (query.data in ["EUR", "USD", "UAH", "CHF"]), state="*")
async def add_currency_to_service(query: types.CallbackQuery):
    """Handler to process the adding of a currency to a new service"""

    new_service[query.from_user.id]["currency"] = query.data
    await bot.delete_message(query.message.chat.id, message_id=query.message.message_id)
    current_state = dp.current_state(user=query.from_user.id)
    await current_state.set_state(AddService.CURRENCY)
        
    return await query.message.answer(
        "Валюта для новой услуги - '%s'.Правильно?" % (query.data), 
        reply_markup=await create_yesno_keyboard(["CURRENCY/yes", "CURRENCY/no"], ["Да,хочу продолжить", "Нет,хочу поменять"])) 


@dp.message_handler(state=AddService.PHOTO, content_types=["photo"])
async def add_image_to_service(file :types.InputMediaPhoto):
    """Handler to process the adding of a photo to a new service"""

    photo = await file["photo"][0].get_file()
    photo_to_send = await bot.download_file(photo.file_path)
    await bot.send_photo(file.chat.id, photo=photo_to_send.read())
    new_service[file.from_user.id]["photo"] = photo

    await bot.send_message(
        file.chat.id, 
        text="Точно?", 
        reply_markup=await create_yesno_keyboard(["PHOTO/yes", "PHOTO/no"], ["Да", "Нет"]))


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
        await tutorial.send_tutorial(query)
    else:
        loop = asyncio.get_running_loop()
        loop.create_task(record.start_pooling(bot))
        for index in range(-1,1):
            await bot.delete_message(chat_id=query.message.chat.id,message_id=query.message.message_id+index)
        await query.message.answer(
            "😔Ну ладно,начну-ко отслеживание записей на сиансы", 
            reply_markup=await create_reply_keyboard(["Добавить услугу", "Изменить информацию про себя", "Изменить изображения на начальной странице"]))


@dp.callback_query_handler(lambda query: ( query.data in 
    ["CONFIRMING/no", "CONFIRMING/yes", "NAME/no", "NAME/yes",
    "NAME_DE_/no", "NAME_DE_/yes", "DESCRIPTION/no", "DESCRIPTION/yes",
    "DESCRIPTION_DE_/no", "DESCRIPTION_DE_/yes", "PRICE/no", "PRICE/yes",
    "CURRENCY/no", "CURRENCY/yes", "PHOTO/no", "PHOTO/yes"]), state="*")
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

    current_state = dp.current_state(user=query.from_user.id)
    if query.data == "CONFIRMING/yes":
        new_service[query.from_user.id] = {}
        await current_state.set_state(AddService.NAME)
        await query.message.answer("Ок, начнем с названия")
    elif query.data == "CONFIRMING/no":
        await current_state.reset_state()
        await query.message.answer("Ну ладно")
    else:
        if query.data.split("/")[0][-1] == "_" and query.data.split("/")[1] == "yes":
            new_service[query.from_user.id]["%s" % (query.data[:-1].lower())] = query.message.text.split("'")[1]

        if query.data.split("/")[1] == "yes":
            new_service[query.from_user.id]["%s" % (query.data.split("/")[0].lower())] = query.message.text.split("'")[1]

        if query.data == "NAME/no":
            await current_state.set_state(AddService.NAME)
            await query.message.answer("Напишите другое название")

        elif query.data == "NAME/yes":
            await current_state.set_state(AddService.NAME_DE)
            await query.message.answer("Приступим к названию на немецком")

        elif query.data == "NAME_DE_/no":
            await current_state.set_state(AddService.NAME_DE)
            await query.message.answer("Напишите другое название")

        elif query.data == "NAME_DE_/yes":
            await current_state.set_state(AddService.DESCRIPTION)
            await query.message.answer("Приступим к описанию")

        elif query.data == "DESCRIPTION/no":
            await current_state.set_state(AddService.DESCRIPTION)
            await query.message.answer("Напишите другое описание")

        elif query.data == "DESCRIPTION/yes":
            await current_state.set_state(AddService.DESCRIPTION_DE)
            await query.message.answer("Напишите описание на немецком")

        elif query.data == "DESCRIPTION_DE_/no":
            await current_state.set_state(AddService.DESCRIPTION_DE)
            await query.message.answer("Напишите другое описание на немецком")

        elif query.data == "DESCRIPTION_DE_/yes":
            await current_state.set_state(AddService.PRICE)
            await query.message.answer("Напишите цену услуги")

        elif query.data == "PRICE/no":
            await current_state.set_state(AddService.PRICE)
            await query.message.answer("Напишите другую цену")

        elif query.data == "PRICE/yes":
            await current_state.set_state(AddService.CURRENCY)
            await query.message.answer("Приступим к валюте")
            await query.message.answer(
                "Виберете", 
                reply_markup=create_yesno_keyboard(["EUR", "USD", "UAH", "CHF"], ["EUR", "USD", "UAH", "CHF"]))

        elif query.data == "CURRENCY/no":
            await current_state.set_state(AddService.CURRENCY)
            await query.message.answer("Поменяйте валюту")

        elif query.data == "CURRENCY/yes":
            await current_state.set_state(AddService.PHOTO)
            await query.message.answer("Время фотографии для услуги.")

        elif query.data == "PHOTO/no":
            await current_state.set_state(AddService.PHOTO)
            await query.message.answer("Ок,поменяйте фото")

        elif query.data == "PHOTO/yes":
            await service.test_new_service(bot, query,new_service[query.from_user.id])
            await query.message.answer("Проверте данные новой услуги")
            await query.message.answer(
                "Все правильно?", 
                reply_markup=create_yesno_keyboard(["ADDyes", "ADDno"], ["Да", "Нет"]))

    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)


@dp.callback_query_handler(lambda query: True, state=ChangeVisitImage.EDIT_IMAGE)
async def edit_visit_image(query: types.InlineQuery):
    
    new_visit_image[query.from_user.id] = {"pk": query.data}
    current_state = dp.current_state(user=query.from_user.id)
    await current_state.set_state(ChangeVisitImage.EDIT_PROCESS)
    await query.message.answer("Отошлите новое фото")


@dp.message_handler(content_types=["photo"], state=ChangeVisitImage.EDIT_PROCESS)
async def set_visit_image_process(message: types.InputMedia):
    
    photo_path = await message["photo"][0].get_file()
    photo = await bot.download_file(photo_path.file_path)
    await bot.send_photo(message.chat.id, photo)
    await message.answer(
        "Вам подходить такое изображение?",
        reply_markup=await create_yesno_keyboard(["VISITIMAGEyes", "VISITIMAGEno"], ["Да", "Нет"]))
    new_visit_image[message.from_user.id]["visitimage"] = photo_path


@dp.callback_query_handler(lambda query:(query.data in ["VISITIMAGEyes", "VISITIMAGEno"]), state=ChangeVisitImage.EDIT_PROCESS)
async def agree_with_new_visitimage(query: types.InlineQuery):

    if query.data == "VISITIMAGEyes":
        await visitimages.set_visit_image(bot, query, new_visit_image)
        await query.message.answer("Поздравляю! Изображение добавлено")
    else:
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.reset_state()
        await query.message.answer("Ок")


@dp.callback_query_handler(lambda query: (query.data in ["ADDyes", "ADDno"]), state="*")
async def service_add_confiramtion(query: types.CallbackQuery):
    """Handler to understand wether user wants to add a new service"""

    if query.data == "ADDyes":
        await service.create_new_service(bot, query, new_service[query.from_user.id])
        await bot.delete_message(query.message.chat.id, message_id=query.message.message_id)
        await query.message.answer("Поздравляю!Услуга добавлена")

    elif query.data == "ADDno":
        await bot.delete_message(query.message.chat.id, message_id=query.message.message_id)
        await query.message.answer(
            "Ок,хотите переделать?",
            reply_markup=create_yesno_keyboard(["REWRITEyes", "REWRITEno"], ["Да", "Нет"]))


@dp.callback_query_handler(lambda query: (query.data in ["REWRITEyes", "REWRITEno"]), state="*")
async def rewrite_confiramation(query: types.CallbackQuery):
    """Handler to understand whether user wants to rewrite his new service or not"""

    if query.data == "REWRITEyes":
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.NAME)
        await query.message.answer("Хорошо начнем с начала.А именно с названия")
        
    else:
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


executor.start_polling(dp, skip_updates=True, timeout=10)
