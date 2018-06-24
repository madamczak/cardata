import re, datetime

from OperationUtils.data_operations import DataCleaning
from OperationUtils.url_operations import URLOperations
from OperationUtils.db_operations import DataBase
import inspect
from OperationUtils.logger import Logger

moduleLogger = Logger.setLogger("BrandsCollector")

#todo: Test for Collect method
class BrandsCollector(object):
    def __init__(self, database):
        self.db = database

    def _addNewBrandCategory(self, item, count):
        # todo: create method that verifies if brand/model/version is present in db
        methodName = inspect.stack()[0][3]

        if not self.db.valueIsPresentInColumnOfATable(item[1], 'link', "cars_brand") \
                and not self.db.valueIsPresentInColumnOfATable(item[0], 'brandname', "cars_brand"):
            s = """%d, "%s", NULL, NULL, "%s" """ % (count, item[0], item[1])
            moduleLogger.debug("%s - New brand found: %s." % (methodName, s))
            self.db.insertStringData("cars_brand", s)
            return 1
        else:
            return 0

    def _addNewModelCategory(self, item, model, count):
        methodName = inspect.stack()[0][3]

        if not self.db.valueIsPresentInColumnOfATable(model[1], 'link', "cars_brand") \
                and not self.db.valueIsPresentInColumnOfATable(model[0], 'modelname', "cars_brand"):
            s = """%d, "%s", "%s", NULL, "%s" """ % (count, item[0], model[0], model[1])
            moduleLogger.debug("%s - New model found: %s." % (methodName, s))
            self.db.insertStringData("cars_brand", s)
            return 1
        else:
            return 0

    def _addNewVersionCategory(self, item, model, ver, count):
        methodName = inspect.stack()[0][3]
        versionName = DataCleaning.normalize(ver[0])
        pattern1 = re.compile(".*\(\d+-")
        pattern2 = re.compile(".*T\d")

        if not self.db.valueIsPresentInColumnOfATable(ver[1], 'link', "cars_brand") \
                and (pattern1.match(str(versionName)) or pattern2.match(str(versionName))):
            s = """%d, "%s", "%s", "%s", "%s" """ % (count, item[0], model[0], ver[0], ver[1])
            moduleLogger.debug("%s - New version found: %s." % (methodName, s))
            self.db.insertStringData("cars_brand", s)
            return 1
        else:
            return 0

    def _bottomReached(self, upperDictionary, lowerDictionary):
        return all([k in upperDictionary.keys() for k in lowerDictionary.keys()])

    def Collect(self, limit=2000):
        methodName = inspect.stack()[0][3]

        startAmountOfBrands = self.db.getMaxFromColumnInTable("b_id", "cars_brand")
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