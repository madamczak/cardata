import unittest, os, datetime
from OperationUtils.db_operations import DataBase
from Collectors.BrandsCollector import BrandsCollector
from Collectors.LinksCollector import LinksCollector
from Collectors.CarsCollector import CarsCollector
from cars import CarDataCollector
from unit_tests import *
import time

class SeparateCollectorsTest(unittest.TestCase):
    def setUp(self):
        self.separateDBname = "separate_collectors_test.db"

        if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.separateDBname)):
            os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.separateDBname))

        self.database = DataBase(self.separateDBname)
        self.database.constructDBTables()

    def tearDown(self):
        del self.database
        os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.separateDBname))

    def testSeparateCollectors(self):
        brandsCollector = BrandsCollector(self.database)
        numberOfBrands, brandsStartTime = brandsCollector.Collect(limit=20)
        self.assertTrue(brandsCollector.db.brandNameIsPresentInDatabase("Rover"))
        self.assertTrue(brandsCollector.db.brandNameIsPresentInDatabase("Honda"))
        self.assertTrue(brandsCollector.db.brandNameIsPresentInDatabase("Mercury"))
        self.assertTrue(brandsCollector.db.modelNameIsPresentInDatabase("Accord"))
        self.assertTrue(brandsCollector.db.modelNameIsPresentInDatabase("Civic"))
        self.assertTrue(brandsCollector.db.modelNameIsPresentInDatabase("75"))
        self.assertTrue(brandsCollector.db.versionIsPresentInDatabase("V (1993-1998)"))
        self.assertLess((datetime.datetime.now() - brandsStartTime).total_seconds(), 500)

        #todo: inconsistency between brands limit and number of brands collected (models and version counted as brands)
        self.assertGreater(numberOfBrands, 20)
        self.assertGreater(brandsCollector.db.countRecordsInTable("cars_brand"), 20)
        #todo: by 1 error below
        self.assertEqual(brandsCollector.db.countRecordsInTable("cars_brand"), numberOfBrands)
        linksCollector = LinksCollector(self.database)
        numberOfLinks, linksStartTime = linksCollector.Collect(limit=100)
        self.assertFalse(linksCollector.db.thereAreParsedLinksInTheTable())
        self.assertGreater(numberOfLinks, 100)
        self.assertEqual(linksCollector.db.countRecordsInTable("links"), numberOfLinks)
        self.assertLess((datetime.datetime.now() - linksStartTime).total_seconds(), 500)

        carsCollector = CarsCollector(self.database)
        before = time.time()
        numberOfCars, carsStartTime = carsCollector.Collect()
        self.assertGreater(numberOfCars, 0)
        self.assertLess(numberOfCars, numberOfLinks)
        self.assertEqual(carsCollector.db.countRecordsInTable("cars_car"), numberOfCars)

        self.assertTrue(carsCollector.db.thereAreOnlyParsedLinksInTheTable())

        self.assertLess((datetime.datetime.now() - carsStartTime).total_seconds(), 900)

class CombinedCollectorsTest(unittest.TestCase):
    def setUp(self):
        self.combinedDBname = "combined_collectors_test.db"

        if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.combinedDBname)):
            os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.combinedDBname))

    def tearDown(self):
        os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.combinedDBname))

    def testCombinedCollectors(self):
        collector = CarDataCollector(self.combinedDBname)
        collector.Collect(brandsLimit=20, linksLimit=100, howManyCycles=1)

        self.assertTrue(collector.db.brandNameIsPresentInDatabase("Rover"))
        self.assertTrue(collector.db.brandNameIsPresentInDatabase("Honda"))
        self.assertTrue(collector.db.brandNameIsPresentInDatabase("Mercury"))
        self.assertTrue(collector.db.modelNameIsPresentInDatabase("Accord"))
        self.assertTrue(collector.db.modelNameIsPresentInDatabase("Civic"))
        self.assertTrue(collector.db.modelNameIsPresentInDatabase("75"))
        self.assertTrue(collector.db.versionIsPresentInDatabase("V (1993-1998)"))

        self.assertGreater(collector.db.countRecordsInTable("cars_brand"), 20)
        self.assertGreater(collector.db.countRecordsInTable("links"), 100)
        self.assertGreater(collector.db.countRecordsInTable("invalidlinks"), 0)
        self.assertGreater(collector.db.countRecordsInTable("cars_car"), 50)

        self.assertTrue(collector.db.thereAreOnlyParsedLinksInTheTable())

        self.assertEqual(collector.db.countRecordsInTable("collectcycle"), 1)


if __name__ == "__main__":
    unittest.main()