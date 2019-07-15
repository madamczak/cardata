import inspect
import re

import datetime

from OperationUtils.data_operations import DataCleaning
from OperationUtils.logger import Logger
moduleLogger = Logger.setLogger("CarsCollector")

class CarVerificationUtils(object):
    def _checkDigit(self, textValue):
        # todo: verify if both ways are used, fix accordingly
        if type(textValue) == int or textValue.isdigit():
            return '%d,' % int(textValue)
        else:
            return '0,'

    def _checkString(self, textValue):
        #todo: verify if both ways are used, fix accordingly
        if type(textValue) == str:
            return '%s' % textValue
        else:
            return "%s" % DataCleaning.normalize(textValue)

    def constructOtoMotoCarInsert(self, b_id, l_id, carDict):
        methodName = inspect.stack()[0][3]
        s = """"""
        s += '%d,' % int(b_id)
        s += '%d,' % int(l_id)
        s += self._checkDigit(DataCleaning.stripDecimalValue(carDict.get('rok produkcji', 0)))
        s += self._checkDigit(DataCleaning.stripDecimalValue(carDict.get('przebieg', 0)))
        s += self._checkDigit(DataCleaning.stripDecimalValue(carDict.get('moc', 0)))
        s += self._checkDigit(DataCleaning.stripDecimalValue(carDict.get('pojemnosc skokowa', 0)))
        s += '"%s",' % DataCleaning.internationalizeFuel(str(carDict.get('rodzaj paliwa', "")))
        s += '"%s",' % DataCleaning.internationalizeColor(self._checkString(carDict.get('kolor', u"")))
        s += '"%s",' % DataCleaning.internationalizeState(carDict.get('stan', ""))
        s += '"%s",' % DataCleaning.normalizeNumberOfDoors(str(carDict.get('liczba drzw:', "")))

        gearboxValue = carDict.get('skrzynia biegow', u"")  #
        if type(gearboxValue) == str:
            s += '"%s",' % DataCleaning.internationalizeGearbox(gearboxValue)
        else:
            s += '"%s",' % DataCleaning.internationalizeGearbox(DataCleaning.normalize(gearboxValue))

        s += '"%s",' % carDict.get('location', "")

        s += '"%d",' % int(float(carDict.get('price', 0)))

        s += '"%s",' % str(datetime.datetime.now())
        s += '%d' % 2  # TODO: switch to getting allegro id from database

        moduleLogger.debug("%s - %s " % (methodName, s))

        return s

    def constructAllegroCarInsert(self, b_id, l_id, carDict):
        #todo: this would look so much better if Car object would be created, is there time for that?
        methodName = inspect.stack()[0][3]

        s = """"""
        s += '%d,' % int(b_id)
        s += '%d,' % int(l_id)
        s += self._checkDigit(DataCleaning.stripDecimalValue(carDict.get('rok produkcji:', 0)))
        s += self._checkDigit(DataCleaning.stripDecimalValue(carDict.get('przebieg:', 0)))
        s += self._checkDigit(DataCleaning.stripDecimalValue(carDict.get('moc:', 0)))
        s += self._checkDigit(DataCleaning.stripDecimalValue(carDict.get('pojemnosc silnika:', 0)))
        s += '"%s",' % DataCleaning.internationalizeFuel(str(carDict.get('rodzaj paliwa:', "")))
        s += '"%s",' % DataCleaning.internationalizeColor(self._checkString(carDict.get('kolor:', u"")))
        s += '"%s",' % DataCleaning.internationalizeState(carDict.get('stan:', ""))
        s += '"%s",' % DataCleaning.normalizeNumberOfDoors(str(carDict.get('liczba drzwi:', "")))

        gearboxValue = carDict.get('skrzynia biegow:', u"")  #
        if type(gearboxValue) == str:
            s += '"%s",' % DataCleaning.internationalizeGearbox(gearboxValue)
        else:
            s += '"%s",' % DataCleaning.internationalizeGearbox(DataCleaning.normalize(gearboxValue))

        s += '"%s",' % carDict.get('miejsce', "")
        s += '"%d",' % int(carDict.get('cena', 0))
        s += '"%s",' % str(datetime.datetime.now())
        s += '%d' % 1 #TODO: switch to getting allegro id from database

        moduleLogger.debug("%s - %s " % (methodName, s))

        return s

    #todo: change to private
    def logDebugDict(self, dct, param):
        msg = ""
        for k, v in dct.items():
            msg += "%s - %s" % (k, v)

        moduleLogger.debug("Car does not have %s parsed.\n Rest of dictionary: %s\n" % (param, msg))

    # TODO refactor, testing
    def verifyAllegroDictionary(self, carDict):
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
                mileage = carDict.get('przebieg:')
                if mileage is not None:
                    if mileage == 0:
                        self.logDebugDict(carDict, "Mileage")
                        return False
                else:
                    return False

                power = carDict.get('moc:')
                if power is not None:
                    if power == 0:
                        self.logDebugDict(carDict, "power")
                        return False
                else:
                    return False

                capacity = carDict.get('pojemnosc silnika:')
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

    # TODO refactor, testing
    def verifyOtoMotoDictionary(self, carDict):
        # verify keys
        if carDict and len(carDict.keys()) >= 8:
            if carDict.get('price') is not None and carDict.get('price') == 0:
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
                mileage = carDict.get('przebieg:')
                if mileage is not None:
                    if mileage == 0:
                        self.logDebugDict(carDict, "Mileage")
                        return False
                else:
                    return False

                power = carDict.get('moc:')
                if power is not None:
                    if power == 0:
                        self.logDebugDict(carDict, "power")
                        return False
                else:
                    return False

                capacity = carDict.get('pojemnosc silnika:')
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