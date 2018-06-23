import re

from OperationUtils.data_operations import DataCleaning
from OperationUtils.url_operations import URLOperations
from OperationUtils.db_operations import DataBase
import time
from collections import OrderedDict
import datetime
import inspect

from OperationUtils.logger import Logger
moduleLogger = Logger.setLogger("cars.py")

class CarDataCollector(object):
    def __init__(self, databaseName):
        self.db = DataBase(databaseName)

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

    def ConstructBrandsTable(self, limit=2000):
        methodName = inspect.stack()[0][3]
        startAmountOfBrands = self.db.getMaxFromColumnInTable("b_id", "cars_brand")
        counter = startAmountOfBrands + 1
        moduleLogger.debug("%s - Current number of brands: %d." % (methodName, counter - 1))

        top = URLOperations.getAllBrands("https://allegro.pl/kategoria/samochody-osobowe-4029")
        for it in top.items():
            if (counter - startAmountOfBrands) > limit:
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
        return counter - startAmountOfBrands

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


    def ConstructLinkTable(self, limit=100000):
        methodName = inspect.stack()[0][3]
        numberOfNewLinks = 0

        for cat in self.db.readAllDataGenerator('cars_brand'):
            if numberOfNewLinks > limit:
                moduleLogger.info("%s - Collected more links than specified limit - %d." % (methodName, limit))
                break
            newLinks = self._getNewLinksFromCategorySite(cat)
            self._insertLinksFromCategoryToDatabase(cat, newLinks)

            numberOfNewLinks += len(newLinks)

        return numberOfNewLinks

    def _checkDigit(self, textValue):
        if type(textValue) == int or textValue.isdigit():
            return '%d,' % int(textValue)
        else:
            return '0,'

    def _checkString(self, textValue):
        if type(textValue) == str:
            return '"%s",' % textValue
        else:
            return '"%s",' % DataCleaning.normalize(textValue)

    def _getAllegroDictRegexKey(self, text, carDict):
        regex = re.compile("%s .+:" % text)

        for key in carDict.keys():
            if text in key:
                value = self._checkDigit(carDict.get(re.match(regex, key).group(), 0))
                return value
        #todo no final statement - can return None (which actually might be ok but check it)

    def constructAllegroCarInsert(self, b_id, l_id, carDict):
        methodName = inspect.stack()[0][3]

        s = """"""
        s += '%d,' % int(b_id)
        s += '%d,' % int(l_id)
        s += self._checkDigit(carDict.get('rok produkcji:', 0))

        s += self._getAllegroDictRegexKey("przebieg", carDict)

        # TODO: use regex here
        s += self._getAllegroDictRegexKey("moc", carDict)

        # s += _checkDigit(carDict.get('pojemnosc silnika [cm3]:', 0))

        s += self._getAllegroDictRegexKey("pojemnosc silnika", carDict)
        s += '"%s",' % DataCleaning.internationalizeFuel(str(carDict.get('rodzaj paliwa:', "")))
        s += '"%s",' % DataCleaning.internationalizeColor(self._checkString(carDict.get('kolor:', u"")))
        s += '"%s",' % DataCleaning.internationalizeState(carDict.get('stan:', ""))
        s += '"%s",' % DataCleaning.normalizeNumberOfDoors(str(carDict.get('liczba drzwi:', "")))

        gearboxValue = carDict.get('skrzynia biegow:', u"")  #
        if type(gearboxValue) == str:
            s += '"%s",' % DataCleaning.internationalizeGearbox(gearboxValue)
        else:
            s += '"%s",' % DataCleaning.internationalizeGearbox(DataCleaning.normalize(gearboxValue))

        try:

            s += '"%d",' % int(carDict.get('cena', 0))
        except:
            s += "0,"

        s += '"%s"' % str(datetime.datetime.now())

        moduleLogger.debug("%s - %s " % (methodName, s))

        return s

    def constructOtomotoCarInsert(self, b_id, l_id, carDict):
        methodName = inspect.stack()[0][3]

        s = """"""
        s += '%d,' % int(b_id)
        s += '%d,' % int(l_id)
        s += '%d,' % carDict.get('rok produkcji', 0)
        s += '%d,' % carDict.get('przebieg', 0)
        s += '%d,' % carDict.get('moc', 0)
        s += '%d,' % carDict.get('pojemnosc skokowa', 0)
        s += '"%s",' % DataCleaning.internationalizeFuel(str(carDict.get('rodzaj paliwa', "")))
        s += '"%s",' % DataCleaning.internationalizeColor(carDict.get('kolor', ""))
        s += '"%s",' % DataCleaning.internationalizeState(carDict.get('stan', ""))
        s += '"%s",' % DataCleaning.normalizeNumberOfDoors(str(carDict.get('liczba drzwi', "")))
        s += '"%s",' % DataCleaning.internationalizeGearbox(str(carDict.get('skrzynia biegow', "")))
        try:

            s += '"%d",' % int(carDict.get('cena', 0))
        except:
            s += "0,"

        s += '"%s"' % str(datetime.datetime.now())

        moduleLogger.debug("%s - %s" % (methodName, s))

        return s

    def logDebugDict(self, dct, param):
        msg = ""
        for k, v in dct.items():
            msg += "%s - %s" % (k, v)

        moduleLogger.debug("Car does not have %s parsed.\n Rest of dictionary: %s\n" % (param, msg))

    # TODO refactor
    def _verifyDictionary(self, carDict):
        # verify keys
        if carDict and len(carDict.keys()) < 15:
            if carDict.get('cena') is not None and carDict.get('cena') == 0:
                self.logDebugDict(carDict, "Price")
                return False

            if ":" not in carDict.keys()[0]:
                if carDict.get('rok produkcji') is not None and carDict.get('rok produkcji') == 0:
                    self.logDebugDict(carDict, "Year of production")
                    return False
                if carDict.get('przebieg') is not None:
                    if carDict.get('przebieg') == 0:
                        self.logDebugDict(carDict, "Mileage")
                        return False
                else:
                    return False
                if carDict.get('moc') is not None:
                    if carDict.get('moc') == 0:
                        self.logDebugDict(carDict, "power")
                        return False
                else:
                    return False
                if carDict.get('pojemnosc skokowa') is not None:
                    if carDict.get('pojemnosc skokowa') == 0:
                        self.logDebugDict(carDict, "capacity")
                        return False
                else:
                    return False
            else:
                if carDict.get('rok produkcji:') is not None:
                    if carDict.get('rok produkcji:') == 0:
                        self.logDebugDict(carDict, "Year of production")
                        return False
                else:
                    return False

                if carDict.get(self._getAllegroDictRegexKey("przebieg", carDict)) is not None:
                    if carDict.get(self._getAllegroDictRegexKey("przebieg", carDict)) == 0:
                        self.logDebugDict(carDict, "Mileage")
                        return False
                else:
                    return False

                if carDict.get(self._getAllegroDictRegexKey("moc [km]:", carDict)) is not None:
                    if carDict.get(self._getAllegroDictRegexKey("moc", carDict)) == 0:
                        self.logDebugDict(carDict, "power")
                        return False
                else:
                    return False

                if carDict.get(self._getAllegroDictRegexKey("pojemnosc silnika", carDict)) is not None:
                    if carDict.get(self._getAllegroDictRegexKey("pojemnosc silnika", carDict)) == 0:
                        self.logDebugDict(carDict, "capacity")
                        return False
                else:
                    return False

            return True

        else:
            moduleLogger.debug("Car dictionary has less than 15 keys. Number of keys: %d" % len(carDict))
            return False

    def _parseLinks(self, linkTuple):
        pass

    def _parseAllegroLink(self, allegroLinkTuple):
        methodName = inspect.stack()[0][3]
        d = URLOperations.parseAllegroSite(allegroLinkTuple[3])

        if self._verifyDictionary(d):
            moduleLogger.debug("%s - Verified positively. Will be inserted in cars_car table." % methodName)
            s = self.constructAllegroCarInsert(allegroLinkTuple[1], allegroLinkTuple[0], d)
            # todo: create insert car method
            self.db.insertStringData("cars_car", s)
            return 1
        else:
            moduleLogger.debug(
                "%s - Verified negatively. Will be inserted in InvalidLinks table." % methodName)
            s = """ "%d", "%s", "%s", "True" """ % (allegroLinkTuple[0], str(datetime.datetime.now()), allegroLinkTuple[3])
            # todo: create insert invalid link method
            self.db.insertStringData("invalidlinks", s)
            return 0

    def _parseOtomotoLink(self, otomotoLinkTuple):
        methodName = inspect.stack()[0][3]
        # todo: create one method for otomotoLinks
        d = URLOperations.parseOtoMotoSite2(otomotoLinkTuple[3])
        if not d:
            d = URLOperations.parseOtoMotoSite(otomotoLinkTuple[3])

        if self._verifyDictionary(d):
            moduleLogger.debug("%s - Verified positively. Will be inserted in CarData table." % methodName)
            s = self.constructOtomotoCarInsert(otomotoLinkTuple[1], otomotoLinkTuple[0], d)
            self.db.insertStringData("cars_car", s)
            return 1
        else:
            moduleLogger.debug(
                "%s - Verified negatively. Will be inserted in InvalidLinks table." % methodName)
            s = """ "%d", "%s", "%s", "True" """ % (otomotoLinkTuple[0], str(datetime.datetime.now()), otomotoLinkTuple[3])
            self.db.insertStringData("invalidlinks", s)
            return 0


    def ConstructCarsTable(self, limit=300000):
        methodName = inspect.stack()[0][3]

        newCars = 0
        #todo: this variable seems to be only used in logging - remove it
        currentB_id = ""

        counter = 0
        #todo: create method to get all unparsed links
        for entry in self.db.readAllDataGenerator('links', where='WHERE parsed = "False"'):
            if counter > limit:
                moduleLogger.info("%s - Collected %d cars." % (methodName, limit))
                break
            counter += 1

            if currentB_id != entry[1]:
                currentB_id = entry[1]
                moduleLogger.info("%s - %s - Currently working on links from %s b_id. It has %s l_id" %
                                  (datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), methodName, entry[1], entry[0]))

            if 'allegro' in entry[3]:
                newCars += self._parseAllegroLink(entry)

            elif 'otomoto' in entry[3]:
                newCars += self._parseOtomotoLink(entry)

            #todo: there should be unit test for this line below
            self.db.executeSqlCommand("""UPDATE links SET parsed = "True" WHERE link = "%s" """ % entry[3])
        return newCars

    @staticmethod
    def constructDBTables(db):
        brandsDict = OrderedDict(
            [('b_id', "INT"), ('brandname', "TEXT"), ('modelname', "TEXT"), ('version', "TEXT"), ('link', "TEXT")])
        linksDict = OrderedDict(
            [('l_id', "INT"), ('b_id', "INT"), ('time', "TEXT"), ('link', "TEXT"), ('parsed', 'BOOL')])
        oldLinksDict = OrderedDict(
            [('l_id', "INT"), ('b_id', "INT"), ('time', "TEXT"), ('link', "TEXT"), ('parsed', 'BOOL')])
        InvalidLinksDict = OrderedDict([('l_id', "INT"), ('time', "TEXT"), ('link', "TEXT"), ('parsed', 'BOOL')])
        carDataDict = OrderedDict(
            [('b_id', "INT"), ('l_id', "INT"), ('year', "INT"), ('mileage', "INT"), ('power', "INT"),
             ('capacity', "INT"), ('fuel', "TEXT"), ('color', "TEXT"), ('usedornew', "TEXT"),
             ('doors', "TEXT"), ('gearbox', "TEXT"), ('price', "INT"), ('time', "TEXT")])
        CycleDict = OrderedDict([('start_brands', "TEXT"), ('start_links', "TEXT"), ('start_cars', "TEXT"),
                                 ('end_time', "TEXT"), ('new_brands', "INT"), ('new_links', "INT"),
                                 ('new_cars', "INT")])

        db.createTable('cars_brand', brandsDict)
        db.createTable('links', linksDict)
        db.createTable('oldlinks', oldLinksDict)
        db.createTable('cars_car', carDataDict)
        db.createTable('invalidlinks', InvalidLinksDict)
        db.createTable('collectcycle', CycleDict)

    # todo: use only datetime module, refactor 3 below methods
    def _collectBrands(self, limit=2000):

        methodName = inspect.stack()[0][3]
        beginBrands = time.time()
        startTime = str(datetime.datetime.now())
        newBrands = self.ConstructBrandsTable(limit)
        moduleLogger.info("%s - Brands done. %s. Number of new brands: %d. Done in %d seconds." %
                         (methodName, startTime, newBrands, time.time() - beginBrands))

        return newBrands, startTime

    # todo: use only datetime module
    def _collectLinks(self, limit=100000):
        methodName = inspect.stack()[0][3]
        beginLinks = time.time()
        startTime = str(datetime.datetime.now())
        newLinks = self.ConstructLinkTable(limit)
        moduleLogger.info("%s - Links done.  %s. Number of new links:  %d. Done in %d seconds." %
                          (methodName, startTime, newLinks, time.time() - beginLinks))
        return newLinks, startTime

    # todo: use only datetime module
    def _collectCars(self, limit=200000):
        methodName = inspect.stack()[0][3]
        beginCars = time.time()
        startTime = str(datetime.datetime.now())
        newCars = self.ConstructCarsTable(limit)
        moduleLogger.info("%s - Cars done.   %s. Number of new cars:   %d. Done in %d seconds." %
                          (methodName, startTime, newCars, time.time() - beginCars))

        return newCars, startTime

    def _collectNormal(self, brandsLimit=2000, linksLimit=100000, carslimit=200000):
        # start brands
        newBrands, brandsStartTime = self._collectBrands(brandsLimit)
        dbmsg = """ "%s",  """ % brandsStartTime

        # start links
        newLinks, linksStartTime = self._collectLinks(linksLimit)
        dbmsg += """ "%s", """ % linksStartTime

        # start cars
        newCars, carsStartTime = self._collectCars(carslimit)
        dbmsg += """ "%s", """ % carsStartTime

        # end time
        endTime = str(datetime.datetime.now())
        dbmsg += """ "%s", """ % endTime
        dbmsg += "%d, %d, %d" % (newBrands, newLinks, newCars)

        self.db.insertStringData("collectcycle", dbmsg)
        return brandsStartTime, newBrands, newLinks, newCars, endTime

    def _collectReversed(self, brandsLimit=2000, linksLimit=100000, carslimit=200000):
        # start cars
        newCars, carsStartTime = self._collectCars(carslimit)
        dbmsg = """ "%s", """ % carsStartTime

        # start brands
        newBrands, brandsStartTime = self._collectBrands(brandsLimit)
        dbmsg += """ "%s",  """ % brandsStartTime

        # start links
        newLinks, linksStartTime = self._collectLinks(linksLimit)
        dbmsg += """ "%s", """ % linksStartTime

        # end time
        endTime = str(datetime.datetime.now())
        dbmsg += """ "%s", """ % endTime
        dbmsg += "%d, %d, %d" % (newBrands, newLinks, newCars)

        self.db.insertStringData("collectcycle", dbmsg)
        return carsStartTime, newBrands, newLinks, newCars, endTime

    def _logEndCycleMessage(self, startTime, newBrands, newLinks, newCars, endTime):
        message = '\nStarted: %s\n' % startTime
        message += "New Brands: %d\nNew Links:  %d\nNew Cars:   %d\n" % (newBrands, newLinks, newCars)
        message += "End date: %s" % endTime
        moduleLogger.info("%s" % message)

    def collect(self, brandsLimit=2000, linksLimit=100000, carslimit=200000, reversed=False):
        methodName = inspect.stack()[0][3]

        moduleLogger.info('%s - Started: %s' % (methodName, datetime.datetime.now().strftime("%d-%m-%Y %H:%M")))
        CarDataCollector.constructDBTables(self.db)
        while True:
            if not reversed:
                startTime, newBrands, newLinks, newCars, endTime = \
                    self._collectNormal(brandsLimit, linksLimit, carslimit)
            else:
                startTime, newBrands, newLinks, newCars, endTime = \
                    self._collectReversed(brandsLimit, linksLimit, carslimit)

            # clean old links from db
            self.db.clearParsedLinks()

            self._logEndCycleMessage(startTime, newBrands, newLinks, newCars, endTime)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='CarDataCollector')
    parser.add_argument('database_name', metavar='DATABASE_NAME', type=str, nargs=1,
                        help='Name of a database file. If such file name does not exists, it will be created.')

    parser.add_argument("--brands_limit", type=int, required=False, default=2000,
                        help='Maximum number of brands to be collected in one cycle.')
    parser.add_argument("--links_limit", type=int, required=False, default=100000,
                        help='Maximum number of links to be collected in one cycle.')
    parser.add_argument("--cars_limit", type=int, required=False, default=200000,
                        help='Maximum number of cars to be collected in one cycle.')
    parser.add_argument("--reversed", required=False, action='store_true',
                        help='Start with parsing stored links insead of collecting new links.')


    args = parser.parse_args()
    collector = CarDataCollector(args.database_name[0])
    collector.collect(args.brands_limit, args.links_limit, args.cars_limit, args.reversed)

