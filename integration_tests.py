import unittest, os, datetime
from OperationUtils.db_operations import DataBase
from Collectors.BrandsCollector import BrandsCollector
from Collectors.LinksCollector import LinksCollector
from Collectors.CarsCollector import CarsCollector
from cars import CarDataCollector

class SeparateCollectorsTest(unittest.TestCase):
    def setUp(self):
        self.separateDBname = "separate_collectors_test.db"

        if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.separateDBname)):
            os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.separateDBname))

        self.database = DataBase(self.separateDBname)
        CarDataCollector.constructDBTables(self.database)

    def tearDown(self):
        del self.database
        os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.separateDBname))

    def testSeparateCollectors(self):
        brandsCollector = BrandsCollector(self.database)
        numberOfBrands, brandsStartTime = brandsCollector.Collect(limit=20)
        self.assertTrue(brandsCollector.db.valueIsPresentInColumnOfATable("Rover", "brandname", "cars_brand"))
        self.assertTrue(brandsCollector.db.valueIsPresentInColumnOfATable("Honda", "brandname", "cars_brand"))
        self.assertTrue(brandsCollector.db.valueIsPresentInColumnOfATable("Mercury", "brandname", "cars_brand"))
        self.assertLess((datetime.datetime.now() - brandsStartTime).total_seconds(), 240)

        #todo: inconsistency between brands limit and number of brands collected (models and version counted as brands)
        self.assertGreater(numberOfBrands, 20)
        self.assertGreater(brandsCollector.db.countRecordsInTable("cars_brand"), 20)
        #todo: by 1 error below
        self.assertEqual(brandsCollector.db.countRecordsInTable("cars_brand"), numberOfBrands)
        linksCollector = LinksCollector(self.database)
        numberOfLinks, linksStartTime = linksCollector.Collect(limit=100)
        self.assertFalse(linksCollector.db.valueIsPresentInColumnOfATable("True", "parsed", "links"))
        self.assertGreater(numberOfLinks, 100)
        self.assertEqual(linksCollector.db.countRecordsInTable("links"), numberOfLinks)
        self.assertLess((datetime.datetime.now() - linksStartTime).total_seconds(), 240)

        carsCollector = CarsCollector(self.database)
        numberOfCars, carsStartTime = carsCollector.Collect()
        self.assertGreater(numberOfCars, 0)
        self.assertLess(numberOfCars, numberOfLinks)
        self.assertEqual(carsCollector.db.countRecordsInTable("cars_car"), numberOfCars)
        self.assertLess((datetime.datetime.now() - carsStartTime).total_seconds(), 480)

class CombinedCollectorsTest(unittest.TestCase):
    def setUp(self):
        self.combinedDBname = "combined_collectors_test.db"

        if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.combinedDBname)):
            os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.combinedDBname))

    def tearDown(self):
        pass
        os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.combinedDBname))

    def testCombinedCollectors(self):
        collector = CarDataCollector(self.combinedDBname)
        collector.Collect(brandsLimit=20, linksLimit=100, howManyCycles=1)

        self.assertTrue(collector.db.valueIsPresentInColumnOfATable("Rover", "brandname", "cars_brand"))
        self.assertTrue(collector.db.valueIsPresentInColumnOfATable("Honda", "brandname", "cars_brand"))
        self.assertTrue(collector.db.valueIsPresentInColumnOfATable("Mercury", "brandname", "cars_brand"))

        self.assertGreater(collector.db.countRecordsInTable("cars_brand"), 20)
        self.assertGreater(collector.db.countRecordsInTable("links"), 100)
        self.assertGreater(collector.db.countRecordsInTable("invalidlinks"), 0)
        self.assertGreater(collector.db.countRecordsInTable("cars_car"), 100)

        self.assertEqual(collector.db.countRecordsInTable("collectcycle"), 1)


if __name__ == "__main__":
    unittest.main()