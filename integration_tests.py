import datetime

from OperationUtils.db_operations import DataBaseSchema
from SiteModules.Allegro.AllegroUrlOperations import AllegroURLOperations
from SiteModules.OtoMoto.OtoMotoUrlOperations import OtoMotoURLOperations

from SiteModules.Allegro.AllegroBrandsCollector import AllegroBrandsCollector
from SiteModules.Allegro.AllegroLinksCollector import AllegroLinksCollector
from SiteModules.Allegro.AllegroCarsCollector import AllegroCarsCollector
from cars import CarDataCollector
from unit_tests import *
import requests

def _deleteDatabaseIfExists(dbName):
    if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), dbName)):
        os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), dbName))

class OtoMotoWebsiteParsingTest(unittest.TestCase):
    def testParseOtoMotoSite(self):
        lastWeeke60Links = OtoMotoURLOperations.getLinksFromCategorySite(
            "https://www.otomoto.pl/osobowe/bmw/seria-5/e60-2003-2010")

        keys = ["Rok produkcji", "Przebieg", "price"] #most important

        for link in lastWeeke60Links[:10]:
            carDict = OtoMotoURLOperations.parseOtomotoSite(link)

            for key in keys:
                self.assertTrue(key in carDict.keys(), msg="Missing key: %s" % key)

            self.assertGreaterEqual(carDict.get("price"), 0)

            self.assertGreaterEqual(int(carDict.get("Rok produkcji")), 2003)
            self.assertLessEqual(int(carDict.get("Rok produkcji")), 2010)

            self.assertGreaterEqual(int(DataCleaning.stripDecimalValue(carDict.get("Przebieg"))), 0)
            self.assertLessEqual(int(DataCleaning.stripDecimalValue(carDict.get("Przebieg"))), 10000000)

            self.assertNotEqual(carDict.get("location"), None)
            self.assertEqual(carDict.get("currency"), "PLN")

            #todo: date

    def testNumberOfPagesInCategorySite(self):
        model = OtoMotoURLOperations.getNumberOfPagesInBrandCategory("https://www.otomoto.pl/osobowe/bmw/seria-5/")
        version = OtoMotoURLOperations.getNumberOfPagesInBrandCategory("https://www.otomoto.pl/osobowe/bmw/seria-5/e60-2003-2010")
        self.assertGreater(model, version)

        zeroPages = OtoMotoURLOperations.getNumberOfPagesInBrandCategory("https://www.otomoto.pl/osobowe/aro/")
        self.assertEqual(zeroPages, 0)

    def testLinksFromCategorySite(self):
        alle60Links = OtoMotoURLOperations.getLinksFromCategorySite(
            "https://www.otomoto.pl/osobowe/bmw/seria-5/e60-2003-2010/")

        all5SeriesLinks = OtoMotoURLOperations.getLinksFromCategorySite(
            "https://www.otomoto.pl/osobowe/bmw/seria-5/")

        self.assertGreater(len(all5SeriesLinks), len(alle60Links))

    def testBrandMatchingForOtomoto(self):
        testDB = DataBase("UnitTests/test.db")
        matchDictionary = OtoMotoURLOperations.getAllBrandsMatch(testDB)
        self.assertEquals(len(matchDictionary.keys()), 5)
        self.assertTrue(25 in matchDictionary.keys())
        self.assertTrue(27 in matchDictionary.keys())
        self.assertTrue(45 in matchDictionary.keys())
        self.assertTrue(46 in matchDictionary.keys())
        self.assertTrue(47 in matchDictionary.keys())

        for linkValue in matchDictionary.values():
            response = requests.get(linkValue)
            self.assertFalse(response.history)


    def testBrandMatchingForOtomotoWrongDB(self):
        testDB = ""
        matchDictionary = OtoMotoURLOperations.getAllBrandsMatch(testDB)
        self.assertEquals(len(matchDictionary.keys()), 0)


