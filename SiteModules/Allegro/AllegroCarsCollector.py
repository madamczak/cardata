from SiteModules.common_cars_collector import CarsCollector
from multiprocessing import cpu_count
from SiteModules.Allegro.AllegroUrlOperations import AllegroURLOperations
import datetime
import concurrent.futures

from OperationUtils.logger import Logger
moduleLogger = Logger.setLogger("AllegroCarsCollector")


class AllegroCarsCollector(CarsCollector):
    def _parseAllegroLink(self, allegroLinkTuple):
        return allegroLinkTuple, AllegroURLOperations.parseAllegroSite(allegroLinkTuple[3])

    def sortDictionaries(self, allegroLinkTuple, d):
        if self.verificator.verifyAllegroDictionary(d):
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

    def Collect(self):
        startTime = datetime.datetime.now()

        with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count()) as crawler_link_threads:
            future_tasks = {crawler_link_threads.submit(self._parseAllegroLink, link):
                                link for link in self.db.readAllUnparsedLinksOfSiteCategory(1)}
            for future in concurrent.futures.as_completed(future_tasks):
                self.carsResultDict[future.result()[0]] = future.result()[1]

        for allegroLinkTuple, carDictionary in self.carsResultDict.items():
            self.sortDictionaries(allegroLinkTuple, carDictionary)

        self._insertLinks()
        return len(self.validLinksDict.keys()), startTime
