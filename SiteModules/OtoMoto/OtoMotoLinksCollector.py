from OperationUtils.db_operations import DataBase
from SiteModules.common_links_collector import LinksCollector

import threading

from SiteModules.OtoMoto.OtoMotoUrlOperations import OtoMotoURLOperations
import datetime
import inspect
from multiprocessing import cpu_count
from OperationUtils.logger import Logger
import concurrent.futures

moduleLogger = Logger.setLogger("OtoMotoLinksCollector")

class OtomotoLinksCollector(LinksCollector):
    def __init__(self, database):
        LinksCollector.__init__(self, database)

    def _getNewLinksFromCategorySite(self, categoryTuple):
        methodName = inspect.stack()[0][3]
        moduleLogger.info("%s - %s - Working on category with id: %s, link: %s." %
                          (methodName, threading.current_thread().name, categoryTuple[0], categoryTuple[5]))
        newLnks = [str(link) for link in OtoMotoURLOperations.getLinksFromCategorySite(categoryTuple[5])]
        return categoryTuple[0], newLnks

    def _insertLinksFromCategoryToDatabase(self, b_id, links):
        methodName = inspect.stack()[0][3]
        counter = self.db.getAmountOfLinks() + 1
        numberOfNewLinks = 0

        for link in links:
            if not self.db.linkIsPresentInDatabase(str(link)):
                self.db.insertLinkToDatabase(counter, b_id, 2, link) #TODO: get site id from DB
                counter += 1
                numberOfNewLinks += 1

        moduleLogger.info("%s - Number of new links: %d." % (methodName, len(links)))

        return numberOfNewLinks

    def Collect(self):
        numberOfNewLinks = 0
        startTime = datetime.datetime.now()

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as crawler_link_threads:
            future_tasks = [crawler_link_threads.submit(self._getNewLinksFromCategorySite, cat)
                            for cat in self.db.readAllBrands()]
            for future in concurrent.futures.as_completed(future_tasks):
                self.result_dict[future.result()[0]] = future.result()[1]

        for b_id, links in self.result_dict.items():
            numberOfNewLinks += self._insertLinksFromCategoryToDatabase(b_id, links)

        return numberOfNewLinks, startTime

database = DataBase('..\..\crontest3TBT.db')

collector = OtomotoLinksCollector(database)

collector.Collect()