class AllegroWebsiteParsingTest(unittest.TestCase):
    def testGettingAllBrands(self):
        topLink = "https://allegro.pl/kategoria/samochody-osobowe-4029"
        modelLink = "https://allegro.pl/kategoria/osobowe-volkswagen-4055"
        versionLink = "https://allegro.pl/kategoria/passat-b6-2005-2010-12764"
        #top
        allBrands = AllegroURLOperations.getAllBrands(topLink)

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
        self.assertTrue(u'SEAT' in allBrands.keys())
        self.assertTrue(u'Audi' in allBrands.keys())
        #model
        allModels = AllegroURLOperations.getAllBrands(modelLink)
        self.assertTrue(u'Passat' in allModels.keys())
        self.assertTrue("https://allegro.pl/kategoria/volkswagen-passat-12710" in allModels.values())
        #version
        allVersions = AllegroURLOperations.getAllBrands(versionLink)
        self.assertTrue(u'B7 (2010-2014)' in allVersions.keys())
        self.assertTrue("https://allegro.pl/kategoria/passat-b7-2010-2014-110751" in allVersions.values())

    def testLinksFromCategorySite(self):
        lastWeeke60Links = AllegroURLOperations.getLinksFromCategorySite(
            "https://allegro.pl/kategoria/seria-5-e60-2003-2010-18083")
        alle60Links = AllegroURLOperations.getLinksFromCategorySite(
            "https://allegro.pl/kategoria/seria-5-e60-2003-2010-18083", startTimeParameter=None)

        lastWeek5SeriesLinks = AllegroURLOperations.getLinksFromCategorySite(
            "https://allegro.pl/kategoria/bmw-seria-5-12437")

        self.assertGreater(len(lastWeeke60Links), 0)
        self.assertGreater(len(alle60Links), len(lastWeeke60Links))
        for link in lastWeeke60Links:
            self.assertTrue(link in lastWeek5SeriesLinks)

    def testParseAllegroSite(self):
        lastWeeke60Links = AllegroURLOperations.getLinksFromCategorySite(
            "https://allegro.pl/kategoria/seria-5-e60-2003-2010-18083")

        keys = ["rok produkcji:", "przebieg:", "moc:", "pojemnosc silnika:", "cena"] #most important

        sitesWithmissedKeys = 0
        for link in lastWeeke60Links[:10]:
            carDict = AllegroURLOperations.parseAllegroSite(link)

            for key in keys:
                if not key in carDict.keys():
                    sitesWithmissedKeys += 1
                    break

            self.assertGreaterEqual(carDict.get("cena"), 0)

            self.assertGreaterEqual(int(carDict.get("rok produkcji:")), 1950)
            self.assertLessEqual(int(carDict.get("rok produkcji:")), datetime.date.today().year)

            self.assertGreaterEqual(int(DataCleaning.stripDecimalValue(carDict.get("przebieg:"))), 0)
            self.assertLessEqual(int(DataCleaning.stripDecimalValue(carDict.get("przebieg:"))), 10000000)

        self.assertTrue(sitesWithmissedKeys < 5)


