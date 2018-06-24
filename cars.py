import re

from OperationUtils.data_operations import DataCleaning
from OperationUtils.url_operations import URLOperations
from OperationUtils.db_operations import DataBase
import time
from collections import OrderedDict
import datetime
import inspect

from Collectors.BrandsCollector import BrandsCollector
from Collectors.LinksCollector import LinksCollector
from Collectors.CarsCollector import CarsCollector

from OperationUtils.logger import Logger
moduleLogger = Logger.setLogger("cars.py")

class CarDataCollector(object):
    def __init__(self, databaseName):
        self.db = DataBase(databaseName)

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

    def _collectNormal(self, brandsLimit=2000, linksLimit=100000, carslimit=200000):
        # start brands
        newBrands, brandsStartTime = BrandsCollector(self.db).Collect(limit=brandsLimit)
        dbmsg = """ "%s",  """ % str(brandsStartTime)

        # start links
        newLinks, linksStartTime = LinksCollector(self.db).Collect(limit=linksLimit)
        dbmsg += """ "%s", """ % str(linksStartTime)

        # start cars
        newCars, carsStartTime = CarsCollector(self.db).Collect(limit=carslimit)
        dbmsg += """ "%s", """ % str(carsStartTime)

        # end time
        endTime = str(datetime.datetime.now())
        dbmsg += """ "%s", """ % endTime
        dbmsg += "%d, %d, %d" % (newBrands, newLinks, newCars)

        self.db.insertStringData("collectcycle", dbmsg)
        return brandsStartTime, newBrands, newLinks, newCars, endTime

    def _collectReversed(self, brandsLimit=2000, linksLimit=100000, carslimit=200000):
        # start cars
        newCars, carsStartTime = CarsCollector(self.db).Collect(limit=carslimit)
        dbmsg = """ "%s", """ % str(carsStartTime)

        # start brands
        newBrands, brandsStartTime = BrandsCollector(self.db).Collect(limit=brandsLimit)
        dbmsg += """ "%s",  """ % str(brandsStartTime)

        # start links
        newLinks, linksStartTime = LinksCollector(self.db).Collect(limit=linksLimit)
        dbmsg += """ "%s", """ % str(linksStartTime)

        # end time
        endTime = str(datetime.datetime.now())
        dbmsg += """ "%s", """ % endTime
        dbmsg += "%d, %d, %d" % (newBrands, newLinks, newCars)

        self.db.insertStringData("collectcycle", dbmsg)
        return carsStartTime, newBrands, newLinks, newCars, endTime

    def _logEndCycleMessage(self, startTime, newBrands, newLinks, newCars, endTime, cycleNumber):
        message = '\nStarted: %s\n' % startTime
        message += "New Brands: %d\nNew Links:  %d\nNew Cars:   %d\n" % (newBrands, newLinks, newCars)
        message += "End date: %s\n" % endTime
        message += "Cycle number: %d" % cycleNumber
        moduleLogger.info("%s" % message)

    def Collect(self, brandsLimit=2000, linksLimit=100000, carslimit=200000, reversed=False, howManyCycles=None):
        methodName = inspect.stack()[0][3]

        moduleLogger.info('%s - Started: %s' % (methodName, datetime.datetime.now().strftime("%d-%m-%Y %H:%M")))
        CarDataCollector.constructDBTables(self.db)

        whileLoopCounter = 0
        while True:
            if howManyCycles is not None and whileLoopCounter >= howManyCycles:
                break

            if not reversed:
                startTime, newBrands, newLinks, newCars, endTime = \
                    self._collectNormal(brandsLimit, linksLimit, carslimit)
            else:
                startTime, newBrands, newLinks, newCars, endTime = \
                    self._collectReversed(brandsLimit, linksLimit, carslimit)

            # clean old links from db
            self.db.clearParsedLinks()

            self._logEndCycleMessage(startTime, newBrands, newLinks, newCars, endTime, whileLoopCounter)
            whileLoopCounter += 1

        moduleLogger.info('%s - End of collection.' % methodName)


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
    collector.Collect(args.brands_limit, args.links_limit, args.cars_limit, args.reversed)

