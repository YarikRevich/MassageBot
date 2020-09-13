import aiogram
import asyncio
import os
import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.builtin import CommandHelp,IDFilter
from data.contrib import Record, Service, DoctorInfo, VisitImage, utils
from tutorial.tutorial import Tutorial
from tutorial.quiz import random_fact
from massagebot_components.states import AddService, AddChangeInfo, ChangeVisitImage, AddVisitImage
from massagebot_components.validators import TypeValidator
from massagebot_components.keyboards import create_yesno_keyboard, create_reply_keyboard
from massagebot_components.bot_settings import bot, dp
from massagebot_components.decorators import freeze_check
from aiogram.utils.exceptions import MessageToDeleteNotFound


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
visit_image_to_delete = {}

#------------------

@dp.message_handler(IDFilter(user_id=os.getenv("USER_ID")), state="*", commands=["start"])
async def start_func(message: types.Message):
    """Handler for the /start command to start a relationship between user and bot"""    

    await message.answer("😜Hello!Вас приветствует бот сделаный для администрирования сайта http://emassage.com\nЗдесь Вы можете:\n- Просматривать актуальные записи клиентов\n- Добавлять новые услуги\n- Мониторить статистику\n❗️Бот находится в розработке,его функционал будет расширяться")
    await message.answer(
        "🥺Хотите пройти обучение?",
        reply_markup=await create_yesno_keyboard(["TUTORIALyes", "TUTORIALno"], ["Да", "Нет"]))



@dp.message_handler(lambda message: message.text == "Добавить услугу",state="*")
@freeze_check
async def start_adding_service(message: types.Message):
    """A handler to start an adding of a new service""" 

    current_state = dp.current_state(user=message.from_user.id)
    await current_state.set_state(AddService.CONFIRMING)
    
    await message.answer(
        "🛎Вы в разделе добавления услуги. Ви хотите продолжить?", 
        reply_markup=await create_yesno_keyboard(["CONFIRMING/yes", "CONFIRMING/no"], ["✅Да", "❌Нет"]))


@dp.message_handler(lambda message: (message.text == "Изменить информацию про себя"), state="*")
@freeze_check
async def start_editing_info_about_me(message: types.Message):

    if text_about := await info.get_about_text():
        await bot.send_message(message.chat.id, "Ваше описание👇")
        await bot.send_message(message.chat.id, text_about)

        return await bot.send_message(
            message.chat.id, "🔨Хотите изменить его?", 
            reply_markup=await create_yesno_keyboard(["CHANGEyes", "CHANGEno"], ["✅Да", "❌Нет"]))

    await bot.send_message(message.chat.id, "❌Ваше описание не заполнено")
    await bot.send_message(
        message.chat.id, "✏️Хотите добавить его?", 
        reply_markup=await create_yesno_keyboard(["ADDABOUTyes", "ADDABOUTno"], ["✅Да", "❌Нет"]))


@dp.message_handler(lambda message: (message.text == "Изменить изображения на начальной странице"), state="*")
@freeze_check
async def start_editing_visit_images(message: types.Message):

    if visit_images := await visitimages.get_visit_images():

        current_state = dp.current_state(user=message.from_user.id)
        await current_state.set_state(ChangeVisitImage.EDIT_IMAGE)
        for index, image in enumerate(visit_images):
            await message.answer("🖼Изображение №%d" % (index + 1)) 
            await bot.send_photo(
                    message.chat.id, 
                    image[1], 
                    reply_markup=await create_yesno_keyboard(["edit_%s" % (image[0], ), "delete_%s" % (image[0], )], ["✅Редактировать", "❌Удалить"]))
        return await message.answer(
            "🤔Может Вы хотите добавить новое изображение?", 
            reply_markup = await create_yesno_keyboard(["NEWVISITIMAGE"], ["✅Добавить новое изображение"]))
    await message.answer("😢Пока что нет никаких изображений")
    await message.answer(
        "🖼Может Вы хотите добавить новое изображение?", 
        reply_markup = await create_yesno_keyboard(["NEWVISITIMAGE"], ["✅Добавить новое изображение"]))
    