class DatabaseCreationTest(unittest.TestCase):
    def setUp(self):
        self.db = "database_creation_test.db"
        _deleteDatabaseIfExists(self.db)
        self.database = DataBase(self.db)
    def testCreateTables(self):
        self.database.constructDBTables()

        brand_table_name = "cars_brand"
        brands_columns = ["b_id", "brandname", "modelname", "version", "allegro_link", "otomoto_link"]

        links_table_name = "links"
        old_links_table_name = "old_links"
        links_columns = ["l_id", "b_id", "time", "link", "parsed", "site_id"]

        cars_table_name = "cars_car"
        cars_columns = ["b_id", "l_id", "year", "mileage", "power", "capacity", "power", "fuel", "color", "usedornew",
                        "gearbox", "doors", "location", "price", "time", "site_id"]

        invalid_links_table_name = "invalid_links"
        invalid_links_columns = ["l_id", "time", "link"]

        allegro_collect_cycle_table_name = 'allegro_collect_cycle'
        allegro_collect_cycle_columns = ["start_brands", "start_links", "start_cars",
                                         "end_time", "new_brands", "new_links", "new_cars"]

        site_id_table_name = 'site_identifiers'
        site_id_columns = ["name", "identifier"]

        self.assertTrue(self.database.tableExists(brand_table_name))
        for brands_column in brands_columns:
            self.assertTrue(self.database.columnOfATableExists(brands_column, brand_table_name))

        self.assertTrue(self.database.tableExists(links_table_name))
        for links_column in links_columns:
            self.assertTrue(self.database.columnOfATableExists(links_column, links_table_name))

        self.assertTrue(self.database.tableExists(old_links_table_name))
        for old_links_column in links_columns:
            self.assertTrue(self.database.columnOfATableExists(old_links_column, old_links_table_name))

        self.assertTrue(self.database.tableExists(cars_table_name))
        for cars_column in cars_columns:
            self.assertTrue(self.database.columnOfATableExists(cars_column, cars_table_name))

        self.assertTrue(self.database.tableExists(invalid_links_table_name))
        for invalid_links_column in invalid_links_columns:
            self.assertTrue(self.database.columnOfATableExists(invalid_links_column, invalid_links_table_name))

        self.assertTrue(self.database.tableExists(allegro_collect_cycle_table_name))
        for allegro_collect_cycle_column in allegro_collect_cycle_columns:
            self.assertTrue(self.database.columnOfATableExists(allegro_collect_cycle_column,
                                                               allegro_collect_cycle_table_name))

        self.assertTrue(self.database.tableExists(site_id_table_name))
        for site_id_column in site_id_columns:
            self.assertTrue(self.database.columnOfATableExists(site_id_column, site_id_table_name))
        #TODO: new tables/columns


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
        self.database.insertAllegroBrandToDatabase(1, "BMW", "testlink1.com")
        self.database.insertModelToDatabase(2, "BMW", "5", "testlink2.com")
        self.database.insertVersionToDatabase(3, "BMW", "5", "e60", "testlink3.com")

        self.database.insertLinkToDatabase(1, 1, 999, "testlink.com")
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
        self.database.insertAllegroCollectCycleToDatabase(datetime.datetime.now(), datetime.datetime.now(),
                                                          datetime.datetime.now(), datetime.datetime.now(), 1, 1, 1)

        self.database.insertSiteIdentifierToDatabase("allegro", 1)
        self.assertEqual(self.database.countRecordsInTable("site_identifiers"), 1)

        self.assertEqual(self.database.countRecordsInTable("cars_brand"), 3)
        self.assertEqual(self.database.getAmountOfBrands(), 3)
        self.assertEqual(self.database.getMaxFromColumnInTable("b_id", "cars_brand"), 3)
        allBrands = list(self.database.readAllBrands())
        self.assertEqual(len(allBrands), 3)

        self.assertEqual(self.database.countRecordsInTable("links"), 1)
        self.assertEqual(self.database.getAmountOfLinks(), 1)
        unparsedLinks = list(self.database.readAllUnparsedLinks())
        self.assertEqual(len(unparsedLinks), 1)

        self.assertEqual(self.database.countRecordsInTable("invalid_links"), 1)
        self.assertEqual(self.database.countRecordsInTable("cars_car"), 1)
        self.assertEqual(self.database.countRecordsInTable("allegro_collect_cycle"), 1)

        self.assertTrue(self.database.brandNameIsPresentInDatabase("BMW"))
        self.assertTrue(self.database.modelNameIsPresentInDatabase("5"))
        self.assertTrue(self.database.versionIsPresentInDatabase("e60"))

        self.assertTrue(self.database.allegroBrandLinkIsPresentInDatabase("testlink1.com"))
        self.assertTrue(self.database.allegroBrandLinkIsPresentInDatabase("testlink2.com"))
        self.assertTrue(self.database.allegroBrandLinkIsPresentInDatabase("testlink3.com"))

        self.assertTrue(self.database.thereAreOnlyUnparsedLinksInTheTable())
        self.assertFalse(self.database.thereAreParsedLinksInTheTable())

        self.database.updateParsedParameterForLinkWithId(1)

        self.assertTrue(self.database.thereAreParsedLinksInTheTable())
        self.assertTrue(self.database.thereAreOnlyParsedLinksInTheTable())

    def tearDown(self):
        del self.database
        _deleteDatabaseIfExists(self.db)


