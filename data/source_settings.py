import os
from RJAPI.contrib import RJAPI


class SourceSetting:
    """
    Special class for the setting some settings
    for the futher work with REST API using RJAPI
    For the work with records data we need to set url
    and auth_data cause' it is available only for AdminUser
    For the work with service data we need to do the same thing
    as we have done with records data,but we need to change url
    with the end as 'service/'
    """

    class Record(RJAPI):
        """Class for the work with records data
        -> Set url
        -> Set auth_data
        """

        class Meta:
            url = "http://localhost:8000/ru/api/records/"
            auth_data = (os.getenv("USERNAME"), os.getenv("PASS"))


    class Service(RJAPI):
        """Class for the work with service data
        -> Set url
        -> Set auth_data
        """

        class Meta:
            url = "http://localhost:8000/ru/api/service/"
            auth_data = (os.getenv("USERNAME"), os.getenv("PASS"))


    class DoctorInfo(RJAPI):
        """Class for the work with doctorinfo data
        -> Set url
        -> Set auth_data
        """

        class Meta:
            url = "http://localhost:8000/ru/api/about/"
            auth_data = (os.getenv("USERNAME"), os.getenv("PASS"))


    class VisitImage(RJAPI):
        """Class for the work with visitimage data
        -> Set url
        -> Set auth_data
        """

        class Meta:
            url = "http://localhost:8000/ru/api/visitimages/"
            auth_data = (os.getenv("USERNAME"), os.getenv("PASS"))

    record = Record()
    service = Service()
    info = DoctorInfo()
    visitimages = VisitImage()
