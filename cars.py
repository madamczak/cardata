from OperationUtils.db_operations import DataBase

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

    def _collectNormal(self, brandsLimit=2000, linksLimit=100000, carslimit=200000):
        newBrands, brandsStartTime = BrandsCollector(self.db).Collect(limit=brandsLimit)
        newLinks, linksStartTime = LinksCollector(self.db).Collect(limit=linksLimit)
        newCars, carsStartTime = CarsCollector(self.db).Collect(limit=carslimit)
        endTime = str(datetime.datetime.now())
        self.db.insertCollectCycleToDatabase(brandsStartTime, linksStartTime, carsStartTime,
                                             endTime, newBrands, newLinks, newCars)
        return brandsStartTime, newBrands, newLinks, newCars, endTime

    def _collectReversed(self, brandsLimit=2000, linksLimit=100000, carslimit=200000):
        newCars, carsStartTime = CarsCollector(self.db).Collect(limit=carslimit)
        newBrands, brandsStartTime = BrandsCollector(self.db).Collect(limit=brandsLimit)
        newLinks, linksStartTime = LinksCollector(self.db).Collect(limit=linksLimit)
        endTime = str(datetime.datetime.now())
        self.db.insertCollectCycleToDatabase(brandsStartTime, linksStartTime, carsStartTime,
                                             endTime, newBrands, newLinks, newCars)
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
        self.db.constructDBTables()

        whileLoopCounter = 0
        while True:
            #todo: set this loop to run once a day/night
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

