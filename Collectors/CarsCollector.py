from OperationUtils.car_verification_utils import CarVerificationUtils
from multiprocessing import cpu_count
from OperationUtils.url_operations import URLOperations
import datetime
import concurrent.futures

from OperationUtils.logger import Logger
moduleLogger = Logger.setLogger("CarsCollector")

class CarsCollector(object):
    def __init__(self, database):
        self.db = database
        self.verificator = CarVerificationUtils()
        #todo: rename result_dict to be more meaningful
        self.result_dict = {}
        self.validLinksDict = {}
        self.invalidLinksList = []

    #todo: verify if there is an easy way to escape passing allegroLinkTuple to the methods below
    def _parseAllegroLink(self, allegroLinkTuple):
        return allegroLinkTuple, URLOperations.parseAllegroSite(allegroLinkTuple[3])

    def sortDictionaries(self, allegroLinkTuple, d):
        if self.verificator.verifyDictionary(d):
            self.validLinksDict[allegroLinkTuple] = d
        else:
            self.invalidLinksList.append(allegroLinkTuple)

    def _insertLinks(self):
        self._insertValidLinks()
        self._insertInvalidLinks()

    def _insertValidLinks(self):
        for invalidLinkTuple in self.invalidLinksList:
            self.db.updateParsedParameterForLinkWithId(invalidLinkTuple[0])
            self.db.insertInvalidLinkToDatabase(invalidLinkTuple[0], invalidLinkTuple[3])

    def _insertInvalidLinks(self):
        for validLinkTuple, carDictionary in self.validLinksDict.items():
            self.db.updateParsedParameterForLinkWithId(validLinkTuple[0])
            self.db.insertAllegroCarToDatabase(validLinkTuple[1], validLinkTuple[0], carDictionary)

    #todo: remove limits as a passed arguments
    def Collect(self, limit=300000):
        startTime = datetime.datetime.now()

        with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count()) as crawler_link_threads:
            future_tasks = {crawler_link_threads.submit(self._parseAllegroLink, link):
                                link for link in self.db.readAllUnparsedLinks()}
            for future in concurrent.futures.as_completed(future_tasks):
                self.result_dict[future.result()[0]] = future.result()[1]

        for allegroLinkTuple, dictionary in self.result_dict.items():
            self.sortDictionaries(allegroLinkTuple, dictionary)

        self._insertLinks()
        return len(self.validLinksDict.keys()), startTime
