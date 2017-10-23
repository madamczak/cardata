import re
from logger import setUpLogger


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
        logger = setUpLogger("stripDecimalValue")
        if strippedValue.isdigit():
            return int(strippedValue)
        else:
            logger.error("Unable to strip value %s" % strippedValue)
            return -9999


class DataOperations(object):
    @staticmethod
    def getCarsProducedInYear(carData, year):
        return [car for car in carData if car[2] == year]

    @staticmethod
    def createCsvFileFromDataSet(carData, fileName):
        logger = setUpLogger("createCsvFileFromDataSet")
        dataSetString = ""
        for row in carData:
            rowString = ','.join([str(element) for element in row[2:]])
            rowString+="\n"
            dataSetString += rowString

        with open(fileName, "w") as f:
            logger.info("Creating %s file with %d number of rows" % (fileName, len(carData)))
            f.write(dataSetString)
