# -*- coding: utf8 -*-

import re

import datetime

from OperationUtils.logger import Logger
import inspect
import unicodedata

moduleLogger = Logger.setLogger("dataOps")

FUELWORDSDICT = {
            'benzyna': 'petrol',
            'benzyna + lpg': 'petrol + lpg',
            'benzyna+lpg': 'petrol + lpg',
            'benzyna + cng': 'petrol + cng',
            'benzyna+cng': 'petrol + cng',
            'hybryda': 'hybrid',
            'wodor': 'hydrogen',
            'elektryczny': 'electric',
            'etanol': 'ethanol',
            'diesel': 'diesel',
            'inny': 'other'}

COLORWORDSDICT = {
            'biay': 'white',
            'biel': 'white',
            'czarny': 'black',
            'czern': 'black',
            'niebieski': 'blue',
            'zolty': 'yellow',
            'pomaranczowy': 'orange',
            'inny kolor': 'other',
            'inny': 'other',
            'czerwony': 'red',
            'bordowy': 'maroon',
            'bezowy': 'beige',
            'szary': 'gray',
            'srebrny': 'silver',
            'zloty': 'gold',
            'zielony': 'green',
            'brazowy': 'brown',
            'fioletowy': 'violet'}

STATEWORDSDICT = {
            'nowy': 'new',
            'nowe': 'new',
            'uzywane': 'used',
            'uzywany': 'used'}

GEARBOXWORDSDICT = {
            'inna': "unknown",
            'manualna': 'manual',
            'automatyczna': 'automatic',
            'automatyczna hydrauliczna (klasyczna)': 'automatic',
            'automatyczna bezstopniowa (cvt)': 'automatic - cvt',
            'automatyczna bezstopniowa cvt': 'automatic - cvt',
            'automatyczna dwusprzegowa (dct, dsg)': 'automatic - dct, dsg',
            'automatyczna dwusprzeglowa (dct, dsg)': 'automatic - dct, dsg',
            'poautomatyczna (asg, tiptronic)': 'half-automatic',
            'poautomatyczna (asg)': 'half-automatic',
            'polautomatyczna (asg, tiptronic)': 'half-automatic',
            'polautomatyczna (asg)': 'half-automatic'}

COLUMNIDDICTIONARY = {
            "b_id": 0,
            "l_id": 1,
            "year": 2,
            "mileage": 3,
            "power": 4,
            "capacity": 5,
            "fuel": 6,
            "color": 7,
            "usedornew": 8,
            "doors": 9,
            "gearbox": 10,
            "location": 11,
            "price": 12,
            "time": 13
        }

class DataCleaning(object):
    @staticmethod
    def cleanAllData(listOfCars):
        cleanedNumeric = DataCleaning.cleanAllNumericData(listOfCars)
        cleanedUnknowns = DataCleaning.cleanUnknowns(cleanedNumeric)
        return cleanedUnknowns

    @staticmethod
    def cleanAllNumericData(listOfCars):
        cleanedYear = DataCleaning.cleanYear(listOfCars)
        cleanedMileage = DataCleaning.cleanMileage(cleanedYear)
        cleanedPower = DataCleaning.cleanPower(cleanedMileage)
        cleanedCapacity = DataCleaning.cleanCapacity(cleanedPower)
        cleanedPrice = DataCleaning.cleanPrice(cleanedCapacity)
        return cleanedPrice

    @staticmethod
    def cleanUnknowns(listOfCars):
        cleaned = []
        for car in listOfCars:
            if all([col != 'unknown' for col in car]):
                cleaned.append(car)
        return cleaned

    @staticmethod
    def cleanListOfCars(listOfCars, column, minimum, maximum):
        cleaned = []
        columnId = COLUMNIDDICTIONARY.get(column)
        for car in listOfCars:
            valueToCompare = car[columnId]
            if valueToCompare > minimum and valueToCompare < maximum:
                cleaned.append(car)

        return cleaned

    @staticmethod
    def cleanYear(listOfCars, minYear=1960, maxYear=datetime.datetime.now().year):
        return DataCleaning.cleanListOfCars(listOfCars, "year", minYear, maxYear)

    @staticmethod
    def cleanMileage(listOfCars, minMileage=100, maxMileage=950000):
        return DataCleaning.cleanListOfCars(listOfCars, "mileage", minMileage, maxMileage)

    @staticmethod
    def cleanPower(listOfCars, minPower=24, maxPower=1400):
        return DataCleaning.cleanListOfCars(listOfCars, "power", minPower, maxPower)

    @staticmethod
    def cleanCapacity(listOfCars, minCapacity=600, maxCapacity=9000):
        return DataCleaning.cleanListOfCars(listOfCars, "capacity", minCapacity, maxCapacity)

    @staticmethod
    def cleanPrice(listOfCars, minPrice=400, maxPrice=1000000):
        return DataCleaning.cleanListOfCars(listOfCars, "price", minPrice, maxPrice)

    @staticmethod
    def stripDecimalValue(dval):
        #TODO: check why int
        if type(dval) == int:
            return dval


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
    def normalizeNumberOfDoors(numberOfDoors):
        if numberOfDoors == "4" or numberOfDoors == "5" or numberOfDoors == "4/5":
            return "4/5"
        elif numberOfDoors == "2" or numberOfDoors == "3" or numberOfDoors == "2/3":
            return "2/3"
        else:
            return "unknown"

    @staticmethod
    def getVersionProductionBeginYear(versionText):
        regexMatch = re.findall(r"\([0-9]{4,7}-", versionText)
        if regexMatch:
             return int(regexMatch[0][1:-1])
        else:
            return None

    @staticmethod
    def getVersionName(versionText):
        return versionText.split("(")[0].strip()

    @staticmethod
    def getVersionProductionEndYear(versionText):
        regexMatch = re.findall(r"-[0-9]{4,7}\)", versionText)
        if regexMatch:
            return int(regexMatch[0][1:-1])
        else:
            return None










    @staticmethod
    def _internationalize(text, wordsDict):
        for word in wordsDict.keys():
            if word == text:
                return text.replace(word, wordsDict.get(word))

        return "unknown"

    @staticmethod
    def internationalizeFuel(fuel):
        return DataCleaning._internationalize(fuel, FUELWORDSDICT)

    @staticmethod
    def internationalizeColor(color):
        return DataCleaning._internationalize(color, COLORWORDSDICT)

    @staticmethod
    def internationalizeState(state):
        return DataCleaning._internationalize(state, STATEWORDSDICT)

    @staticmethod
    def internationalizeGearbox(gearbox):
        return DataCleaning._internationalize(gearbox, GEARBOXWORDSDICT)

    @staticmethod
    def normalize(unicodeValue):
        unicodeValue = unicodeValue.strip().lower()
        if unicodeValue == u"żółty":
            return "zolty"
        elif unicodeValue == u"złoty":
            return "zloty"
        else:
            return unicodedata.normalize('NFKD', unicodeValue.strip()).encode('ascii', 'ignore').lower()

#todo: move to another file, this will be a lot more important when data analysis will start
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
