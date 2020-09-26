import os
from RJAPI.contrib import RJAPI


class SourceSetting:
    """Special class for the setting some settings for RJAPI."""

    class Record(RJAPI):
        """Class for the work with records data
        -> Set url
        -> Set auth_data
        """

        class Meta:
            url = os.getenv("URL1")
            auth_data = (os.getenv("USERNAME"), os.getenv("PASS"))


    class Service(RJAPI):
        """Class for the work with service data
        -> Set url
        -> Set auth_data
        """

        class Meta:
            url = os.getenv("URL2")
            auth_data = (os.getenv("USERNAME"), os.getenv("PASS"))


    class DoctorInfo(RJAPI):
        """Class for the work with doctorinfo data
        -> Set url
        -> Set auth_data
        """

        class Meta:
            url = os.getenv("URL3")
            auth_data = (os.getenv("USERNAME"), os.getenv("PASS"))


    class VisitImage(RJAPI):
        """Class for the work with visitimage data
        -> Set url
        -> Set auth_data
        """

        class Meta:
            url = os.getenv("URL4")
            auth_data = (os.getenv("USERNAME"), os.getenv("PASS"))

    record = Record()
    service = Service()
    info = DoctorInfo()
    visitimages = VisitImage()
