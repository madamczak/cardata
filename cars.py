from OperationUtils.db_operations import DataBase

import datetime
import inspect
import time
from SiteModules.Allegro.AllegroBrandsCollector import AllegroBrandsCollector
from SiteModules.Allegro.AllegroLinksCollector import AllegroLinksCollector
from SiteModules.Allegro.AllegroCarsCollector import AllegroCarsCollector
from OperationUtils.logger import Logger
from SiteModules.OtoMoto.OtoMotoBrandsCollector import OtoMotoBrandsCollector
from SiteModules.OtoMoto.OtoMotoCarsCollector import OtoMotoCarsCollector
from SiteModules.OtoMoto.OtoMotoLinksCollector import OtomotoLinksCollector

moduleLogger = Logger.setLogger("cars.py")

class CarDataCollector(object):
    def __init__(self, databaseName):
        self.db = DataBase(databaseName)

    def _collectNormalOtoMoto(self, brandsLimit=2000):
        newBrands, brandsStartTime = OtoMotoBrandsCollector(self.db).Collect(limit=brandsLimit)
        newLinks, linksStartTime = OtomotoLinksCollector(self.db).Collect()

        print "End of links"

        newCars, carsStartTime = OtoMotoCarsCollector(self.db).Collect()
        endTime = str(datetime.datetime.now())
        self.db.insertOtoMotoCollectCycleToDatabase(brandsStartTime, linksStartTime, carsStartTime,
                                                    endTime, newBrands, newLinks, newCars)
        return brandsStartTime, newBrands, newLinks, newCars, endTime

    def _collectNormalAllegro(self, brandsLimit=2000):
        newBrands, brandsStartTime = AllegroBrandsCollector(self.db).Collect(limit=brandsLimit)
        newLinks, linksStartTime = AllegroLinksCollector(self.db).Collect()
        newCars, carsStartTime = AllegroCarsCollector(self.db).Collect()
        endTime = str(datetime.datetime.now())
        self.db.insertAllegroCollectCycleToDatabase(brandsStartTime, linksStartTime, carsStartTime,
                                                    endTime, newBrands, newLinks, newCars)
        return brandsStartTime, newBrands, newLinks, newCars, endTime

    def _collectReversedAllegro(self, brandsLimit=2000):
        newCars, carsStartTime = AllegroCarsCollector(self.db).Collect()
        newBrands, brandsStartTime = AllegroBrandsCollector(self.db).Collect(limit=brandsLimit)
        newLinks, linksStartTime = AllegroLinksCollector(self.db).Collect()
        endTime = str(datetime.datetime.now())
        self.db.insertAllegroCollectCycleToDatabase(brandsStartTime, linksStartTime, carsStartTime,
                                                    endTime, newBrands, newLinks, newCars)
        return carsStartTime, newBrands, newLinks, newCars, endTime

    def _logEndCycleMessage(self, startTime, newBrands, newLinks, newCars, endTime, cycleNumber):
        message = '\nStarted: %s\n' % startTime
        message += "New Brands: %d\nNew Links:  %d\nNew Cars:   %d\n" % (newBrands, newLinks, newCars)
        message += "End date: %s\n" % endTime
        message += "Cycle number: %d" % cycleNumber
        moduleLogger.info("%s" % message)

    def _waitForNextLoop(self):
        tomorrow = datetime.datetime.now() + datetime.timedelta(1)
        midnight = datetime.datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, hour=0, minute=0,
                                     second=0)
        time.sleep((midnight - datetime.datetime.now()).seconds - 1)  # one second before midnight

    #todo: get rid of limits
    def Collect(self, brandsLimit=2000, reversed=False, nightly=False, howManyCycles=None):
        methodName = inspect.stack()[0][3]

        moduleLogger.info('%s - Started: %s' % (methodName, datetime.datetime.now().strftime("%d-%m-%Y %H:%M")))
        self.db.constructDBTables()

        #provide site identifiers - currently only allegro
        #TODO - check if they are present in the db
        self.db.insertSiteIdentifierToDatabase("allegro", 1)
        self.db.insertSiteIdentifierToDatabase("otomoto", 2)

        whileLoopCounter = 0
        while True:
            #TODO: this is obsolete as it is run by cron
            if nightly:
                self._waitForNextLoop()

            #todo: this should be a loop condition
            if howManyCycles is not None and whileLoopCounter >= howManyCycles:
                break

            if not reversed:
                startTime, newBrands, newLinks, newCars, endTime = self._collectNormalOtoMoto(brandsLimit)
                    # self._collectNormalAllegro(brandsLimit)
            else:
                startTime, newBrands, newLinks, newCars, endTime = \
                    self._collectReversedAllegro(brandsLimit)

            #TODO: old_links growing too much - check it
            #self.db.clearLinksOlderThanMonth()


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
    parser.add_argument("--reversed", required=False, action='store_true',
                        help='Start with parsing stored links insead of collecting new links.')
    parser.add_argument("--nightly", required=False, action='store_true',
                        help='Collect only once per night.')

    parser.add_argument("--howmanycycles", type=int, required=False, default=1,
                        help='Number of cycles')

    args = parser.parse_args()
    collector = CarDataCollector(args.database_name[0])
    collector.Collect(args.brands_limit, args.reversed, args.nightly, args.howmanycycles)

