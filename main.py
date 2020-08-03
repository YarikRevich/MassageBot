import aiogram
from aiogram import Bot,Dispatcher,executor,types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import os
from states import BotStates
from aiogram.dispatcher.filters.builtin import CommandSettings,Command,Text,HashTag,ContentTypeFilter,IDFilter

TOKEN = os.getenv("TOKEN")
bot = Bot(TOKEN)
dp = Dispatcher(bot,storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(IDFilter(user_id=391091754),state="*",commands=["start"])
async def start_func(message: types.Message):
    markup = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton(text="Изменить картинку бота")
    markup.add(button1)

    current = dp.current_state(user=message.from_user.id)
    await current.set_state(BotStates.START)
    
    await message.answer("Начинаю отслеживание записей на сиансы",reply_markup=markup)


# @dp.message_handler(content_types=["document"],state=BotStates.all()[0])
# async def download_image(file: types.File):
#     file_id = file["document"]["thumb"]["file_id"]
#     image = aiogram.types.chat_photo.ChatPhoto(small_file_id=file_id)
#     with open("image","wb") as fil:
#         await image.download_small(destination=fil)
    
@dp.message_handler(IDFilter(user_id=391091754),state=BotStates.START)
async def test(message: types.Message):
    await message.answer("Hello World!")


@dp.inline_handler(lambda query: (True),state=BotStates.START)
async def test1(query: types.InlineQuery):
    print("Хай")
    await bot.answer_inline_query(query.id,cache_time=1,results=["Hello World!"])

# @dp.inline_handler(lambda query: query.query == "test",state=BotStates.START)
# async def test1(query: types.InlineQuery):
#     print(query)


@dp.message_handler(state="*")
async def user_is_not_owner(message: types.Message):
    await message.answer("Ты не владелец данного бота")


if __name__ == "__main__":
    executor.start_polling(dp,timeout=10,skip_updates=True)
    