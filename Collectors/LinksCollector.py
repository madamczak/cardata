from OperationUtils.url_operations import URLOperations
from OperationUtils.db_operations import DataBase

import datetime
import inspect

from OperationUtils.logger import Logger
moduleLogger = Logger.setLogger("LinksCollector")

#todo: Test for Collect method
class LinksCollector(object):
    def __init__(self, database):
        self.db = database

    def _getNewLinksFromCategorySite(self, categoryTuple):
        methodName = inspect.stack()[0][3]
        moduleLogger.info("%s - %s - Working on category with id: %s, link: %s." %
                          (methodName, datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
                           categoryTuple[0], categoryTuple[4]))

        return [str(link) for link in URLOperations.getLinksFromCategorySite(categoryTuple[4])
                if not self.db.valueIsPresentInColumnOfATable(str(link), 'link', "links")]

    def _insertLinksFromCategoryToDatabase(self, categoryTuple, links):
        methodName = inspect.stack()[0][3]
        counter = self.db.getMaxFromColumnInTable("l_id", "links") + 1

        for link in links:
            moduleLogger.debug("%s - Inserting link: %s to Links table." % (methodName, link))
            s = """ %d, %d, "%s", "%s", "%r" """ % \
                (counter, categoryTuple[0], str(datetime.datetime.now()), link, False)

            #todo: think about inserting links from entire list instead of inserting each one by one
            #todo: method to insert a link
            self.db.insertStringData("links", s)
            counter += 1

        if links:
            moduleLogger.info("%s - Number of new links: %d." % (methodName, len(links)))
        else:
            moduleLogger.info("%s - There weren't any new links in category with b_id: %d" %
                              (methodName, categoryTuple[0]))


    def Collect(self, limit=100000):
        methodName = inspect.stack()[0][3]
        numberOfNewLinks = 0

        startTime = datetime.datetime.now()
        for cat in self.db.readAllDataGenerator('cars_brand'):
            if numberOfNewLinks > limit:
                moduleLogger.info("%s - Collected more links than specified limit - %d." % (methodName, limit))
                break

            newLinks = self._getNewLinksFromCategorySite(cat)
            self._insertLinksFromCategoryToDatabase(cat, newLinks)

            numberOfNewLinks += len(newLinks)

        return numberOfNewLinks, startTime