from SiteModules.common_cars_collector import CarsCollector
from multiprocessing import cpu_count
from SiteModules.OtoMoto.OtoMotoUrlOperations import OtoMotoURLOperations
import datetime
import concurrent.futures

from OperationUtils.logger import Logger
moduleLogger = Logger.setLogger("OtoMotoCarsCollector")

class OtoMotoCarsCollector(CarsCollector):
    def _parseOtoMotoLink(self, otoMotoLinkTuple):
        return allegroLinkTuple, OtoMotoURLOperations.parseOtomotoSite(otoMotoLinkTuple[3])

    def sortDictionaries(self, otoMotoLinkTuple, d):
        if self.verificator.verifyDictionary(d):
            self.validLinksDict[otoMotoLinkTuple] = d
        else:
            self.invalidLinksList.append(otoMotoLinkTuple)

    def _insertLinks(self):
        self._insertValidLinks()
        self._insertInvalidLinks()

    def _insertInvalidLinks(self):
        for invalidLinkTuple in self.invalidLinksList:
            self.db.updateParsedParameterForLinkWithId(invalidLinkTuple[0])
            self.db.insertInvalidLinkToDatabase(invalidLinkTuple[0], invalidLinkTuple[3])

    def _insertValidLinks(self):
        for validLinkTuple, carDictionary in self.validLinksDict.items():
            self.db.updateParsedParameterForLinkWithId(validLinkTuple[0])
            self.db.insertOtoMotoCarToDatabase(validLinkTuple[1], validLinkTuple[0], carDictionary)

    def Collect(self):
        startTime = datetime.datetime.now()

        with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count()) as crawler_link_threads:
            future_tasks = {crawler_link_threads.submit(self._parseOtoMotoLink, link):
                                link for link in self.db.readAllUnparsedLinksOfSiteCategory(2)}
            for future in concurrent.futures.as_completed(future_tasks):
                self.carsResultDict[future.result()[0]] = future.result()[1]

        for otoMotoLinkTuple, carDictionary in self.carsResultDict.items():
            self.sortDictionaries(otoMotoLinkTuple, carDictionary)

        self._insertLinks()
        return len(self.validLinksDict.keys()), startTime
