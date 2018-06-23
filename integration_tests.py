import unittest, os

import datetime
from OperationUtils.db_operations import DataBase
from Collectors.BrandsCollector import BrandsCollector
from Collectors.LinksCollector import LinksCollector
from Collectors.CarsCollector import CarsCollector
from cars import CarDataCollector

class CollectBrandsTest(unittest.TestCase):
    def setUp(self):
        self.dbName = "integration_test.db"
        self.database = DataBase(self.dbName)
        CarDataCollector.constructDBTables(self.database)

    def tearDown(self):
        del self.database
        os.remove("C:\\Users\\asd\\PycharmProjects\\cardata\\" + self.dbName)

    def testBrandsCollection(self):
        brandsCollector = BrandsCollector(self.dbName)
        numberOfBrands = brandsCollector.Collect(limit=20)
        self.assertTrue(brandsCollector.db.valueIsPresentInColumnOfATable("Rover", "brandname", "cars_brand"))
        self.assertTrue(brandsCollector.db.valueIsPresentInColumnOfATable("Honda", "brandname", "cars_brand"))
        self.assertTrue(brandsCollector.db.valueIsPresentInColumnOfATable("Mercury", "brandname", "cars_brand"))

        #todo: inconsistency between brands limit and number of brands collected (models and version counted as brands)
        self.assertGreater(numberOfBrands, 20)
        self.assertGreater(brandsCollector.db.countRecordsInTable("cars_brand"), 20)
        #todo: by 1 error below
        self.assertEqual(brandsCollector.db.countRecordsInTable("cars_brand"), numberOfBrands)
        linksCollector = LinksCollector("integration_test.db")
        numberOfLinks = linksCollector.Collect(limit=100)
        self.assertFalse(linksCollector.db.valueIsPresentInColumnOfATable("True", "parsed", "links"))
        self.assertGreater(numberOfLinks, 100)
        self.assertEqual(linksCollector.db.countRecordsInTable("links"), numberOfLinks)

        carsCollector = CarsCollector(self.dbName)
        numberOfCars = carsCollector.Collect()
        self.assertGreater(numberOfCars, 0)
        self.assertLess(numberOfCars, numberOfLinks)
        self.assertEqual(carsCollector.db.countRecordsInTable("cars_car"), numberOfCars)

if __name__ == "__main__":
    unittest.main()