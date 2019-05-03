import unittest
from OperationUtils.db_operations import DataBaseSchema, DataBase
from SiteModules.Allegro.AllegroBrandsCollector import AllegroBrandsCollector
from SiteModules.Allegro.AllegroCarsCollector import AllegroCarsCollector
from SiteModules.Allegro.AllegroLinksCollector import AllegroLinksCollector


class KeepOnCollectingWithExistingDatabase(unittest.TestCase):
    def setUp(self):
        self.dbSchema = DataBaseSchema()
        self.dbName = "crontest3 - Kopia.db"
        self.workingDatabase = DataBase(self.dbName)

    def run(self, result=None):
        if result.failures or result.errors:
            print "aborted"
        else:
            super(KeepOnCollectingWithExistingDatabase, self).run(result)

    def testContinueCollectingAllegro(self):
        workingDatabase = DataBase(self.dbName)
        brandsCollector = AllegroBrandsCollector(workingDatabase)
        numberOfBrands, brandsStartTime = brandsCollector.Collect(limit=1)
        self.assertGreaterEqual(numberOfBrands, 0)

        linksCollector = AllegroLinksCollector(workingDatabase)
        numberOfLinks, linksStartTime = linksCollector.Collect()
        self.assertGreaterEqual(numberOfLinks, 1)

        carsCollector = AllegroCarsCollector(workingDatabase)
        numberOfCars, carsStartTime = carsCollector.Collect()
        self.assertGreaterEqual(numberOfCars, 1)

        #assert time of collection is earlier than now

    def testAWorkingDatabaseHasCorrectSchema(self):
        workingDatabase = DataBase(self.dbName)
        #check tables
        for table in self.dbSchema.getEntireSchema():
            self.assertTrue(workingDatabase.tableExists(table.getName()), "table %s does not exist in the database" % table.getName())
            #check columns
            for columnName in table.getColumnsNames():
                self.assertTrue(workingDatabase.columnOfATableExists(columnName, table.getName()),
                                "Column %s is not present in table: %s" % (columnName, table.getName()))
        self.workingDatabase.conn.close()


if __name__ == "__main__":
    #COPY DB AND OPERATE ON COPY
    unittest.main(failfast=True)