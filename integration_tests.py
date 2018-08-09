import datetime
from OperationUtils.db_operations import DataBase
from Collectors.BrandsCollector import BrandsCollector
from Collectors.LinksCollector import LinksCollector
from Collectors.CarsCollector import CarsCollector
from cars import CarDataCollector
from unit_tests import *


class DatabaseCreationTest(unittest.TestCase):
    def setUp(self):
        self.db = "database_creation_test.db"
        if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.separateDBname)):
            os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.separateDBname))

        self.database = DataBase(self.db)
    def testCreateTables(self):
        self.database.constructDBTables()
        self.assertTrue(self.database.tableExists('cars_brand'))
        self.assertTrue(self.database.tableExists('links'))
        self.assertTrue(self.database.tableExists('oldlinks'))
        self.assertTrue(self.database.tableExists('cars_car'))
        self.assertTrue(self.database.tableExists('invalidlinks'))
        self.assertTrue(self.database.tableExists('collectcycle'))

    def tearDown(self):
        del self.database
        if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.separateDBname)):
            os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.separateDBname))


class DatabaseInsertionTest(unittest.TestCase):
    def setUp(self):
        self.db = "database_insertion_test.db"
        if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.db)):
            os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.db))

        self.database = DataBase(self.db)
        self.database.constructDBTables()

    def testInsertions(self):
        self.database.insertBrandToDatabase(1, "BMW", "testlink1.com")
        self.database.insertModelToDatabase(2, "BMW", "5", "testlink2.com")
        self.database.insertVersionToDatabase(3, "BMW", "5", "e60", "testlink3.com")

        self.database.insertLinkToDatabase(1, 1, "testlink.com")
        self.database.insertInvalidLinkToDatabase(2, "testlink.com")

        cardict = {
            "b_id": 1,
            "l_id": 1,
            "rok produkcji:": '1988',
            "przebieg (km):": '168000',
            "moc (km):": '192',
            "pojemnosc silnika (cm3):": '2500',
            "rodzaj paliwa:": "benzyna",
            "kolor:": "szary",
            "stan:": "uzywany",
            "liczba drzwi:": "4/5",
            "skrzynia biegow:": "automatic",
            "cena": 29000,

        }
        self.database.insertAllegroCarToDatabase(1, 1, cardict)
        self.database.insertCollectCycleToDatabase(datetime.datetime.now(), datetime.datetime.now(),
                                                   datetime.datetime.now(), datetime.datetime.now(), 1, 1, 1)

        self.assertEqual(self.database.countRecordsInTable("cars_brand"), 3)
        self.assertEqual(self.database.getAmountOfBrands(), 3)
        self.assertEqual(self.database.getMaxFromColumnInTable("b_id", "cars_brand"), 3)
        allBrands = list(self.database.readAllBrands())
        self.assertEqual(len(allBrands), 3)

        self.assertEqual(self.database.countRecordsInTable("links"), 1)
        self.assertEqual(self.database.getAmountOfLinks(), 1)
        unparsedLinks = list(self.database.readAllUnparsedLinks())
        self.assertEqual(len(unparsedLinks), 1)

        self.assertEqual(self.database.countRecordsInTable("invalidlinks"), 1)
        self.assertEqual(self.database.countRecordsInTable("cars_car"), 1)
        self.assertEqual(self.database.countRecordsInTable("collectcycle"), 1)

        self.assertTrue(self.database.brandNameIsPresentInDatabase("BMW"))
        self.assertTrue(self.database.modelNameIsPresentInDatabase("5"))
        self.assertTrue(self.database.versionIsPresentInDatabase("e60"))

        self.assertTrue(self.database.brandLinkIsPresentInDatabase("testlink1.com"))
        self.assertTrue(self.database.brandLinkIsPresentInDatabase("testlink2.com"))
        self.assertTrue(self.database.brandLinkIsPresentInDatabase("testlink3.com"))

        self.assertTrue(self.database.thereAreOnlyUnparsedLinksInTheTable())
        self.assertFalse(self.database.thereAreParsedLinksInTheTable())

        self.database.updateParsedParameterForLinkWithId(1)

        self.assertTrue(self.database.thereAreParsedLinksInTheTable())
        self.assertTrue(self.database.thereAreOnlyParsedLinksInTheTable())

    def tearDown(self):
        del self.database
        if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.db)):
            os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.db))

class SeparateCollectorsTest(unittest.TestCase):
    def setUp(self):
        self.separateDBname = "separate_collectors_test.db"

        if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.separateDBname)):
            os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.separateDBname))

        self.database = DataBase(self.separateDBname)
        self.database.constructDBTables()

    def tearDown(self):
        del self.database
        if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.separateDBname)):
            os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.separateDBname))

    def testSeparateCollectors(self):
        #todo: test values in db - too many unknowns in color
        brandsCollector = BrandsCollector(self.database)
        numberOfBrands, brandsStartTime = brandsCollector.Collect(limit=20)
        self.assertTrue(brandsCollector.db.brandNameIsPresentInDatabase("Rover"))
        self.assertTrue(brandsCollector.db.brandNameIsPresentInDatabase("Honda"))
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
        self.assertGreater(numberOfLinks, 50)
        self.assertEqual(linksCollector.db.countRecordsInTable("links"), numberOfLinks)
        self.assertLess((datetime.datetime.now() - linksStartTime).total_seconds(), 500)

        carsCollector = CarsCollector(self.database)
        numberOfCars, carsStartTime = carsCollector.Collect()
        self.assertGreater(numberOfCars, 0)
        self.assertLessEqual(numberOfCars, numberOfLinks)
        self.assertEqual(carsCollector.db.countRecordsInTable("cars_car"), numberOfCars)

        self.assertTrue(carsCollector.db.thereAreOnlyParsedLinksInTheTable())

        self.assertLess((datetime.datetime.now() - carsStartTime).total_seconds(), 900)

class CombinedCollectorsTest(unittest.TestCase):
    def setUp(self):
        self.combinedDBname = "combined_collectors_test.db"

        if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.combinedDBname)):
            os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.combinedDBname))

    def tearDown(self):
        if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.separateDBname)):
            os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.separateDBname))

    def testCombinedCollectors(self):
        collector = CarDataCollector(self.combinedDBname)
        collector.Collect(brandsLimit=20, linksLimit=100, howManyCycles=1)

        self.assertTrue(collector.db.brandNameIsPresentInDatabase("Rover"))
        self.assertTrue(collector.db.brandNameIsPresentInDatabase("Honda"))
        self.assertTrue(collector.db.modelNameIsPresentInDatabase("Accord"))
        self.assertTrue(collector.db.modelNameIsPresentInDatabase("Civic"))
        self.assertTrue(collector.db.modelNameIsPresentInDatabase("75"))
        self.assertTrue(collector.db.versionIsPresentInDatabase("V (1993-1998)"))

        self.assertGreater(collector.db.countRecordsInTable("cars_brand"), 20)
        self.assertGreater(collector.db.countRecordsInTable("links"), 50)
        self.assertGreaterEqual(collector.db.countRecordsInTable("invalidlinks"), 0)
        self.assertGreater(collector.db.countRecordsInTable("cars_car"), 50)

        self.assertTrue(collector.db.thereAreOnlyParsedLinksInTheTable())

        self.assertEqual(collector.db.countRecordsInTable("collectcycle"), 1)


if __name__ == "__main__":
    unittest.main()