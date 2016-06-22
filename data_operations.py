import re

class DataValidation(object):
    @staticmethod
    def validateYear(year):
        if u'\u017c' in year:
            return False
        if int(year) < 1950 or int(year) > 2016:
            return False
        else:
            return True

    @staticmethod
    def validatePower(power):
        if u'\u017c' in power:
            return False
        if int(power) < 20 or int(power) > 1500:
            return False
        else:
            return True

    @staticmethod
    def validateMilegae(mileage):
        if u'\u017c' in mileage:
            return False
        if int(mileage) < 0:
            return False
        else:
            return True

    @staticmethod
    def isMileageSuspicious(mileage):
        if u'\u017c' in mileage:
            return False
        if int(mileage) < 10000:
            return True
        else:
            return False

    @staticmethod
    def validateVolume(volume):
        if u'\u017c' in volume:
            return False
        if int(volume) < 150 or int(volume) > 20000:
            return False
        else:
            return True

    @staticmethod
    def stripDecimalValue(dval):
        dval = dval.replace(" ", "")
        decimal = re.match("\d+", dval)
        if decimal is None:
            return dval
        else:
            return decimal.group()

    @staticmethod
    def cleanWholeCarDict(cDict):
        newDict = {}
        for item in cDict.items():
            newDict[item[0].strip()] = DataValidation.stripDecimalValue(item[1].strip())

        return newDict

    @staticmethod
    def validateOtomotoCarDict(cDict):

        if cDict.get(u'Pojemno\u015b\u0107 skokowa', None) is None\
                or not DataValidation.validateVolume(cDict.get(u'Pojemno\u015b\u0107 skokowa', 0)):
            return False, ""#"Volume is not valid: %d" % cDict.get(u'Pojemno\u015b\u0107 skokowa', 0)

        if cDict.get(u'Przebieg', None) is None\
                or not DataValidation.validateMilegae(cDict.get(u'Przebieg', 0)):
            return False, ""#"Mileage is not valid: %d" % cDict.get(u'Przebieg', 0)

        if cDict.get(u'Moc', None) is None\
                or not DataValidation.validatePower(cDict.get(u'Moc', 0)):
            return False,""# "Power is not valid: %d" % cDict.get(u'Moc', 0)

        if cDict.get(u'Rok produkcji', None) is None\
                or not DataValidation.validateYear(cDict.get(u'Rok produkcji', 0)):
            return False, ""#"Year is not valid: %d" % cDict.get(u'Rok produkcji', None)

        return True, 'OK'


    @staticmethod
    def validateAllegrCarDict(cDict):

        if cDict.get(u'Pojemno\u015b\u0107 silnika [cm3]:', None) is None\
                or not DataValidation.validateVolume(cDict.get(u'Pojemno\u015b\u0107 silnika [cm3]:', 0)):
            return False, ""#"Volume is not valid: %d" % cDict.get(u'Pojemno\u015b\u0107 silnika [cm3]:', 0)

        if cDict.get(u'Przebieg [km]:', None) is None\
                or not DataValidation.validateMilegae(cDict.get(u'Przebieg [km]:', 0)):
            return False, ''# "Mileage is not valid: %d" % cDict.get(u'Przebieg [km]:', 0)

        if cDict.get(u'Moc [KM]:', None) is None\
                or not DataValidation.validatePower(cDict.get(u'Moc [KM]:', 0)):
            return False, ""#"Power is not valid: %d" % cDict.get(u'Moc [KM]:', 0)

        if cDict.get(u'Rok produkcji:', None) is None\
                or not DataValidation.validateYear(cDict.get(u'Rok produkcji:', 0)):
            return False, ""%"Year is not valid: %d" % cDict.get(u'Rok produkcji:', None)

        return True, 'OK'
