from SiteModules.common_links_collector import LinksCollector

import threading

from SiteModules.Allegro.AllegroUrlOperations import AllegroURLOperations
import datetime
import inspect
from multiprocessing import cpu_count
from OperationUtils.logger import Logger
import concurrent.futures

moduleLogger = Logger.setLogger("AllegroLinksCollector")


class AllegroLinksCollector(LinksCollector):
    def _getNewLinksFromCategorySite(self, categoryTuple):
        methodName = inspect.stack()[0][3]
        moduleLogger.info("%s - %s - Working on category with id: %s, link: %s." %
                          (methodName, threading.current_thread().name, categoryTuple[0], categoryTuple[4]))

        return categoryTuple[0], [str(link) for link in AllegroURLOperations.getLinksFromCategorySite(categoryTuple[4])]

    def _insertLinksFromCategoryToDatabase(self, b_id, links):
        methodName = inspect.stack()[0][3]
        counter = self.db.getAmountOfLinks() + 1
        numberOfNewLinks = 0

        for link in links:
            if not self.db.linkIsPresentInDatabase(str(link)):
                self.db.insertLinkToDatabase(counter, b_id, link)
                counter += 1
                numberOfNewLinks += 1

        moduleLogger.info("%s - Number of new links: %d." % (methodName, len(links)))

        return numberOfNewLinks

    def Collect(self):
        numberOfNewLinks = 0
        startTime = datetime.datetime.now()

        with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count()) as crawler_link_threads:
            future_tasks = [crawler_link_threads.submit(self._getNewLinksFromCategorySite, cat)
                                for cat in self.db.readAllBrands()]
            for future in concurrent.futures.as_completed(future_tasks):
                self.result_dict[future.result()[0]] = future.result()[1]

        for b_id, links in self.result_dict.items():
            numberOfNewLinks += self._insertLinksFromCategoryToDatabase(b_id, links)

        return numberOfNewLinks, startTime
