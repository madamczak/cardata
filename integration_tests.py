import unittest

import os
from mock import patch
from cars import ConstructBrandsTable, constructDBTables, constructLinkTable, ConstructCarsTable
import datetime
from OperationUtils.db_operations import DataBase
from OperationUtils.data_operations import GEARBOXWORDSDICT, FUELWORDSDICT, COLORWORDSDICT, STATEWORDSDICT, \
    DataCleaning


class DBCreation(unittest.TestCase):
    def setUp(self):
        self.newDb = DataBase("integration_test.db")

    def testDataCollection(self):
        #Tables
        constructDBTables(self.newDb)
        self.assertTrue(self.newDb.tableExists("Brands"))
        self.assertTrue(self.newDb.tableExists("Links"))
        self.assertTrue(self.newDb.tableExists("InvalidLinks"))
        self.assertTrue(self.newDb.tableExists("CarData"))

        #Brands
        newBrands = ConstructBrandsTable(self.newDb)
        self.assertGreater(newBrands, 1300)

        brandIds = []
        for brand in self.newDb.readAllDataGenerator("Brands", amount=1500):
            self.assertTrue(brand[0] != 0)
            self.assertTrue(brand[0] not in brandIds)
            brandIds.append(brand[0])
            self.assertTrue(brand[1] != "")

            self.assertTrue(brand[4] != "")
            self.assertTrue("kategoria" in brand[4])
            # assert that brand name or model name is in the link

            # if not DataCleaning.normalize(brand[1]) in str(brand[4]):
            #     if brand[1] is not None:
            #         self.assertTrue(DataCleaning.normalize(brand[2]) in str(brand[4]))
            #     else:
            #         # brand name not in link
            #         self.assertTrue(False)

        self.assertTrue(self.newDb.valueIsPresentInColumnOfATable("Civic", "modelName", "Brands"))
        self.assertTrue(self.newDb.valueIsPresentInColumnOfATable("VIII (2006-2011)", "version", "Brands"))

        newLinks = constructLinkTable(self.newDb, limit=2000)

        # 3000 because number of links is decided per category.
        # If there is 1999 links read from previous categories and
        # next one will contain 2 links the number of new links will be 2001, not 2000.
        # Therefore I assume 3000 is enough, or is it?
        self.assertLess(newLinks, 3000)

        wrongCount = 0
        for link in self.newDb.readAllDataGenerator("Links", amount=3000):
            self.assertTrue(link[4] == "False")
            #TODO assert that time of link collection is no longer that 15minutes

            #assert that brand name is in the link
            brandInfo = self.newDb.getBrandInfo(link[1])
            if not brandInfo[0] in link[3]:
                if len(brandInfo) >= 2 and not brandInfo[1] in link[3]:
                    wrongCount += 1

            if wrongCount > 20: #around 1% of links amount
                self.assertTrue(False)


        newCars = ConstructCarsTable(self.newDb, limit=2000)
        self.assertGreater(newCars, 1500)

        for car in self.newDb.readAllDataGenerator("CarData", amount=2000):
            self.assertGreater(car[2], 1900)
            self.assertLess(car[2], datetime.datetime.now().year + 1)

            self.assertGreater(car[3], 0)
            self.assertGreater(car[4], 0)
            self.assertGreater(car[5], 0)

            self.assertIn(car[6], FUELWORDSDICT.values())
            self.assertIn(car[7], COLORWORDSDICT.values())
            self.assertIn(car[10], GEARBOXWORDSDICT.values())
            self.assertGreater(car[11], 0)
            self.assertLess(car[11], 10000000)
            #TODO assert that time of car collection is no longer that 15minutes

        # assert that InvalidLinks table contains 2000 - numberOfnewCars values
        self.assertAlmostEquals(self.newDb.countRecordsInTable("InvalidLinks"), 2000-newCars, delta=5)



    def tearDown(self):
        del self.newDb
        #self.addCleanup(os.remove, "integration_test.db")

if __name__ == "__main__":
    unittest.main()