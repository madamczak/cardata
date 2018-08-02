from OperationUtils.url_operations import URLOperations
import datetime
import inspect
from multiprocessing import cpu_count

from OperationUtils.logger import Logger
moduleLogger = Logger.setLogger("LinksCollector")
import concurrent.futures



#todo: Test for Collect method
class LinksCollector(object):
    def __init__(self, database):
        self.db = database
        self.result_dict = {}

    def _getNewLinksFromCategorySite(self, categoryTuple):
        methodName = inspect.stack()[0][3]
        moduleLogger.info("%s - %s - Working on category with id: %s, link: %s." %
                          (methodName, datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
                           categoryTuple[0], categoryTuple[4]))

        return categoryTuple[0], [str(link) for link in URLOperations.getLinksFromCategorySite(categoryTuple[4])]

    # todo: As a separate method - think about inserting links from entire list instead of inserting each one by one
    def _insertLinksFromCategoryToDatabase(self, b_id, links):
        methodName = inspect.stack()[0][3]
        counter = self.db.getAmountOfLinks() + 1

        for link in links:
            if not self.db.linkIsPresentInDatabase(str(link)):
                self.db.insertLinkToDatabase(counter, b_id, link)
                counter += 1

        if links:
            moduleLogger.info("%s - Number of new links: %d." % (methodName, len(links)))
        else:
            moduleLogger.info("%s - There weren't any new links in category with b_id: %d" %
                              (methodName, b_id))

    def Collect(self, limit=100000):
        numberOfNewLinks = 0
        startTime = datetime.datetime.now()

        with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count()) as crawler_link_threads:
            future_tasks = {crawler_link_threads.submit(self._getNewLinksFromCategorySite, cat):
                                cat for cat in self.db.readAllBrands()}
            for future in concurrent.futures.as_completed(future_tasks):
                self.result_dict[future.result()[0]] = future.result()[1]

        for b_id, links in self.result_dict.items():
            self._insertLinksFromCategoryToDatabase(b_id, links)
            numberOfNewLinks += len(links)

        return numberOfNewLinks, startTime
