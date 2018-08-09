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
        #todo: change result_dict to some more meaningful name
        self.result_dict = {}

    def _getNewLinksFromCategorySite(self, categoryTuple):
        #todo: is this extensive logging necessary? Create a method that will handle log time etc.
        #todo: multithreaded logging
        methodName = inspect.stack()[0][3]
        moduleLogger.info("%s - %s - Working on category with id: %s, link: %s." %
                          (methodName, datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
                           categoryTuple[0], categoryTuple[4]))

        return categoryTuple[0], [str(link) for link in URLOperations.getLinksFromCategorySite(categoryTuple[4])]

    def _insertLinksFromCategoryToDatabase(self, b_id, links):
        methodName = inspect.stack()[0][3]
        counter = self.db.getAmountOfLinks() + 1
        numberOfNewLinks = 0

        for link in links:
            if not self.db.linkIsPresentInDatabase(str(link)):
                self.db.insertLinkToDatabase(counter, b_id, link)
                counter += 1
                numberOfNewLinks += 1

        #todo: is this logging necessary? Create a method for that.
        if links:
            moduleLogger.info("%s - Number of new links: %d." % (methodName, len(links)))
        else:
            moduleLogger.info("%s - There weren't any new links in category with b_id: %d" %
                              (methodName, b_id))
        return numberOfNewLinks

    def Collect(self, limit=100000):
        numberOfNewLinks = 0
        startTime = datetime.datetime.now()

        with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count()) as crawler_link_threads:
            future_tasks = {crawler_link_threads.submit(self._getNewLinksFromCategorySite, cat):
                                cat for cat in self.db.readAllBrands()}
            for future in concurrent.futures.as_completed(future_tasks):
                self.result_dict[future.result()[0]] = future.result()[1]

        for b_id, links in self.result_dict.items():
            numberOfNewLinks += self._insertLinksFromCategoryToDatabase(b_id, links)

        return numberOfNewLinks, startTime