@dp.callback_query_handler(lambda query: query.data == "NEWVISITIMAGE", state="*")
@freeze_check
async def start_adding_new_visit_image(query: types.InlineQuery):

    try:
        all_message_number = len(await visitimages.get_visit_images()) * 2 + 1
    except TypeError:
        all_message_number = 1
    for index in range(-all_message_number, 1):
        await bot.delete_message(query.message.chat.id, message_id=query.message.message_id + index)
    current_state = dp.current_state(user=query.from_user.id)
    await current_state.set_state(AddVisitImage.ADD_IMAGE)
    await query.message.answer("🤲Отошлите изображение")


@dp.message_handler(content_types=["photo"], state = AddVisitImage.ADD_IMAGE)
@freeze_check
async def add_new_visit_image(photo: types.InputMedia):

    image = await photo["photo"][1].get_file()
    new_visit_image[photo.from_user.id] = {}
    new_visit_image[photo.from_user.id]["photo_path"] = image.file_path
    new_visit_image[photo.from_user.id]["photo"] = await bot.download_file(image.file_path)
    photo_to_send = await bot.download_file(image.file_path)
    await bot.send_photo(photo.chat.id, photo=photo_to_send.read())
    await photo.answer(
        "🤔Вам подходить?", 
        reply_markup = await create_yesno_keyboard(["NEWVISITIMAGEAGREE", "NEWVISITIMAGEDISAGREE"], ["✅Да", "❌Нет"]))


@dp.callback_query_handler(lambda query: (query.data in ["NEWVISITIMAGEAGREE", "NEWVISITIMAGEDISAGREE"]), state=AddVisitImage.ADD_IMAGE)
@freeze_check
async def agreement_width_new_visit_image(query: types.InlineQuery):

    current_state = dp.current_state(user=query.from_user.id)
    if query.data == "NEWVISITIMAGEAGREE":

        for index in range(-1, 1):
            await bot.delete_message(query.message.chat.id, query.message.message_id + index)
        await current_state.reset_state()
        await visitimages.add_new_visit_image(
            new_visit_image[query.from_user.id]["photo_path"], 
            new_visit_image[query.from_user.id]["photo"])
        return await query.message.answer("😄Поздравляю! Изображение добавлено")

    await current_state.set_state(AddVisitImage.ADD_IMAGE)
    await query.message.answer("🤲Отошлите изображение")


@dp.callback_query_handler(lambda query: (query.data in ["CHANGEyes", "CHANGEno"]), state="*")
@freeze_check
async def change_about_text(query: types.InlineQuery):

    if query.data == "CHANGEyes":
        for index in range(-1,1):
            await bot.delete_message(query.message.chat.id, message_id=query.message.message_id + index)
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddChangeInfo.INFO)
        await query.message.answer("🤲Введите новую информацию")
    else:
        for index in range(-1,1):
            await bot.delete_message(query.message.chat.id, message_id=query.message.message_id + index)
        await query.message.answer("😔Ок")


@dp.callback_query_handler(lambda query: (query.data in ["ADDABOUTyes", "ADDABOUTno"]), state="*")
@freeze_check
async def change_about_text(query: types.InlineQuery):

    if query.data == "ADDABOUTyes":
        for index in range(-1,1):
            await bot.delete_message(query.message.chat.id, message_id=query.message.message_id + index)
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddChangeInfo.INFO)
        await query.message.answer("🤲Введите информацию")
    else:
        for index in range(-1,1):
            await bot.delete_message(query.message.chat.id, message_id=query.message.message_id + index)
        await query.message.answer("😔Ок")


@dp.message_handler(state=AddChangeInfo.INFO)
@freeze_check
async def set_new_text(message: types.Message):
    
    if message.text:
        await message.answer(message.text)

        new_info[message.from_user.id] = {"about_text": message.text}
        current_state = dp.current_state(user=message.from_user.id)
        await current_state.set_state(AddChangeInfo.CONFIRMING)

        return await message.answer(
            "🤔Вам все нравиться?", 
            reply_markup=await create_yesno_keyboard(["CHANGEINFOyes", "CHANGEINFOno"], ["✅Да", "❌Нет"]))
    await message.answer("😦Вы ничего не ввели")


