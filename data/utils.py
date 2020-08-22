import random
from .source_settings import SourceSetting

class Utils(SourceSetting):
    """Class for the adding some funcionality to the base data with RJAPI"""

    async def get_random_id(self) -> str:
        """Creates a random id for the photo
        and checks whether there is a photo
        with such id and if it does it makes
        random id again 
        """

        nums = ["1", "2", "3", "4", "5", "6", "7"]
        random.shuffle(nums)
        rand_id = "".join(nums)
        for entry in self.service.get_data():
            if entry["photo"].split("/")[-1] == rand_id:
                return await self.get_random_id
        return rand_id


    async def update_data_and_get_author(self, params:dict = None, json_data:dict = None) -> str:
        """Updates entry and returns updated data"""

        return self.record.update_data(params=params, json_data=json_data)["author"]
        