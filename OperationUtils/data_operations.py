# -*- coding: utf8 -*-

import re
from OperationUtils.logger import Logger
import inspect
import unicodedata

moduleLogger = Logger.setLogger("dataOps")


class DataCleaning(object):
    @staticmethod
    def stripDecimalValue(dval):
        dval = dval.replace("cm3", "")

        catchDoors = re.match("\d/\d", dval)
        if catchDoors:
            return catchDoors.group()

        stripped = ""
        for char in dval:
            if char.isdigit():
                stripped += char
            elif char == "." or char == ",":
                stripped += "."

        return stripped

    @staticmethod
    def normalize(unicodeValue):
        unicodeValue = unicodeValue.strip().lower()
        if unicodeValue == u"żółty":
            return "zolty"
        elif unicodeValue == u"złoty":
            return "zloty"
        else:
            return unicodedata.normalize('NFKD', unicodeValue.strip()).encode('ascii', 'ignore').lower()

class DataOperations(object):
    @staticmethod
    def getCarsProducedInYear(carData, year):
        return [car for car in carData if car[2] == year]

    @staticmethod
    def createCsvFileFromDataSet(carData, fileName):
        methodName = inspect.stack()[0][3]
        dataSetString = ""
        for row in carData:
            rowString = ','.join([str(element) for element in row[2:]])
            rowString+="\n"
            dataSetString += rowString

        with open(fileName, "w") as f:
            moduleLogger.info("s - Creating %s file with %d number of rows" % (methodName, fileName, len(carData)))
            f.write(dataSetString)