@dp.callback_query_handler(lambda query: (query.data in ["CHANGEINFOyes", "CHANGEDINFOno"]),state=AddChangeInfo.CONFIRMING)
@freeze_check
async def agree_with_changed_text(query: types.InlineQuery):
    
    if query.data == "CHANGEINFOyes":
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddChangeInfo.AGGRE_WITH_START_ADD_DE_VERSION)

        await query.message.answer(
            "🇩🇪Хотите добавить версию на немецком язике?", 
            reply_markup=await create_yesno_keyboard(["ADDDEVERSIONyes", "ADDDEVERSIONno"], ["✅Да", "❌Нет"]))
    else:
        del new_info[query.from_user.id]

        await query.message.answer(
            "🤔Желаете изменить информацию?",
            reply_markup=await create_yesno_keyboard(["AGREEWITHCHANGEyes", "AGREEWITHCHANGEno"], ["✅Да", "❌Нет"]))


@dp.callback_query_handler(lambda query: (query.data in ["ADDDEVERSIONyes", "ADDDEVERSIONno"]), state=AddChangeInfo.AGGRE_WITH_START_ADD_DE_VERSION)
@freeze_check
async def add_de_version(query: types.InlineQuery):

    current_state = dp.current_state(user=query.from_user.id)
    if query.data == "ADDDEVERSIONyes":
        await current_state.set_state(AddChangeInfo.ADD_DE_VERSION)
        await query.message.answer("🤲Введите информацию")
    else:
        await info.set_about_text(new_info[query.from_user.id])
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.reset_state()
        del new_info[query.from_user.id]
        await query.message.answer("🥳Ок.Поздравляю информация добавлена!")


@dp.message_handler(state=AddChangeInfo.ADD_DE_VERSION)
@freeze_check
async def confirm_adding_de_version(message: types.Message):

    if message.text:
        new_info[message.from_user.id]["about_text_de"] = message.text
        await message.answer(message.text)
        current_state = dp.current_state(user=message.from_user.id)
        await current_state.set_state(AddChangeInfo.ADD_DE_VERSION_CONFIRMING)    
        return await message.answer(
            "🤔Вам все нравиться?", 
            reply_markup=await create_yesno_keyboard(["AGREEWITHDEyes", "AGREEWITHDEno"], ["✅Да", "❌Нет"]))
    await message.answer("😤Информация не может быть пустой")


@dp.callback_query_handler(lambda query: (query.data in ["AGREEWITHDEyes", "AGREEWITHDEno"]), state = AddChangeInfo.ADD_DE_VERSION_CONFIRMING)
@freeze_check
async def confirming_de_version(query: types.InlineQuery):

    if query.data == "AGREEWITHDEyes":
        await info.set_about_text(new_info[query.from_user.id])
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.reset_state()
        del new_info[query.from_user.id]
        await query.message.answer("👌Поздравляю! Информация добавлена")
    else:
        await query.message.answer(
            "🤔Желаете переделать?",
            reply_markup=await create_yesno_keyboard(["WANNACHANGEyes", "WANNACHANGEno"], ["✅Да", "❌Нет"]))


@dp.callback_query_handler(lambda query: (query.data in ["WANNACHANGEyes", "WANNACHANGEno"]), state="*")
@freeze_check
async def wanna_change_de_version(query: types.InlineQuery):

    if query.data == "WANNACHANGEyes":
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddChangeInfo.ADD_DE_VERSION)
        await query.message.answer("🤲Введите информацию?")
    else:
        del new_info[query.from_user.id]["about_text_de"]
        await info.set_about_text(bot, query, new_info[query.from_user.id])
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.reset_state()
        await query.message.answer("😭Ок, перевод не добавлен")


@dp.callback_query_handler(lambda query: (query.data in ["AGREEWITHCHANGEyes", "AGREEWITHCHANGEno"]), state="*")
@freeze_check
async def change_filled_text(query: types.InlineQuery):

    if query.data == "AGREEWITHCHANGEyes":
        await query.message.answer("😊Введите другую информацию")
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddChangeInfo.INFO)
    else:
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.reset_state()
        await query.message.answer("😭Информация не была применена")


