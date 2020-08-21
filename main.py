import aiogram
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import os
import quiz

from aiogram.dispatcher.filters.builtin import CommandHelp,IDFilter
from data import start_pooling, data, send_tutorial

TOKEN = os.getenv("TOKEN")
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(IDFilter(user_id=os.getenv("USER_ID")), state="*", commands=["start"])
async def start_func(message: types.Message):

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(callback_data="yes",text="Да")
    button2 = types.InlineKeyboardButton(callback_data="no",text="Нет")
    markup.add(button1, button2)
    await message.answer("😜Hello!Вас приветствует бот сделаный для администрирования сайта http://emassage.com\nЗдесь Вы можете:\n- Просматривать актуальные записи клиентов\n- Добавлять новые услуги\n- Мониторить статистику\n❗️Бот находится в розработке,его функционал будет расширяться")
    await message.answer("🥺Хотите пройти обучение?",reply_markup=markup)


@dp.callback_query_handler(lambda query: True, state="*")
async def callback(query: types.CallbackQuery):

    if query.data == "yes":
        for index in range(-1,1):
            await bot.delete_message(chat_id=query.message.chat.id,message_id=query.message.message_id+index)
        return await send_tutorial(query)

    elif query.data == "no":
        loop = asyncio.get_running_loop()
        loop.create_task(start_pooling(bot))
        for index in range(-1,1):
            await bot.delete_message(chat_id=query.message.chat.id,message_id=query.message.message_id+index)

        return await query.message.answer("😔Ну ладно,начну-ко отслеживание записей на сиансы")

    elif query.data == "tutorial":
        for index in range(-1,7):
            await bot.delete_message(chat_id=query.message.chat.id,message_id=query.message.message_id+index)
        await query.message.answer(text="😘Молодец!Обучение пройдено!\nА как награду,пуличите интерестный факт!")
        await query.message.answer(text=await quiz.random_fact())
        loop = asyncio.get_running_loop()
        loop.create_task(start_pooling(bot))
        return await query.message.answer(text="☺️Ну,а я,начну отслеживание записей на сиансы!")

    data.update_data({"status": True}, {"pk": query.data})
    author_name = data.get_data(get_params={"pk": query.data})["author"]
    
    await bot.edit_message_text(text=f"✅Заказ для {author_name} - выполнен", 
            message_id=query.message.message_id, 
            chat_id=query.message.chat.id)


@dp.message_handler(CommandHelp(),IDFilter(user_id=os.getenv("USER_ID")),state="*")
async def help_command(message :types.Message):
    await message.answer("❗️Данный бот был розработан специально для сайта http://emassage.name")


@dp.message_handler(state="*")
async def user_is_not_owner(message: types.Message):
    await message.answer("😔Ты не владелец данного бота")


if __name__ == "__main__":
    executor.start_polling(dp, timeout=10, skip_updates=True)
