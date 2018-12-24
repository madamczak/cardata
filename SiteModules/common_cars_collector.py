from OperationUtils.car_verification_utils import CarVerificationUtils

class CarsCollector(object):
    def __init__(self, database):
        self.db = database
        self.verificator = CarVerificationUtils()
        self.carsResultDict = {}
        self.validLinksDict = {}
        self.invalidLinksList = []

    def Collect(self):
        raise NotImplementedError("Not implemented")
