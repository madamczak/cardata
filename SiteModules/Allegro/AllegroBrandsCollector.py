from SiteModules.common_brands_collector import BrandsCollector
import re, datetime

from OperationUtils.data_operations import DataCleaning
from SiteModules.Allegro.AllegroUrlOperations import AllegroURLOperations
import inspect
from OperationUtils.logger import Logger

moduleLogger = Logger.setLogger("AllegroBrandsCollector")
TOPLINK = "https://allegro.pl/kategoria/samochody-osobowe-4029"


class AllegroBrandsCollector(BrandsCollector):
    def _addNewBrandCategory(self, item, count):
        if not self.db.allegroBrandLinkIsPresentInDatabase(item[1]) and not self.db.brandNameIsPresentInDatabase(item[0]):
            self.db.insertAllegroBrandToDatabase(count, item[0], item[1])
            return 1
        else:
            return 0

    def _addNewModelCategory(self, item, model, count):
        if not self.db.allegroBrandLinkIsPresentInDatabase(model[1]) and not self.db.modelNameIsPresentInDatabase(model[0]):
            self.db.insertModelToDatabase(count, item[0], model[0], model[1])
            return 1
        else:
            return 0

    def _addNewVersionCategory(self, item, model, ver, count):
        versionName = DataCleaning.normalize(ver[0])
        pattern1 = re.compile(".*\(\d+-")
        pattern2 = re.compile(".*T\d")

        if not self.db.allegroBrandLinkIsPresentInDatabase(ver[1]) \
                and (pattern1.match(str(versionName)) or pattern2.match(str(versionName))):
            self.db.insertVersionToDatabase(count, item[0], model[0], ver[0], ver[1])
            return 1
        else:
            return 0

    def _bottomReached(self, upperDictionary, lowerDictionary):
        return all([k in upperDictionary.keys() for k in lowerDictionary.keys()])

    def Collect(self, limit=2000):
        methodName = inspect.stack()[0][3]
        newBrands = 0

        counter = self.db.getAmountOfBrands() + 1
        moduleLogger.debug("%s - Current number of brands: %d." % (methodName, counter - 1))
        startTime = datetime.datetime.now()

        top = AllegroURLOperations.getAllBrands(TOPLINK)
        for it in top.items():
            if newBrands > limit:
                break

            models = AllegroURLOperations.getAllBrands(it[1])
            if not self._bottomReached(top, models):
                for model in models.items():
                    versions = AllegroURLOperations.getAllBrands(model[1])
                    if not self._bottomReached(models, versions):
                        for ver in versions.items():
                            toAdd = self._addNewVersionCategory(it, model, ver, counter)
                            counter += toAdd
                            newBrands += toAdd
                    else:
                        toAdd = self._addNewModelCategory(it, model, counter)
                        counter += toAdd
                        newBrands += toAdd
            else:
                toAdd = self._addNewBrandCategory(it, counter)
                counter += toAdd
                newBrands += toAdd

        return newBrands, startTime
