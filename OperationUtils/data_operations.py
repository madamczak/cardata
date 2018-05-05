# -*- coding: utf8 -*-

import re
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
    def normalizeNumberOfDoors(numberOfDoors):
        if numberOfDoors == "4" or numberOfDoors == "5" or numberOfDoors == "4/5":
            return "4/5"
        elif numberOfDoors == "2" or numberOfDoors == "3" or numberOfDoors == "2/3":
            return "2/3"
        else:
            return "unknown"

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
