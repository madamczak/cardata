import re, datetime

from OperationUtils.data_operations import DataCleaning
from OperationUtils.url_operations import URLOperations
import inspect
from OperationUtils.logger import Logger

moduleLogger = Logger.setLogger("BrandsCollector")

#todo: Test for Collect method
class BrandsCollector(object):
    def __init__(self, database):
        self.db = database

    def _addNewBrandCategory(self, item, count):
        if not self.db.brandLinkIsPresentInDatabase(item[1]) and not self.db.brandNameIsPresentInDatabase(item[0]):
            self.db.insertBrandToDatabase(count, item[0], item[1])
            return 1
        else:
            return 0

    def _addNewModelCategory(self, item, model, count):
        if not self.db.brandLinkIsPresentInDatabase(model[1]) and not self.db.modelNameIsPresentInDatabase(model[0]):
            self.db.insertModelToDatabase(count, item[0], model[0], model[1])
            return 1
        else:
            return 0

    def _addNewVersionCategory(self, item, model, ver, count):
        versionName = DataCleaning.normalize(ver[0])
        pattern1 = re.compile(".*\(\d+-")
        pattern2 = re.compile(".*T\d")

        if not self.db.brandLinkIsPresentInDatabase(ver[1]) \
                and (pattern1.match(str(versionName)) or pattern2.match(str(versionName))):
            self.db.insertVersionToDatabase(count, item[0], model[0], ver[0], ver[1])
            return 1
        else:
            return 0

    def _bottomReached(self, upperDictionary, lowerDictionary):
        return all([k in upperDictionary.keys() for k in lowerDictionary.keys()])

    def Collect(self, limit=2000):
        methodName = inspect.stack()[0][3]

        startAmountOfBrands = self.db.getAmountOfBrands()
        counter = startAmountOfBrands + 1
        moduleLogger.debug("%s - Current number of brands: %d." % (methodName, counter - 1))
        startTime = datetime.datetime.now()

        top = URLOperations.getAllBrands("https://allegro.pl/kategoria/samochody-osobowe-4029")
        for it in top.items():
            #todo: get this properly done without -1
            if (counter - 1 - startAmountOfBrands) > limit:
                moduleLogger.info("%s - Collected %d brands." % (methodName, counter - startAmountOfBrands))
                break

            models = URLOperations.getAllBrands(it[1])
            if not self._bottomReached(top, models):
                for model in models.items():
                    versions = URLOperations.getAllBrands(model[1])
                    if not self._bottomReached(models, versions):
                        for ver in versions.items():
                            counter += self._addNewVersionCategory(it, model, ver, counter)
                    else:
                        counter += self._addNewModelCategory(it, model, counter)
            else:
                counter += self._addNewBrandCategory(it, counter)
        moduleLogger.debug("%s - Number of new brands found: %d." % (methodName, counter - startAmountOfBrands))

        #todo: unit test if return does not make a mistake (+/- 1)
        return counter - startAmountOfBrands - 1, startTime