import sqlite3

from OperationUtils.data_operations import DataCleaning
from OperationUtils.logger import Logger
import inspect
import datetime
import time


moduleLogger = Logger.setLogger("dbops")

class DataBase(object):
    def __init__(self, databaseName):
        self.dbName = databaseName
        self.conn = sqlite3.connect(databaseName)
        self.c = self.conn.cursor()
        moduleLogger.info("Connection to db: '%s' is set up." % databaseName)

    def __del__(self):
        self.c.close()
        self.conn.close()
        moduleLogger.info("Connection to db is closed.")

    def createTable(self, name, columnDict):
        methodName = inspect.stack()[0][3]

        command = "CREATE TABLE IF NOT EXISTS %s(" % name
        for item in columnDict.items():
            command += " %s %s," % item
        command = command[:-1] + ")"

        moduleLogger.debug("%s - Command: %s will be executed." % (methodName, command))
        self.c.execute(command)
        moduleLogger.debug("%s - Command: %s executed successfully." % (methodName, command))

    def insertStringData(self, tableName, stringData):
        methodName = inspect.stack()[0][3]

        command = "INSERT INTO %s VALUES(%s)" % (tableName, stringData)
        moduleLogger.debug("%s - Command: %s will be executed." % (methodName, command))
        self.c.execute(command)
        self.conn.commit()
        moduleLogger.debug("%s - Command: %s executed successfully." % (methodName, command))

    def insertLinkToDatabase(self, linkId, brandId, link):
        moduleLogger.debug("Inserting link: %s." % link)
        s = """ %d, %d, "%s", "%s", "%r" """ % (linkId, brandId, str(datetime.datetime.now()), link, False)
        self.insertStringData("links", s)

    def insertInvalidLinkToDatabase(self, linkId, link):
        moduleLogger.debug("Inserting invalid link: %s." % link)
        s = """ "%d", "%s", "%s" """ % (linkId, str(datetime.datetime.now()), link)
        self.insertStringData("invalidlinks", s)

    def insertBrandToDatabase(self, brandId, brandName, link):
        moduleLogger.debug("Inserting brand: %s." % brandName)
        s = """%d, "%s", NULL, NULL, "%s" """ % (brandId, brandName, link)
        self.insertStringData("cars_brand", s)

    def insertModelToDatabase(self, brandId, brandName, modelName, link):
        moduleLogger.debug("Inserting model: %s - %s." % (brandName, modelName))
        s = """%d, "%s", "%s", NULL, "%s" """ % (brandId, brandName, modelName, link)
        self.insertStringData("cars_brand", s)

    def insertVersionToDatabase(self, brandId, brandName, modelName, versionName, link):
        s = """%d, "%s", "%s", "%s", "%s" """ % (brandId, brandName, modelName, versionName, link)
        moduleLogger.debug("Inserting version: %s - %s - %s." % (brandName, modelName, versionName))
        self.insertStringData("cars_brand", s)


    def readAllDataGenerator(self, tableName, amount=2000, where=""):
        conn = sqlite3.connect(self.dbName)
        cursor = self.conn.cursor()

        methodName = inspect.stack()[0][3]
        command = "SELECT * FROM %s %s" % (tableName, where)
        moduleLogger.debug("%s - Command: %s will be executed." % (methodName, command))
        cursor.execute(command)
        moduleLogger.debug("%s - Command: %s executed successfully." % (methodName, command))

        counter = 0
        while True:
            rows = cursor.fetchmany(amount)
            if not rows:
                moduleLogger.debug(
                    "%s - End of rows returned from command: %s. There was around %d records in %s table." %
                                   (methodName, command, counter * amount, tableName))
                conn.close()
                break
            moduleLogger.debug("%s - Fetching another %d rows." % (methodName, amount))
            counter += 1
            for row in rows:
                yield row

    # this is obsolete, use readAllDataGenerator
    def readAllData(self, tableName):

        methodName = inspect.stack()[0][3]

        command = "SELECT * FROM %s" % tableName
        moduleLogger.debug("%s - Command: %s will be executed." % (methodName, command))
        self.c.execute(command)
        moduleLogger.debug("%s - Command: %s executed successfully." % (methodName, command))
        items = self.c.fetchall()
        moduleLogger.debug("%s - Number of items returned: %d." % (methodName, len(items)))
        return items

    def executeSqlCommand(self, command):
        methodName = inspect.stack()[0][3]

        moduleLogger.debug("%s - Command: %s will be executed." % (methodName, command))
        self.c.execute(command)
        self.conn.commit()
        moduleLogger.debug("%s - Command: %s executed successfully." % (methodName, command))


    def _getAllIds(self, colName, name):
        methodName = inspect.stack()[0][3]

        command = """SELECT B_Id FROM Brands WHERE %s = "%s" """ % (colName, name)
        moduleLogger.debug("%s - Command: %s will be executed." % (methodName, command))
        self.c.execute(command)
        moduleLogger.debug("%s - Command: %s executed successfully." % (methodName, command))
        output = self.c.fetchall()

        if output:
            items = [element[0] for element in output]
            moduleLogger.debug("%s - Number of items returned: %d." % (methodName, len(items)))
            return items
        else:
            raise Exception('There is no %s called %s'  % (colName, name))

    def _getCarsById(self,  brandId):
        methodName = inspect.stack()[0][3]

        command = """SELECT * FROM CarData WHERE B_Id = "%s" """ % brandId
        moduleLogger.debug("%s - Command: %s will be executed." % (methodName, command))
        self.c.execute(command)
        moduleLogger.debug("%s - Command: %s executed successfully." % (methodName, command))
        output = self.c.fetchall()

        if output:
            moduleLogger.debug("%s - Number of items returned: %d." % (methodName, len(output)))
            return output
        else:
            moduleLogger.debug('%s - There are no cars with B_Id %s'  % (methodName,brandId))
            return []

    #TODO write unittests
    def getAllParsedBrandsIds(self):
        methodName = inspect.stack()[0][3]

        command = """SELECT DISTINCT B_Id FROM CarData"""
        moduleLogger.debug("%s - Command: %s will be executed." % (methodName, command))
        self.c.execute(command)
        moduleLogger.debug("%s - Command: %s executed successfully." % (methodName, command))
        output = self.c.fetchall()

        if output:
            items = [element[0] for element in output]
            moduleLogger.debug("%s - Number of items returned: %d." % (methodName, len(items)))
            return items
        else:
            return []

    # TODO write unittests
    def getBrandInfo(self, B_Id):
        methodName = inspect.stack()[0][3]

        command = """SELECT brandName, modelName, version FROM Brands WHERE B_Id = "%s" """ % B_Id
        moduleLogger.debug("%s - Command: %s will be executed." % (methodName, command))
        self.c.execute(command)
        moduleLogger.debug("%s - Command: %s executed successfully." % (methodName, command))
        output = self.c.fetchone()
        if output:
            items = [DataCleaning.normalize(element) for element in output if element]
            moduleLogger.debug("%s - Number of items returned: %d." % (methodName, len(items)))
            return items
        else:
            return []

    def getAllBrandIdsOfBrand(self, brandName):
        return self._getAllIds('brandName', brandName)

    def getAllBrandIdsOfModel(self, modelName):
        return self._getAllIds('modelName', modelName)

    def getVersionID(self, modelName, version):
        methodName = inspect.stack()[0][3]

        command = """SELECT B_Id FROM Brands WHERE "modelName" = "%s" and "version" = "%s" """ % (modelName, version)
        moduleLogger.debug("%s - Command: %s will be executed." % (methodName, command))
        self.c.execute(command)
        moduleLogger.debug("%s - Command: %s executed successfully." % (methodName, command))
        output = self.c.fetchall()

        if output:
            items = [element[0] for element in output]
            moduleLogger.debug("%s - Number of items returned: %d." % (methodName, len(items)))
            return items[0]
        else:
            raise Exception('There is no version "%s" of model called "%s"'  % (version, modelName))


    #TODO: Use GENERATOR for method below

    def getAllCars(self):
        methodName = inspect.stack()[0][3]

        command = """SELECT * FROM CarData """
        moduleLogger.debug("%s - Command: %s will be executed." % (methodName, command))
        self.c.execute(command)
        moduleLogger.debug("%s - Command: %s executed successfully." % (methodName, command))
        output = self.c.fetchall()

        if output:
            moduleLogger.debug("%s - Number of items returned: %d." % (methodName, len(output)))
            return output

        else:
            raise Exception('Problems with getting all car data')

    def getAllCarsOfModel(self, modelName):
        methodName = inspect.stack()[0][3]

        cars = []
        modelIds = self.getAllBrandIdsOfModel(modelName)
        for brandId in modelIds:
            cars.extend(self._getCarsById(brandId))

        moduleLogger.debug("%s - Number of cars returned: %d which have a model name: %s." %
                           (methodName, len(cars), modelName))
        return cars

    def getAllCarsOfBrand(self, brandName):
        methodName = inspect.stack()[0][3]

        cars = []
        modelIds = self.getAllBrandIdsOfBrand(brandName)
        for brandId in modelIds:
            cars.extend(self._getCarsById(brandId))
        moduleLogger.debug("%s - Number of cars returned: %d which have a brand name: %s." %
                           (methodName, len(cars), brandName))
        return cars

    def getAllCarsOfVersion(self, modelName, versionName):
        methodName = inspect.stack()[0][3]

        cars = self._getCarsById(self.getVersionID(modelName, versionName))
        moduleLogger.debug("%s - Number of cars returned: %d which have a model  and version name: %s - %s." %
                            (methodName, len(cars), modelName, versionName))
        return cars

    def _valueIsPresentInColumnOfATable(self, value, column, table):
        methodName = inspect.stack()[0][3]

        command = """SELECT 1 FROM %s WHERE "%s" = "%s" """ % (table, column, value)
        try:
            now = time.time()
            self.c.execute(command)
            moduleLogger.debug("%s - Command: %s executed in %f." % (methodName, command, float(time.time() - now)))
        except:
            return True
            moduleLogger.debug("%s - Command: %s not executed successfully." % (methodName, command))

        valueIsPresentInDb = self.c.fetchall() != []

        if valueIsPresentInDb:
            moduleLogger.debug("%s - Value: %s is present in table: %s." % (methodName, value, table))
        else:
            moduleLogger.debug("%s - Value: %s is NOT present in table: %s." % (methodName, value, table))

        return valueIsPresentInDb

    def linkIsPresentInDatabase(self, link):
        return self._valueIsPresentInColumnOfATable(link, "link", "links")

    def thereAreParsedLinksInTheTable(self):
        return self._valueIsPresentInColumnOfATable("True", "parsed", "links")

    def brandLinkIsPresentInDatabase(self, link):
        return self._valueIsPresentInColumnOfATable(link, 'link', "cars_brand")

    def brandNameIsPresentInDatabase(self, brandName):
        return self._valueIsPresentInColumnOfATable(brandName, 'brandname', "cars_brand")

    def modelNameIsPresentInDatabase(self, modelName):
        return self._valueIsPresentInColumnOfATable(modelName, 'modelname', "cars_brand")

    def versionIsPresentInDatabase(self, version):
        return self._valueIsPresentInColumnOfATable(version, 'version', "cars_brand")

    def countRecordsInTable(self, tableName):
        command = "SELECT count(*) FROM %s" % tableName
        self.c.execute(command)
        output = self.c.fetchone()
        return int(output[0])

    def getMaxFromColumnInTable(self, column, table):
        command = """SELECT MAX(%s) FROM %s""" % (column, table)
        self.c.execute(command)
        output = self.c.fetchone()

        if output and output[0] is not None:
            return int(output[0])
        else:
            return 0

    def tableExists(self, table):
        methodName = inspect.stack()[0][3]

        command = """SELECT name FROM sqlite_master WHERE type = "table" AND name = "%s" """ % table
        self.c.execute(command)
        moduleLogger.debug("%s - Command: %s executed successfully." % (methodName, command))
        columnExists = self.c.fetchall() != []

        if columnExists:
            moduleLogger.debug("%s - Table %s exists" % (methodName, table))
        else:
            moduleLogger.debug("%s - Table %s does not exists" % (methodName, table))

        return columnExists

    #TODO: Unit tests, calculate how many links were transfered and return it
    def clearParsedLinks(self):

        self.executeSqlCommand("INSERT INTO oldlinks SELECT * FROM links WHERE time < '%s'" %
                               str(datetime.datetime.now() - datetime.timedelta(30)))