class AllegroSeparateCollectorsTest(unittest.TestCase):
    def setUp(self):
        self.separateDBname = "separate_collectors_test.db"

        _deleteDatabaseIfExists(self.separateDBname)

        self.database = DataBase(self.separateDBname)
        self.database.constructDBTables()

    def tearDown(self):
        del self.database
        _deleteDatabaseIfExists(self.separateDBname)

    def testSeparateCollectors(self):
        brandsCollector = AllegroBrandsCollector(self.database)
        numberOfBrands, brandsStartTime = brandsCollector.Collect(limit=20)
        self.assertTrue(brandsCollector.db.brandNameIsPresentInDatabase("Rover"))
        self.assertTrue(brandsCollector.db.brandNameIsPresentInDatabase("Honda"))
        self.assertTrue(brandsCollector.db.modelNameIsPresentInDatabase("Accord"))
        self.assertTrue(brandsCollector.db.modelNameIsPresentInDatabase("Civic"))
        self.assertTrue(brandsCollector.db.modelNameIsPresentInDatabase("75"))
        self.assertTrue(brandsCollector.db.versionIsPresentInDatabase("VII (2002-2008)"))
        self.assertLess((datetime.datetime.now() - brandsStartTime).total_seconds(), 500)
        self.assertGreater(numberOfBrands, 20)
        self.assertGreater(brandsCollector.db.countRecordsInTable("cars_brand"), 20)
        self.assertEqual(brandsCollector.db.countRecordsInTable("cars_brand"), numberOfBrands)
        linksCollector = AllegroLinksCollector(self.database)
        numberOfLinks, linksStartTime = linksCollector.Collect()
        self.assertFalse(linksCollector.db.thereAreParsedLinksInTheTable())
        self.assertGreaterEqual(numberOfLinks, 1)
        self.assertEqual(linksCollector.db.countRecordsInTable("links"), numberOfLinks)
        self.assertLess((datetime.datetime.now() - linksStartTime).total_seconds(), 500)

        carsCollector = AllegroCarsCollector(self.database)
        numberOfCars, carsStartTime = carsCollector.Collect()
        self.assertGreater(numberOfCars, 0)
        self.assertLessEqual(numberOfCars, numberOfLinks)
        self.assertEqual(carsCollector.db.countRecordsInTable("cars_car"), numberOfCars)

        self.assertTrue(carsCollector.db.thereAreOnlyParsedLinksInTheTable())

        self.assertLess((datetime.datetime.now() - carsStartTime).total_seconds(), 900)


class AllegroCombinedCollectorsTest(unittest.TestCase):
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
        self.assertTrue(collector.db.versionIsPresentInDatabase("VII (2002-2008)"))

        self.assertGreaterEqual(collector.db.countRecordsInTable("cars_brand"), 20)
        self.assertGreaterEqual(collector.db.countRecordsInTable("links"), 1)
        self.assertGreaterEqual(collector.db.countRecordsInTable("invalid_links"), 0)
        self.assertGreaterEqual(collector.db.countRecordsInTable("cars_car"), 1)

        self.assertTrue(collector.db.thereAreOnlyParsedLinksInTheTable())

        self.assertEqual(collector.db.countRecordsInTable("allegro_collect_cycle"), 1)


class AllegroCollectedDataTest(unittest.TestCase):
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


class AllegroMoreThanOneCycleTest(unittest.TestCase):
    def setUp(self):
        self.dbname = "morethanonecycle_collectors_test.db"
        _deleteDatabaseIfExists(self.dbname)

    def tearDown(self):
        _deleteDatabaseIfExists(self.dbname)

    def testTripleCycle(self):
        collector = CarDataCollector(self.dbname)
        collector.Collect(brandsLimit=20, howManyCycles=3)
        self.assertEqual(collector.db.countRecordsInTable("allegro_collect_cycle"), 3)
        self.assertEqual(collector.db.countRecordsInTable("cars_brand"), collector.db.getAmountOfBrands())
        self.assertEqual(collector.db.countRecordsInTable("links"), collector.db.getAmountOfLinks())


if __name__ == "__main__":
    unittest.main()
