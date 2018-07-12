import inspect
import re

import datetime

from OperationUtils.data_operations import DataCleaning
from OperationUtils.logger import Logger
moduleLogger = Logger.setLogger("CarsCollector")

class CarVerificationUtils(object):
    def _checkDigit(self, textValue):
        if type(textValue) == int or textValue.isdigit():
            return '%d,' % int(textValue)
        else:
            return '0,'

    def _checkString(self, textValue):
        if type(textValue) == str:
            return '%s' % textValue
        else:
            return "%s" % DataCleaning.normalize(textValue)

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

    # TODO refactor, testing
    def verifyDictionary(self, carDict):
        # verify keys
        if carDict and len(carDict.keys()) >= 8:
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
                mileage = self._getAllegroDictRegexKey("przebieg", carDict)
                if mileage is not None:
                    if mileage == 0:
                        self.logDebugDict(carDict, "Mileage")
                        return False
                else:
                    return False

                power = self._getAllegroDictRegexKey("moc", carDict)
                if power is not None:
                    if power == 0:
                        self.logDebugDict(carDict, "power")
                        return False
                else:
                    return False

                capacity = self._getAllegroDictRegexKey("pojemnosc silnika", carDict)
                if capacity is not None:
                    if capacity == 0:
                        self.logDebugDict(carDict, "capacity")
                        return False
                else:
                    return False

            return True

        else:
            moduleLogger.debug("Car dictionary has less than 15 keys. Number of keys: %d" % len(carDict))
            return False