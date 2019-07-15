from SiteModules.common_cars_collector import CarsCollector
from multiprocessing import cpu_count
from SiteModules.OtoMoto.OtoMotoUrlOperations import OtoMotoURLOperations
import datetime
import concurrent.futures

from OperationUtils.logger import Logger
moduleLogger = Logger.setLogger("OtoMotoCarsCollector")

class OtoMotoCarsCollector(CarsCollector):
    def _parseOtoMotoLink(self, otoMotoLinkTuple):
        return otoMotoLinkTuple, OtoMotoURLOperations.parseOtomotoSite(otoMotoLinkTuple[3])

    def sortDictionaries(self, otoMotoLinkTuple, d):
        if self.verificator.verifyOtoMotoDictionary(d):
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
        count = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count()) as crawler_link_threads:
            future_tasks = {crawler_link_threads.submit(self._parseOtoMotoLink, link):
                                link for link in self.db.readAllUnparsedLinksOfSiteCategory(2)}
            for future in concurrent.futures.as_completed(future_tasks):
                self.db.updateParsedParameterForLinkWithId(future.result()[0][0])
                if self.verificator.verifyOtoMotoDictionary(future.result()[1]):
                    moduleLogger.info("Inserting car with l_id %s" % future.result()[0][1])
                    self.db.insertOtoMotoCarToDatabase(future.result()[0][1], future.result()[0][0], future.result()[1])
                    count += 1
                else:
                    moduleLogger.info("Not inserting car with l_id %s - verified negitively" % future.result()[0][1])

        return count, startTime