@dp.message_handler(state=AddService.NAME)
@freeze_check
async def add_name_to_service(message: types.Message):
    """Handler to process the adding of a name to a new service"""

    await message.answer(
        "🤔Вы хотите создать услугу с названием '%s'.Вы уверены?" % (message.text), 
        reply_markup=await create_yesno_keyboard(["NAME/yes", "NAME/no"], ["✅Да,хочу продолжить", "❌Нет,хочу поменять"])) 


@dp.message_handler(state=AddService.NAME_DE)
@freeze_check
async def add_name_to_service(message: types.Message):
    """Handler to process the adding of a name to a new service"""

    await message.answer(
        "🇩🇪Вы хотите создать услугу с названием на немецком '%s'.Вы уверены?" % (message.text), 
        reply_markup=await create_yesno_keyboard(["NAME_DE_/yes", "NAME_DE_/no"], ["✅Да,хочу продолжить", "❌Нет,хочу поменять"])) 


@dp.message_handler(state=AddService.DESCRIPTION)
@freeze_check
async def add_description_to_service(message: types.Message):
    """Handler to process the adding of a description to a new service"""

    await message.answer(
        "🤔Вы написали '%s'.Вы уверены?" % (message.text), 
        reply_markup=await create_yesno_keyboard(["DESCRIPTION/yes", "DESCRIPTION/no"], ["✅Да,хочу продолжить", "❌Нет,хочу поменять"])) 


@dp.message_handler(state=AddService.DESCRIPTION_DE)
@freeze_check
async def add_description_to_service(message: types.Message):
    """Handler to process the adding of a description to a new service"""

    await message.answer(
        "🇩🇪Вы написали такое описание на немецком '%s'.Вы уверены?" % (message.text), 
        reply_markup=await create_yesno_keyboard(["DESCRIPTION_DE_/yes", "DESCRIPTION_DE_/no"], ["✅Да,хочу продолжить", "❌Нет,хочу поменять"])) 


@dp.message_handler(state=AddService.PRICE)
@freeze_check
async def add_price_to_service(message: types.Message):
    """Handler to process the adding of a price to a new service"""

    if await TypeValidator.is_digit(message.text):
        return await message.answer(
            "😎Цена новосозданного услуги '%s'.Продолжим?" % (message.text), 
            reply_markup=await create_yesno_keyboard(["PRICE/yes", "PRICE/no"], ["✅Да,хочу продолжить", "❌Нет,хочу поменять"])) 
    await message.answer("👿Цена не может быть текстом! Напишите правильно!")


@dp.callback_query_handler(lambda query: (query.data in ["EUR", "USD", "UAH", "CHF"]), state="*")
@freeze_check
async def add_currency_to_service(query: types.CallbackQuery):
    """Handler to process the adding of a currency to a new service"""

    new_service[query.from_user.id]["currency"] = query.data
    await bot.delete_message(query.message.chat.id, message_id=query.message.message_id)
    current_state = dp.current_state(user=query.from_user.id)
    await current_state.set_state(AddService.CURRENCY)
    return await query.message.answer(
        "Валюта для новой услуги - '%s'.Правильно?💰" % (query.data), 
        reply_markup=await create_yesno_keyboard(["CURRENCY/yes", "CURRENCY/no"], ["✅Да,хочу продолжить", "❌Нет,хочу поменять"])) 


@dp.message_handler(state=AddService.PHOTO, content_types=["photo"])
@freeze_check
async def add_image_to_service(file :types.InputMediaPhoto):
    """Handler to process the adding of a photo to a new service"""

    photo = await file["photo"][1].get_file()
    photo_to_send = await bot.download_file(photo.file_path)
    await bot.send_photo(file.chat.id, photo=photo_to_send.read())
    new_service[file.from_user.id]["photo"] = photo

    await bot.send_message(
        file.chat.id, 
        text="🤔Точно?", 
        reply_markup=await create_yesno_keyboard(["PHOTO/yes", "PHOTO/no"], ["✅Да", "❌Нет"]))


