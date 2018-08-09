import sqlite3
from OperationUtils.car_verification_utils import CarVerificationUtils
from OperationUtils.data_operations import DataCleaning
from OperationUtils.logger import Logger
import inspect
import datetime
import time
from collections import OrderedDict


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

    #todo: testing
    def constructDBTables(self):
        brandsDict = OrderedDict(
            [('b_id', "INT"), ('brandname', "TEXT"), ('modelname', "TEXT"), ('version', "TEXT"), ('link', "TEXT")])
        linksDict = OrderedDict(
            [('l_id', "INT"), ('b_id', "INT"), ('time', "TEXT"), ('link', "TEXT"), ('parsed', 'BOOL')])
        oldLinksDict = OrderedDict(
            [('l_id', "INT"), ('b_id', "INT"), ('time', "TEXT"), ('link', "TEXT"), ('parsed', 'BOOL')])
        InvalidLinksDict = OrderedDict([('l_id', "INT"), ('time', "TEXT"), ('link', "TEXT")])
        carDataDict = OrderedDict(
            [('b_id', "INT"), ('l_id', "INT"), ('year', "INT"), ('mileage', "INT"), ('power', "INT"),
             ('capacity', "INT"), ('fuel', "TEXT"), ('color', "TEXT"), ('usedornew', "TEXT"),
             ('doors', "TEXT"), ('gearbox', "TEXT"), ('price', "INT"), ('time', "TEXT")])
        CycleDict = OrderedDict([('start_brands', "TEXT"), ('start_links', "TEXT"), ('start_cars', "TEXT"),
                                 ('end_time', "TEXT"), ('new_brands', "INT"), ('new_links', "INT"),
                                 ('new_cars', "INT")])

        self.createTable('cars_brand', brandsDict)
        self.createTable('links', linksDict)
        self.createTable('oldlinks', oldLinksDict)
        self.createTable('cars_car', carDataDict)
        self.createTable('invalidlinks', InvalidLinksDict)
        self.createTable('collectcycle', CycleDict)

    def createTable(self, name, columnDict):
        methodName = inspect.stack()[0][3]

        command = "CREATE TABLE IF NOT EXISTS %s(" % name
        for item in columnDict.items():
            command += " %s %s," % item
        command = command[:-1] + ")"

        moduleLogger.debug("%s - Command: %s will be executed." % (methodName, command))
        self.c.execute(command)
        moduleLogger.debug("%s - Command: %s executed successfully." % (methodName, command))

    def _insertStringData(self, tableName, stringData):
        methodName = inspect.stack()[0][3]

        command = "INSERT INTO %s VALUES(%s)" % (tableName, stringData)
        moduleLogger.debug("%s - Command: %s will be executed." % (methodName, command))
        self.c.execute(command)
        self.conn.commit()
        moduleLogger.debug("%s - Command: %s executed successfully." % (methodName, command))

    #todo: testing
    def insertLinkToDatabase(self, linkId, brandId, link):
        moduleLogger.debug("Inserting link: %s." % link)
        s = """ %d, %d, "%s", "%s", "%r" """ % (linkId, brandId, str(datetime.datetime.now()), link, False)
        self._insertStringData("links", s)

    # todo: testing
    def insertInvalidLinkToDatabase(self, linkId, link):
        moduleLogger.debug("Inserting invalid link: %s." % link)
        s = """ "%d", "%s", "%s" """ % (linkId, str(datetime.datetime.now()), link)
        self._insertStringData("invalidlinks", s)

    # todo: testing
    def insertBrandToDatabase(self, brandId, brandName, link):
        moduleLogger.debug("Inserting brand: %s." % brandName)
        s = """%d, "%s", NULL, NULL, "%s" """ % (brandId, brandName, link)
        self._insertStringData("cars_brand", s)

    # todo: testing
    def insertModelToDatabase(self, brandId, brandName, modelName, link):
        moduleLogger.debug("Inserting model: %s - %s." % (brandName, modelName))
        s = """%d, "%s", "%s", NULL, "%s" """ % (brandId, brandName, modelName, link)
        self._insertStringData("cars_brand", s)

    # todo: testing
    def insertVersionToDatabase(self, brandId, brandName, modelName, versionName, link):
        s = """%d, "%s", "%s", "%s", "%s" """ % (brandId, brandName, modelName, versionName, link)
        moduleLogger.debug("Inserting version: %s - %s - %s." % (brandName, modelName, versionName))
        self._insertStringData("cars_brand", s)

    # todo: testing
    def insertAllegroCarToDatabase(self, b_id, l_id, carDict):
        verificator = CarVerificationUtils()
        s = verificator.constructAllegroCarInsert(b_id, l_id, carDict)
        self._insertStringData("cars_car", s)

    # todo: testing
    def insertCollectCycleToDatabase(self, brandsStartTime, linksStartTime, carsStartTime,
                                     endTime, newBrands, newLinks, newCars):
        dbmsg = """ "%s", "%s", "%s", "%s", %d, %d, %d""" % \
                (str(brandsStartTime), str(linksStartTime), str(carsStartTime),
                 str(endTime), newBrands, newLinks, newCars)
        self._insertStringData("collectcycle", dbmsg)

    # todo: testing
    def getAmountOfBrands(self):
        return self.getMaxFromColumnInTable("b_id", "cars_brand")

    # todo: testing
    def getAmountOfLinks(self):
        return self.getMaxFromColumnInTable("l_id", "links")

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

    # todo: testing
    def readAllUnparsedLinks(self):
        return self.readAllDataGenerator('links', where='WHERE parsed = "False"')

    # todo: testing
    def readAllBrands(self):
        return self.readAllDataGenerator('cars_brand')

    def _executeSqlCommand(self, command):
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

    # todo: testing
    def linkIsPresentInDatabase(self, link):
        return self._valueIsPresentInColumnOfATable(link, "link", "links")

    # todo: testing
    def thereAreParsedLinksInTheTable(self):
        return self._valueIsPresentInColumnOfATable("True", "parsed", "links")

    # todo: testing
    def thereAreOnlyParsedLinksInTheTable(self):
        return not self._valueIsPresentInColumnOfATable("False", "parsed", "links")

    # todo: testing
    def thereAreOnlyUnparsedLinksInTheTable(self):
        return not self._valueIsPresentInColumnOfATable("True", "parsed", "links")

    # todo: testing
    def brandLinkIsPresentInDatabase(self, link):
        return self._valueIsPresentInColumnOfATable(link, 'link', "cars_brand")

    # todo: testing
    def brandNameIsPresentInDatabase(self, brandName):
        return self._valueIsPresentInColumnOfATable(brandName, 'brandname', "cars_brand")

    # todo: testing
    def modelNameIsPresentInDatabase(self, modelName):
        return self._valueIsPresentInColumnOfATable(modelName, 'modelname', "cars_brand")

    # todo: testing
    def versionIsPresentInDatabase(self, version):
        return self._valueIsPresentInColumnOfATable(version, 'version', "cars_brand")

    # todo: testing
    def countRecordsInTable(self, tableName):
        command = "SELECT count(*) FROM %s" % tableName
        self.c.execute(command)
        output = self.c.fetchone()
        return int(output[0])

    # todo: testing
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
        self._executeSqlCommand("INSERT INTO oldlinks SELECT * FROM links WHERE time < '%s'" %
                                str(datetime.datetime.now() - datetime.timedelta(30)))

    # todo: testing
    def updateParsedParameterForLinkWithId(self, linkId):
        self._executeSqlCommand("""UPDATE links SET parsed = "True" WHERE l_id = "%d" """ % linkId)

