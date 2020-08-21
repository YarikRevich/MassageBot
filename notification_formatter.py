
class Formatter:

    @property
    def get_customername(self):
        return self.json["author"]

    @property
    def get_servicename(self):
        return self.json["name"]

    @property
    def get_description(self):
        return self.json["description"]

    @property
    def get_time(self):
        time = self.json["time"]
        date_splited = time.split("T")
        time_splited = date_splited[1].split(".")
        return date_splited[0] + " " + time_splited[0]

    @property
    def get_phone(self):
        return self.json["phone"]

class FormattedInfo(Formatter):

    def __new__(cls,*args, **kwargs):
        if not hasattr(cls,"_formatted"):
            cls._formatted = super(FormattedInfo,cls).__new__(cls)
        return cls._formatted


    def __init__(self,json):
        self.json = json

    @property
    def get_info(self):
        return f"❗️❗️❗️Новая запись\n🙋Клиент - {self.get_customername}\n💼Название услуги - {self.get_servicename}\n📄Дополнение клиента - {self.get_description}\n🕐Время записи - {self.get_time}\n📱Номер телефона - {self.get_phone}\n"
        

