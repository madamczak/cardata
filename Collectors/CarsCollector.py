import re

from OperationUtils.data_operations import DataCleaning
from OperationUtils.url_operations import URLOperations
import datetime
import inspect
from OperationUtils.db_operations import DataBase
from OperationUtils.logger import Logger
moduleLogger = Logger.setLogger("CarsCollector")

#todo: Test for Collect method
class CarsCollector(object):
    def __init__(self, dbName):
        self.db = DataBase(dbName)

    def __del__(self):
        del self.db

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


    def Collect(self, limit=300000):
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