@dp.message_handler(state=AddService.PHOTO)
@freeze_check
async def image_getter(message :types.Message):
    """Handler to notificate user that he needs to a photo not a text"""

    await message.answer(text="😤Текст - не фото!")


@dp.message_handler(CommandHelp(),IDFilter(user_id=os.getenv("USER_ID")),state="*")
@freeze_check
async def help_command(message :types.Message):
    """Sends some information about this bot"""

    await message.answer("❗️Данный бот был розработан специально для сайта http://emassage.name")


@dp.callback_query_handler(lambda query: query.data == "tutorial", state="*")
@freeze_check
async def tutorial_callback(query: types.CallbackQuery):
    """Handler for the test confirming button"""

    for index in range(-1,7):
        await bot.delete_message(chat_id=query.message.chat.id,message_id=query.message.message_id+index)
    await query.message.answer(text="😘Молодец!Обучение пройдено!\nА как награду,пуличите интерестный факт!")
    await query.message.answer(text=await random_fact())
    if await utils.test_request():
        loop = asyncio.get_running_loop()
        loop.create_task(record.start_pooling())
        return await query.message.answer(text="☺️Ну,а я,начну отслеживание записей на сиансы!")  
    return await utils.connection_revise()


@dp.callback_query_handler(lambda query: ( query.data in ["TUTORIALno", "TUTORIALyes"] ), state="*")
@freeze_check
async def tutorial_passage(query :types.CallbackQuery):
    """Handler to understand wether user wants to pass a tutorial"""

    if query.data == "TUTORIALyes":
        for index in range(-1,1):
            await bot.delete_message(chat_id=query.message.chat.id,message_id=query.message.message_id+index)
        await tutorial.send_tutorial(query)
    else:
        if await utils.test_request():
            loop = asyncio.get_running_loop()
            loop.create_task(record.start_pooling())
            for index in range(-1,1):
                await bot.delete_message(chat_id=query.message.chat.id,message_id=query.message.message_id+index)
            return await query.message.answer(
                "😔Ну ладно,начну-ко отслеживание записей на сиансы", 
                reply_markup=await create_reply_keyboard(["Добавить услугу", "Изменить информацию про себя", "Изменить изображения на начальной странице"]))
        return await utils.connection_revise()


@dp.callback_query_handler(lambda query: ( query.data in 
    ["CONFIRMING/no", "CONFIRMING/yes", "NAME/no", "NAME/yes",
    "NAME_DE_/no", "NAME_DE_/yes", "DESCRIPTION/no", "DESCRIPTION/yes",
    "DESCRIPTION_DE_/no", "DESCRIPTION_DE_/yes", "PRICE/no", "PRICE/yes",
    "CURRENCY/no", "CURRENCY/yes", "PHOTO/no", "PHOTO/yes"]), state="*")
