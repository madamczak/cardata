import datetime

from OperationUtils.url_operations import URLOperations
from Collectors.BrandsCollector import BrandsCollector
from Collectors.LinksCollector import LinksCollector
from Collectors.CarsCollector import CarsCollector
from cars import CarDataCollector
from unit_tests import *

def _deleteDatabaseIfExists(dbName):
    if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), dbName)):
        os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), dbName))

class WebsiteParsingTest(unittest.TestCase):
    def testGettingAllBrands(self):
        topLink = "https://allegro.pl/kategoria/samochody-osobowe-4029"
        modelLink = "https://allegro.pl/kategoria/osobowe-volkswagen-4055"
        versionLink = "https://allegro.pl/kategoria/passat-b6-2005-2010-12764"
        #top
        allBrands = URLOperations.getAllBrands(topLink)

        self.assertTrue(u'Rover' in allBrands.keys())
        self.assertTrue("https://allegro.pl/kategoria/osobowe-rover-4048" in allBrands.values())

        self.assertTrue(u'Honda' in allBrands.keys())
        self.assertTrue(u'Porsche' in allBrands.keys())
        self.assertTrue(u'Mercedes-Benz' in allBrands.keys())

        self.assertTrue(u'Volkswagen' in allBrands.keys())
        self.assertTrue("https://allegro.pl/kategoria/osobowe-volkswagen-4055" in allBrands.values())

        self.assertTrue(u'Alfa Romeo' in allBrands.keys())
        self.assertTrue(u'Dacia' in allBrands.keys())
        self.assertTrue(u'Hyundai' in allBrands.keys())
        self.assertTrue(u'Ford' in allBrands.keys())
        self.assertTrue(u'Mazda' in allBrands.keys())
        self.assertTrue(u'BMW' in allBrands.keys())
        self.assertTrue(u'Peugeot' in allBrands.keys())
        self.assertTrue(u'Renault' in allBrands.keys())
        self.assertTrue(u'Volvo' in allBrands.keys())
        self.assertTrue(u'Citroen' in allBrands.keys())
        self.assertTrue(u'Seat' in allBrands.keys())
        self.assertTrue(u'Audi' in allBrands.keys())
        #model
        allModels = URLOperations.getAllBrands(modelLink)
        self.assertTrue(u'Passat' in allModels.keys())
        self.assertTrue("https://allegro.pl/kategoria/volkswagen-passat-12710" in allModels.values())
        #version
        allVersions = URLOperations.getAllBrands(versionLink)
        self.assertTrue(u'B7 (2010-2014)' in allVersions.keys())
        self.assertTrue("https://allegro.pl/kategoria/passat-b7-2010-2014-110751" in allVersions.values())

    def testLinksFromCategorySite(self):
        lastWeeke60Links = URLOperations.getLinksFromCategorySite(
            "https://allegro.pl/kategoria/seria-5-e60-2003-2010-18083")
        alle60Links = URLOperations.getLinksFromCategorySite(
            "https://allegro.pl/kategoria/seria-5-e60-2003-2010-18083", startTimeParameter=None)

        lastWeek5SeriesLinks = URLOperations.getLinksFromCategorySite(
            "https://allegro.pl/kategoria/bmw-seria-5-12437")

        self.assertGreater(len(lastWeeke60Links), 0)
        self.assertGreater(len(alle60Links), len(lastWeeke60Links))
        for link in lastWeeke60Links:
            self.assertTrue(link in lastWeek5SeriesLinks)

    def testParseAllegroSite(self):
        lastWeeke60Links = URLOperations.getLinksFromCategorySite(
            "https://allegro.pl/kategoria/seria-5-e60-2003-2010-18083")

        keys = ["rok produkcji:", "przebieg:", "moc:", "pojemnosc silnika:", "cena"] #most important

        for link in lastWeeke60Links[:10]:
            carDict = URLOperations.parseAllegroSite(link)

            for key in keys:
                self.assertTrue(key in carDict.keys(), msg="Missing key: %s" % key)

            self.assertGreaterEqual(carDict.get("cena"), 0)

            self.assertGreaterEqual(int(carDict.get("rok produkcji:")), 1950)
            self.assertLessEqual(int(carDict.get("rok produkcji:")), datetime.date.today().year)

            self.assertGreaterEqual(int(DataCleaning.stripDecimalValue(carDict.get("przebieg:"))), 0)
            self.assertLessEqual(int(DataCleaning.stripDecimalValue(carDict.get("przebieg:"))), 10000000)

class DatabaseCreationTest(unittest.TestCase):
    def setUp(self):
        self.db = "database_creation_test.db"
        _deleteDatabaseIfExists(self.db)
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
        _deleteDatabaseIfExists(self.db)

class DatabaseInsertionTest(unittest.TestCase):
    def setUp(self):
        self.db = "database_insertion_test.db"
        _deleteDatabaseIfExists(self.db)

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
        _deleteDatabaseIfExists(self.db)

