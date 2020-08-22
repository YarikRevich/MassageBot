
class FormattedInfo:

    def __init__(self, json):
        self.json = json


    async def get_customername(self):
        return self.json["author"]
    

    async def get_servicename(self):
        return self.json["name"]


    async def get_description(self):
        return self.json["description"]


    async def get_time(self):
        time = self.json["time"]
        date_splited = time.split("T")
        time_splited = date_splited[1].split(".")
        return date_splited[0] + " " + time_splited[0]


    async def get_phone(self):
        return self.json["phone"]


    @property
    async def get_formatted_data(self):
        return f"❗️❗️❗️Новая запись\n🙋Клиент - {await self.get_customername()}\n💼Название услуги - {await self.get_servicename()}\n📄Дополнение клиента - {await self.get_description()}\n🕐Время записи - {await self.get_time()}\n📱Номер телефона - {await self.get_phone()}\n"
        