@freeze_check
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
        await query.message.answer("📋Ок, начнем с названия")
    elif query.data == "CONFIRMING/no":
        await current_state.reset_state()
        await query.message.answer("😒Ну ладно")
    else:
        if query.data.split("/")[0][-1] == "_" and query.data.split("/")[1] == "yes":
            new_service[query.from_user.id]["%s" % (query.data.split("/")[0][:-1].lower())] = query.message.text.split("'")[1]

        if query.data.split("/")[1] == "yes" and query.data.split("/")[0] != "PHOTO":
            new_service[query.from_user.id]["%s" % (query.data.split("/")[0].lower())] = query.message.text.split("'")[1]

        if query.data == "NAME/no":
            await current_state.set_state(AddService.NAME)
            await query.message.answer("🖌Напишите другое название")

        elif query.data == "NAME/yes":
            await current_state.set_state(AddService.NAME_DE)
            await query.message.answer("🇩🇪Приступим к названию на немецком")

        elif query.data == "NAME_DE_/no":
            await current_state.set_state(AddService.NAME_DE)
            await query.message.answer("🖌Напишите другое название")

        elif query.data == "NAME_DE_/yes":
            await current_state.set_state(AddService.DESCRIPTION)
            await query.message.answer("📄Приступим к описанию")

        elif query.data == "DESCRIPTION/no":
            await current_state.set_state(AddService.DESCRIPTION)
            await query.message.answer("🖌Напишите другое описание")

        elif query.data == "DESCRIPTION/yes":
            await current_state.set_state(AddService.DESCRIPTION_DE)
            await query.message.answer("🇩🇪Напишите описание на немецком")

        elif query.data == "DESCRIPTION_DE_/no":
            await current_state.set_state(AddService.DESCRIPTION_DE)
            await query.message.answer("🖌Напишите другое описание на немецком")

        elif query.data == "DESCRIPTION_DE_/yes":
            await current_state.set_state(AddService.PRICE)
            await query.message.answer("💵Напишите цену услуги")

        elif query.data == "PRICE/no":
            await current_state.set_state(AddService.PRICE)
            await query.message.answer("🖌Напишите другую цену")

        elif query.data == "PRICE/yes":
            await current_state.set_state(AddService.CURRENCY)
            await query.message.answer("💰Приступим к валюте")
            await query.message.answer(
                "Виберете", 
                reply_markup = await create_yesno_keyboard(["EUR", "USD", "UAH", "CHF"], ["EUR", "USD", "UAH", "CHF"]))

        elif query.data == "CURRENCY/no":
            await current_state.set_state(AddService.CURRENCY)
            await query.message.answer("🖌Поменяйте валюту")

        elif query.data == "CURRENCY/yes":
            await current_state.set_state(AddService.PHOTO)
            await query.message.answer("🖼Время фотографии для услуги.")

        elif query.data == "PHOTO/no":
            await current_state.set_state(AddService.PHOTO)
            await query.message.answer("🖌Ок,поменяйте фото")

        elif query.data == "PHOTO/yes":
            
            photo = await bot.download_file(new_service[query.from_user.id]["photo"].file_path)
            await bot.send_photo(query.message.chat.id, photo=photo)
            await bot.send_message(
                query.message.chat.id,
                text="Информация новой услуги\nНазвание: %s\n%sОписание: %s\n%sЦена: %s %s\n" % (
                    new_service[query.from_user.id]["name"],
                    (("Название на немецком: " + new_service[query.from_user.id]["name_de"] + "\n") if new_service[query.from_user.id].get("name_de") else ""),
                    new_service[query.from_user.id]["description"],
                    (("Описание на немецком: " + new_service[query.from_user.id]["description_de"] + "\n") if new_service[query.from_user.id].get("description_de") else ""),
                    new_service[query.from_user.id]["price"],
                    new_service[query.from_user.id]["currency"]
                ))
            await query.message.answer("📝Проверте данные новой услуги")
            await query.message.answer(
                "🤔Все правильно?", 
                reply_markup = await create_yesno_keyboard(["ADDyes", "ADDno"], ["✅Да", "❌Нет"]))

    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)


@dp.callback_query_handler(lambda query: True, state=ChangeVisitImage.EDIT_IMAGE)
@freeze_check
async def edit_visit_image(query: types.InlineQuery):
    
    current_state = dp.current_state(user=query.from_user.id)
    pk_from_query_data = query.data.split("_")[1]

    if query.data.split("_")[0] == "edit":
        new_visit_image[query.from_user.id] = {"pk": pk_from_query_data}
        await current_state.set_state(ChangeVisitImage.EDIT_PROCESS)
        await query.message.answer("🤲Отошлите новое фото")
    else:
        visit_image_to_delete[query.from_user.id] = {"pk": pk_from_query_data}
        await current_state.set_state(ChangeVisitImage.DELETE_PROCESS)
        await query.message.answer(
            "🤔Вы уверены?",
            reply_markup=await create_yesno_keyboard(["DELETEIMAGEyes", "DELETEIMAGEno"], ["✅Да", "❌Нет"]))
        



@dp.message_handler(content_types=["photo"], state=ChangeVisitImage.EDIT_PROCESS)
@freeze_check
async def set_visit_image_process(message: types.InputMedia):
    
    photo_path = await message["photo"][1].get_file()
    photo = await bot.download_file(photo_path.file_path)
    await bot.send_photo(message.chat.id, photo)
    await message.answer(
        "🤔Вам подходить такое изображение?",
        reply_markup=await create_yesno_keyboard(["VISITIMAGEyes", "VISITIMAGEno"], ["✅Да", "❌Нет"]))
    new_visit_image[message.from_user.id]["visitimage"] = await bot.download_file(photo_path.file_path)
    new_visit_image[message.from_user.id]["visitimage_path"] = photo_path.file_path



