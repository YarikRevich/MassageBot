from aiogram import types
from data.notification_formatter import FormattedInfo


class Tutorial:
    """Class for the work with tutorial.
    Here, it creates all the importnant 
    messages to teach user
    """

    @property
    async def get_test_record(self) -> str:
        """Creates a test record"""

        test_data = {
            "author":"Василий",
            "name":"Массаж спины",
            "description":"Прошу массаж помягче",
            "time":"2020-08-18T11:52:44.236541+03:00",
            "phone":"0632260575",
        }
        formatter = FormattedInfo(test_data)
        return await formatter.get_formatted_data

    @property
    async def get_tutorial_description_message(self) -> str:
        """Creates a description of the tutorial"""

        return "🤗 Приветсвую Вас в обучении!\nНиже Вы видете тестовую запись клиента на сеанс,изучите её!"

    @property
    async def get_record_user_name_review(self) -> str:
        """Returns a review of client's name gotten from test record"""

        return "1️⃣ На первой строке Вы видете Имя клиента сделавшего запись(Тут,думаю,ничего сложного нет)"

    @property
    async def get_record_service_name(self) -> str:
        """Returns a review of service name gotten from test record"""

        return "2️⃣ На второй строчке Вы видете название услуги,которую выбрал клиент"

    @property
    async def record_description_review(self) -> str:
        """Returns a review of client's description of taken service gotten from test record"""

        return "3️⃣ На третей строке Вы виделет описание которое сделал клиент для того что бы уведомить Вас о чем-то нетриввиальном"

    @property
    async def record_time_review(self) -> str:
        """Returns a review of record made time gotten from test record"""

        return "4️⃣ На четвертой строчке Вы видете время,когда клиент сделал запись"

    @property
    async def record_phone_review(self) -> str:
        """Returns a review of client's phone number gotten from test record"""

        return "5️⃣ Ну и на последней строке Вы можете наблюдать номер телефона клиента с помощью которого Вы можете коммуницировать с ним"

    @property
    async def answer_review(self) -> str:
        """Returns a review of the confirming button under the test record"""

        return "✅ Под тестовой записью Вы можете увидеть кнопку.Нажав на неё Вы укажете,что данный заказ был выполнен\nНу,а сейчас,для теста,нажмите на кнопку и Вы увидете сюрприз!"


    async def send_tutorial(self, query: types.InlineQuery) -> str:
        """Gets all the important data and sends messages to user"""

        all_messages = [
            await self.get_tutorial_description_message,
            await self.get_test_record,
            await self.get_record_user_name_review,
            await self.get_record_service_name,
            await self.record_description_review,
            await self.record_time_review,
            await self.record_phone_review,
            await self.answer_review
        ]
    
        for message in all_messages:
            if message == await self.get_test_record:
                markup = types.InlineKeyboardMarkup()
                button1 = types.InlineKeyboardButton("Указать как выполненый!",callback_data="tutorial")
                markup.add(button1)
                await query.message.answer(message, reply_markup=markup)
            else:
                await query.message.answer(message)