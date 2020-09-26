import random
import aiohttp
import os
import asyncio
from .source_settings import SourceSetting
from massagebot_components.bot_settings import bot
from data import contrib
import urllib
from aiohttp.client_exceptions import ClientConnectionError


class Utils(SourceSetting):
	"""Class for the adding some funcionality to the base data with RJAPI"""

	async def get_random_id(self, extansion: str) -> str:
		"""Creates a random id for the photo
		and checks whether there is a photo
		with such id and if it does it makes
		random id again 
		"""

		nums = ["1", "2", "3", "4", "5", "6", "7"]
		random.shuffle(nums)
		rand_id = "".join(nums)

		for entry in await self.service.get_data():
			if entry["photo"].split("/")[-1] == rand_id:
				return await self.get_random_id

		for entry in await self.visitimages.get_data():
			if entry["visit_image"] is not None:
				if entry["visit_image"].split("/")[-1] == rand_id:
					return await self.get_random_id
		return rand_id + ".%s" % (extansion)


	async def update_data_and_get_author(self, params:dict = None, json_data:dict = None) -> str:
		"""Updates entry and returns updated data"""

		data = await self.record.update_data(params=params, json_data=json_data)
		return data["author"]
		

	async def format_url(self, url: str) -> str:
		"""Formats url to get an image for the futher actions"""

		if url is not None:
			splited_url = url.split("/")
			image_file_part = splited_url[-1]
			return f"{os.getenv('URL5')}%s" % (image_file_part) 


	async def convert_link_into_image(self, image_url: str) -> object:
		"""Gets image from url"""

		if image_url is not None:
			image = urllib.request.urlopen(image_url)
			return image


	async def test_request(self):
		"""Checks whether server is alive"""

		async with aiohttp.ClientSession(
			headers={
				"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0"
			}) as session:
			try:
				async with session.get(os.getenv("TEST_URL")) as response:
					if response.status == 200:
						return True
					return False
			except ClientConnectionError:
				return False


	async def connection_revise(self) -> object:
		"""Tries to revise a connection"""

		await bot.send_message(os.getenv("USER_ID"), "❌Соединение с сервером не было установлено. Через 2 минуты будет повторная попытка соединения")
		os.environ["FREEZE"] = "1"
		await asyncio.sleep(120)
		if not await self.test_request():
			await bot.send_message(os.getenv("USER_ID"), "❌Повторная попытка дала сбой. Следуйщая будет через 20 минут")
			os.environ["FREEZE"] = "1"
			await asyncio.sleep(7200)
			if not await self.test_request():
				await bot.send_message(os.getenv("USER_ID"), "❌Повторная попытка дала сбой. Робота бота будет заморожена до восстановление соединения")
				os.environ["FREEZE"] = "1"
				while True:
					if await self.test_request():
						del os.environ["FREEZE"]
						return await bot.send_message(os.getenv("USER_ID"), "✅Соединение восстановлено!")
					await asyncio.sleep(10)
			else:
				del os.environ["FREEZE"]
				await bot.send_message(os.getenv("USER_ID"), "✅Соединение восстановлено!")
		else:
			del os.environ["FREEZE"]
			await bot.send_message(os.getenv("USER_ID"), "✅Соединение восстановлено!")

	
	async def send_freeze_error_message(self) -> object:
		"""Sends a message about a bot freezing until the connection is revised"""

		return await bot.send_message(os.getenv("USER_ID"), "🥶Бот заморожен до восстановления соединения")
