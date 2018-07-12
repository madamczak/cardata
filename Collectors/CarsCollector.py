
from OperationUtils.car_verification_utils import CarVerificationUtils

from OperationUtils.url_operations import URLOperations
import datetime
import inspect

from OperationUtils.logger import Logger
moduleLogger = Logger.setLogger("CarsCollector")

class CarsCollector(object):
    def __init__(self, database):
        self.db = database
        self.verificator = CarVerificationUtils()

    def _parseAllegroLink(self, allegroLinkTuple):
        methodName = inspect.stack()[0][3]
        d = URLOperations.parseAllegroSite(allegroLinkTuple[3])

        if self.verificator.verifyDictionary(d):
            moduleLogger.debug("%s - Verified positively. Will be inserted in cars_car table." % methodName)
            self.db.insertAllegroCarToDatabase(allegroLinkTuple[1], allegroLinkTuple[0], d)
            return 1
        else:
            self.db.insertInvalidLinkToDatabase(allegroLinkTuple[0], allegroLinkTuple[3])
            return 0

    def Collect(self, limit=300000):
        methodName = inspect.stack()[0][3]

        newCars = 0
        #todo: this variable seems to be only used in logging - remove it
        currentB_id = ""

        counter = 0
        startTime = datetime.datetime.now()

        for entry in self.db.readAllUnparsedLinks():
            if counter > limit:
                moduleLogger.info("%s - Collected %d cars." % (methodName, limit))
                break
            counter += 1

            if currentB_id != entry[1]:
                currentB_id = entry[1]
                moduleLogger.info("%s - %s - Currently working on links from %s b_id. It has %s l_id" %
                                  (datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), methodName, entry[1], entry[0]))

            if 'allegro' in entry[3]:
                newCars += self._parseAllegroLink(entry)

            elif 'otomoto' in entry[3]:
                newCars += self._parseOtomotoLink(entry)

            self.db.updateParsedParameterForLinkWithId(entry[0])
        return newCars, startTime