@dp.callback_query_handler(lambda query:(query.data in ["VISITIMAGEyes", "VISITIMAGEno"]), state=ChangeVisitImage.EDIT_PROCESS)
@freeze_check
async def agree_with_new_visitimage(query: types.InlineQuery):

    try:
        all_message_number = len(await visitimages.get_visit_images()) * 2 + 4
    except TypeError:
        all_message_number = 1
    for index in range(-all_message_number, 1):
        await bot.delete_message(query.message.chat.id, query.message.message_id + index)

    if query.data == "VISITIMAGEyes":
        await visitimages.set_visit_image(new_visit_image[query.from_user.id])
        await query.message.answer("😄Поздравляю! Изображение добавлено")
    else:
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.reset_state()
        await query.message.answer("😞Ок")


@dp.callback_query_handler(lambda query: (query.data in ["DELETEIMAGEyes", "DELETEIMAGEno"]), state=ChangeVisitImage.DELETE_PROCESS)
@freeze_check
async def delete_visit_image(query: types.InlineQuery):
    
    if query.data == "DELETEIMAGEyes":
        try:
            all_message_number = len(await visitimages.get_visit_images()) * 2 + 3
        except TypeError:
            all_message_number = 1
        for index in range(-all_message_number, 1):
            await bot.delete_message(query.message.chat.id, query.message.message_id + index)
        await visitimages.delete_visit_image({"pk":visit_image_to_delete[query.from_user.id]["pk"]})
        return await query.message.answer("🥳Изображение удалено")
    await query.message.answer("😔Oк")


@dp.callback_query_handler(lambda query: (query.data in ["ADDyes", "ADDno"]), state="*")
@freeze_check
async def service_add_confiramtion(query: types.CallbackQuery):
    """Handler to understand wether user wants to add a new service"""

    if query.data == "ADDyes":
        photo = await bot.download_file(new_service[query.from_user.id]["photo"].file_path)
        photo_path = new_service[query.from_user.id]["photo"].file_path
        del new_service[query.from_user.id]["photo"]
        await service.create_new_service(new_service[query.from_user.id], photo, photo_path)
        await bot.delete_message(query.message.chat.id, message_id=query.message.message_id)
        await query.message.answer("🥳Поздравляю!Услуга добавлена")

    elif query.data == "ADDno":
        await bot.delete_message(query.message.chat.id, message_id=query.message.message_id)
        await query.message.answer(
            "😉Ок,хотите переделать?",
            reply_markup=create_yesno_keyboard(["REWRITEyes", "REWRITEno"], ["✅Да", "❌Нет"]))


@dp.callback_query_handler(lambda query: (query.data in ["REWRITEyes", "REWRITEno"]), state="*")
@freeze_check
async def rewrite_confiramation(query: types.CallbackQuery):
    """Handler to understand whether user wants to rewrite his new service or not"""

    if query.data == "REWRITEyes":
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.set_state(AddService.NAME)
        await query.message.answer("👌Хорошо начнем с начала.А именно с названия")
        
    else:
        current_state = dp.current_state(user=query.from_user.id)
        await current_state.reset_state()
        await query.message.answer("😒Ну ладно")
    

@dp.callback_query_handler(lambda query: True, state="*")
@freeze_check
async def client_confirmation(query: types.CallbackQuery):
    """A callback hander to make the record inactive and done"""

    author_name = await utils.update_data_and_get_author(params={"pk": query.data}, json_data={"status": True})
    author_name_to_send = author_name if author_name else "Имя не указано"
    await bot.edit_message_text(text=f"✅Заказ для {author_name_to_send} - выполнен", 
            message_id=query.message.message_id, 
            chat_id=query.message.chat.id)    


executor.start_polling(dp, skip_updates=True, timeout=10)