class SeparateCollectorsTest(unittest.TestCase):
    def setUp(self):
        self.separateDBname = "separate_collectors_test.db"

        _deleteDatabaseIfExists(self.separateDBname)

        self.database = DataBase(self.separateDBname)
        self.database.constructDBTables()

    def tearDown(self):
        del self.database
        _deleteDatabaseIfExists(self.separateDBname)

    def testSeparateCollectors(self):
        brandsCollector = BrandsCollector(self.database)
        numberOfBrands, brandsStartTime = brandsCollector.Collect(limit=20)
        self.assertTrue(brandsCollector.db.brandNameIsPresentInDatabase("Rover"))
        self.assertTrue(brandsCollector.db.brandNameIsPresentInDatabase("Honda"))
        self.assertTrue(brandsCollector.db.modelNameIsPresentInDatabase("Accord"))
        self.assertTrue(brandsCollector.db.modelNameIsPresentInDatabase("Civic"))
        self.assertTrue(brandsCollector.db.modelNameIsPresentInDatabase("75"))
        self.assertTrue(brandsCollector.db.versionIsPresentInDatabase("V (1993-1998)"))
        self.assertLess((datetime.datetime.now() - brandsStartTime).total_seconds(), 500)
        self.assertGreater(numberOfBrands, 20)
        self.assertGreater(brandsCollector.db.countRecordsInTable("cars_brand"), 20)
        self.assertEqual(brandsCollector.db.countRecordsInTable("cars_brand"), numberOfBrands)
        linksCollector = LinksCollector(self.database)
        numberOfLinks, linksStartTime = linksCollector.Collect()
        self.assertFalse(linksCollector.db.thereAreParsedLinksInTheTable())
        self.assertGreater(numberOfLinks, 10)
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
        _deleteDatabaseIfExists(self.combinedDBname)

    def tearDown(self):
        _deleteDatabaseIfExists(self.combinedDBname)

    def testCombinedCollectors(self):
        collector = CarDataCollector(self.combinedDBname)
        collector.Collect(brandsLimit=20, howManyCycles=1)

        self.assertTrue(collector.db.brandNameIsPresentInDatabase("Rover"))
        self.assertTrue(collector.db.brandNameIsPresentInDatabase("Honda"))
        self.assertTrue(collector.db.modelNameIsPresentInDatabase("Accord"))
        self.assertTrue(collector.db.modelNameIsPresentInDatabase("Civic"))
        self.assertTrue(collector.db.modelNameIsPresentInDatabase("75"))
        self.assertTrue(collector.db.versionIsPresentInDatabase("V (1993-1998)"))

        self.assertGreater(collector.db.countRecordsInTable("cars_brand"), 20)
        self.assertGreater(collector.db.countRecordsInTable("links"), 10)
        self.assertGreaterEqual(collector.db.countRecordsInTable("invalidlinks"), 0)
        self.assertGreater(collector.db.countRecordsInTable("cars_car"), 10)

        self.assertTrue(collector.db.thereAreOnlyParsedLinksInTheTable())

        self.assertEqual(collector.db.countRecordsInTable("collectcycle"), 1)

class CollectedDataTest(unittest.TestCase):
    def setUp(self):
        self.collectedDataDB = "collected_data_test.db"
        _deleteDatabaseIfExists(self.collectedDataDB)

    def tearDown(self):
        _deleteDatabaseIfExists(self.collectedDataDB)

    def testCollectedData(self):
        collector = CarDataCollector(self.collectedDataDB)
        collector.Collect(brandsLimit=20, howManyCycles=1)

        allCars = collector.db.getAllCars()
        self.assertTrue(all([car[2] != 0 for car in allCars]))#year

        for car in allCars:
            self.assertGreaterEqual(car[2], 1886)   # 1886 - invention of car
            self.assertLessEqual(car[2], datetime.date.today().year)

        self.assertFalse(all([car[3] == 0 for car in allCars]))  # mileage
        self.assertFalse(all([car[4] == 0 for car in allCars]))  # power
        self.assertFalse(all([car[5] == 0 for car in allCars]))   # capacity
        self.assertFalse(all([car[6] == u'unknown' for car in allCars]))  # fuel type
        self.assertFalse(all([car[7] == u'unknown' for car in allCars]))  # color
        self.assertFalse(all([car[8] == u'unknown' for car in allCars]))  # state
        self.assertFalse(all([car[9] == u'unknown' for car in allCars]))  # doors
        self.assertFalse(all([car[10] == u'unknown' for car in allCars]))  # gearbox
        self.assertFalse(all([car[10] == 0 for car in allCars]))  # price

class MoreThanOneCycleTest(unittest.TestCase):
    def setUp(self):
        self.dbname = "morethanonecycle_collectors_test.db"
        _deleteDatabaseIfExists(self.dbname)

    def tearDown(self):
        _deleteDatabaseIfExists(self.dbname)

    def testTripleCycle(self):
        collector = CarDataCollector(self.dbname)
        collector.Collect(brandsLimit=20, howManyCycles=3)
        self.assertEqual(collector.db.countRecordsInTable("collectcycle"), 3)
        self.assertEqual(collector.db.countRecordsInTable("cars_brand"), collector.db.getAmountOfBrands())
        self.assertEqual(collector.db.countRecordsInTable("links"), collector.db.getAmountOfLinks())


if __name__ == "__main__":
    unittest.main()
