import random
from .source_settings import SourceSetting
import urllib


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

        for entry in self.service.get_data()["results"]:
            if entry["photo"].split("/")[-1] == rand_id:
                return await self.get_random_id

        for entry in self.visitimages.get_data()["results"]:
            if entry["visit_image"].split("/")[-1] == rand_id:
                return await self.get_random_id
        return rand_id + ".%s" % (extansion)


    async def update_data_and_get_author(self, params:dict = None, json_data:dict = None) -> str:
        """Updates entry and returns updated data"""

        return self.record.update_data(params=params, json_data=json_data)["author"]
        

    async def format_url(self, url):
        splited_url = url.split("/")
        image_file_part = splited_url[-1]
        return "http://localhost:8000/static/media/visitimages/%s" % (image_file_part) 


    async def convert_link_into_image(self, image_url):
        image = urllib.request.urlopen(image_url)
        return image