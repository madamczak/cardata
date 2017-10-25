import re
from logger import Logger
import inspect

moduleLogger = Logger.setLogger("dataOps")


class DataCleaning(object):
    @staticmethod
    def stripDecimalValue(dval):
        dval = dval.replace(" ", "")
        decimal = re.match("\d+", dval)
        if decimal is None:
            return dval
        else:
            return decimal.group()

    @staticmethod
    def convertToNumeric(strippedValue):
        methodName = inspect.stack()[0][3]
        if strippedValue.isdigit():
            return int(strippedValue)
        else:
            moduleLogger.error("%s - Unable to strip value %s" % (methodName, strippedValue))
            return -9999


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
