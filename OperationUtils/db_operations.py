import sqlite3
from OperationUtils.car_verification_utils import CarVerificationUtils
from OperationUtils.logger import Logger
import inspect
import datetime
import time
from collections import OrderedDict


moduleLogger = Logger.setLogger("dbops")

class DataBaseTable(object):
    #TODO: Unit tests
    def __init__(self, tableName, columnsDictionary):
        self.name = tableName
        self.columnsDictionary = columnsDictionary

    def getName(self):
        return self.name

    def getColumnsDictionary(self):
        return self.columnsDictionary

    def getColumnsNames(self):
        return self.columnsDictionary.keys()

class DataBaseSchema(object):
    def __init__(self):
        self.brandTable = DataBaseTable("cars_brand", OrderedDict(
            [('b_id', "INT"), ('brandname', "TEXT"), ('modelname', "TEXT"), ('version', "TEXT"),
             ('allegro_link', "TEXT"), ('otomoto_link', "TEXT")]))

        self.linkTable = DataBaseTable("links", OrderedDict(
            [('l_id', "INT"), ('b_id', "INT"), ('time', "TEXT"), ('link', "TEXT"), ('parsed', 'BOOL'), ("site_id", "INT")]))

        self.oldLinkTable = DataBaseTable("old_links", OrderedDict(
            [('l_id', "INT"), ('b_id', "INT"), ('time', "TEXT"), ('link', "TEXT"), ('parsed', 'BOOL'), ("site_id", "INT")]))

        self.invalidLinksTable = DataBaseTable("invalid_links",
                                               OrderedDict([('l_id', "INT"), ('time', "TEXT"), ('link', "TEXT")]))

        self.carsTable = DataBaseTable("cars_car", OrderedDict(
            [('b_id', "INT"), ('l_id', "INT"), ('year', "INT"), ('mileage', "INT"), ('power', "INT"),
             ('capacity', "INT"), ('fuel', "TEXT"), ('color', "TEXT"), ('usedornew', "TEXT"),
             ('doors', "TEXT"), ('gearbox', "TEXT"), ('location', "TEXT"), ('price', "INT"),
             ('time', "TEXT"), ("site_id", "INT")]))

        self.allegroCollectCycle = DataBaseTable("allegro_collect_cycle", OrderedDict(
            [('start_brands', "TEXT"), ('start_links', "TEXT"), ('start_cars', "TEXT"),
             ('end_time', "TEXT"), ('new_brands', "INT"), ('new_links', "INT"),
             ('new_cars', "INT")]))

        self.siteIdentifierTable = DataBaseTable("site_identifiers",
                                                 OrderedDict([("name", "TEXT"), ("identifier", "INT")]))

    def getEntireSchema(self):
        return [self.brandTable, self.linkTable, self.oldLinkTable, self.invalidLinksTable, self.carsTable,
                self.allegroCollectCycle, self.siteIdentifierTable]

class DataBase(object):
    def __init__(self, databaseName):
        self.dbName = databaseName
        self.dbSchema = DataBaseSchema()
        self.conn = sqlite3.connect(databaseName)
        #TODO: self.c? really?
        self.c = self.conn.cursor()
        moduleLogger.info("Connection to db: '%s' is set up." % databaseName)

    def __del__(self):
        self.c.close()
        self.conn.close()
        moduleLogger.info("Connection to db is closed.")

    def constructDBTables(self):
        for databaseTable in self.dbSchema.getEntireSchema():
            self.createTable(databaseTable.getName(), databaseTable.getColumnsDictionary())

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

    #todo: unit tests
    def insertOtoMotoBrandLink(self, otomotolink, b_id):
        cmd = "UPDATE %s SET otomotolink = %s where b_id = %d" % (self.dbSchema.brandTable.getName(), otomotolink, b_id)

    def insertAllegroBrandToDatabase(self, brandId, brandName, allegroLink, otomotoLink =""):
        moduleLogger.debug("Inserting brand: %s." % brandName)
        s = """%d, "%s", NULL, NULL, "%s", "%s" """ % (brandId, brandName, allegroLink, otomotoLink)
        self._insertStringData(self.dbSchema.brandTable.getName(), s)

    def insertModelToDatabase(self, brandId, brandName, modelName, allegroLink, otomotoLink =""):
        moduleLogger.debug("Inserting model: %s - %s." % (brandName, modelName))
        s = """%d, "%s", "%s", NULL, "%s", "%s" """ % (brandId, brandName, modelName, allegroLink, otomotoLink)
        self._insertStringData(self.dbSchema.brandTable.getName(), s)

    def insertVersionToDatabase(self, brandId, brandName, modelName, versionName, allegroLink, otomotoLink =""):
        s = """%d, "%s", "%s", "%s", "%s", "%s" """ % (brandId, brandName, modelName, versionName, allegroLink, otomotoLink)
        moduleLogger.debug("Inserting version: %s - %s - %s." % (brandName, modelName, versionName))
        self._insertStringData(self.dbSchema.brandTable.getName(), s)

    def insertLinkToDatabase(self, linkId, brandId, siteId, link):
        moduleLogger.debug("Inserting link: %s." % link)
        s = """ %d, %d, "%s", "%s", "%r", %d """ % (linkId, brandId, str(datetime.datetime.now()), link, False, siteId)
        self._insertStringData(self.dbSchema.linkTable.getName(), s)

    def insertInvalidLinkToDatabase(self, linkId, link):
        moduleLogger.debug("Inserting invalid link: %s." % link)
        s = """ "%d", "%s", "%s" """ % (linkId, str(datetime.datetime.now()), link)
        self._insertStringData(self.dbSchema.invalidLinksTable.getName(), s)

    def insertAllegroCarToDatabase(self, b_id, l_id, carDict):
        verificator = CarVerificationUtils()
        s = verificator.constructAllegroCarInsert(b_id, l_id, carDict)
        self._insertStringData(self.dbSchema.carsTable.getName(), s)

    def insertAllegroCollectCycleToDatabase(self, brandsStartTime, linksStartTime, carsStartTime,
                                            endTime, newBrands, newLinks, newCars):
        dbmsg = """ "%s", "%s", "%s", "%s", %d, %d, %d""" % \
                (str(brandsStartTime), str(linksStartTime), str(carsStartTime),
                 str(endTime), newBrands, newLinks, newCars)
        self._insertStringData(self.dbSchema.allegroCollectCycle.getName(), dbmsg)

    def insertSiteIdentifierToDatabase(self, name, identifier):
        dbmsg = """ '%s', %d """ % (name, identifier)
        self._insertStringData(self.dbSchema.siteIdentifierTable.getName(), dbmsg)

    def getAmountOfBrands(self):
        return self.getMaxFromColumnInTable("b_id", self.dbSchema.brandTable.getName())

    def getAmountOfLinks(self):
        return self.getMaxFromColumnInTable("l_id", self.dbSchema.linkTable.getName())

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

    def readAllUnparsedLinks(self):
        return self.readAllDataGenerator(self.dbSchema.linkTable.getName(), where='WHERE parsed = "False"')

    def readAllBrands(self):
        return self.readAllDataGenerator(self.dbSchema.brandTable.getName())

    def getAllBrandNames(self):
        return set([brand[1] for brand in self.readAllDataGenerator(self.dbSchema.brandTable.getName())])

    def getAllModelNamesOfBrand(self, brandName):
        return set([model[2] for model in self.readAllDataGenerator(self.dbSchema.brandTable.getName(), where='where brandname="%s"' % brandName)])

    def getAllVersionNamesOfModel(self, brandName):
        return set([version[3] for version in self.readAllDataGenerator(self.dbSchema.brandTable.getName(), where='where modelname="%s"' % brandName)])

    # todo: unit tests
    def addColumnToATable(self, columnName, dataType, tableName):
        self._executeSqlCommand("alter table %s Add %s %s" % (tableName, columnName, dataType))

    def _executeSqlCommand(self, command):
        methodName = inspect.stack()[0][3]

        moduleLogger.debug("%s - Command: %s will be executed." % (methodName, command))
        self.c.execute(command)
        self.conn.commit()
        moduleLogger.debug("%s - Command: %s executed successfully." % (methodName, command))

    # ==?==
    def _getAllIds(self, colName, name):
        methodName = inspect.stack()[0][3]

        command = """SELECT B_Id FROM %s WHERE %s = "%s" """ % (self.dbSchema.brandTable.getName(), colName, name)
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

        command = """SELECT * FROM %s WHERE B_Id = "%s" """ % (self.dbSchema.carsTable.getName(), brandId)
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

    # ==?==
    def getAllBrandIdsOfBrand(self, brandName):
        return self._getAllIds('brandName', brandName)

    # ==?==
    def getAllBrandIdsOfModel(self, modelName):
        return self._getAllIds('modelName', modelName)

    # ==?==
    def getVersionID(self, modelName, version):
        methodName = inspect.stack()[0][3]

        command = """SELECT B_Id FROM %s WHERE "modelName" = "%s" and "version" = "%s" """ % (
                                                                self.dbSchema.brandTable.getName(), modelName, version)
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
    # ==?==
    def getAllCars(self):
        methodName = inspect.stack()[0][3]

        command = """SELECT * FROM %s """ % self.dbSchema.carsTable.getName()
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

    # ==?==
    def linkIsPresentInDatabase(self, link):
        return self._valueIsPresentInColumnOfATable(link, "allegro_link", self.dbSchema.linkTable.getName())

    # ==?==
    def thereAreParsedLinksInTheTable(self):
        return self._valueIsPresentInColumnOfATable("True", "parsed", self.dbSchema.linkTable.getName())

    # ==?==
    def thereAreOnlyParsedLinksInTheTable(self):
        return not self._valueIsPresentInColumnOfATable("False", "parsed", self.dbSchema.linkTable.getName())

    # ==?==
    def thereAreOnlyUnparsedLinksInTheTable(self):
        return not self._valueIsPresentInColumnOfATable("True", "parsed", self.dbSchema.linkTable.getName())

    # ==?==
    def allegroBrandLinkIsPresentInDatabase(self, link):
        return self._valueIsPresentInColumnOfATable(link, 'allegro_link', self.dbSchema.brandTable.getName())

    # ==?==
    def brandNameIsPresentInDatabase(self, brandName):
        return self._valueIsPresentInColumnOfATable(brandName, 'brandname', self.dbSchema.brandTable.getName())

    # ==?==
    def modelNameIsPresentInDatabase(self, modelName):
        return self._valueIsPresentInColumnOfATable(modelName, 'modelname', self.dbSchema.brandTable.getName())

    # ==?==
    def versionIsPresentInDatabase(self, version):
        return self._valueIsPresentInColumnOfATable(version, 'version', self.dbSchema.brandTable.getName())

    def countRecordsInTable(self, tableName):
        #mostly for testing purposes
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

    def columnOfATableExists(self, column, table):
        command = """SELECT %s FROM %s """ % (column, table)
        try:
            self.c.execute(command)
            return True
        except:
            return False

    #TODO: test if old links are removed
    def clearLinksOlderThanMonth(self):
        self._executeSqlCommand("INSERT INTO %s SELECT * FROM %s WHERE time < '%s'" %
                                (self.dbSchema.oldLinkTable.getName(), self.dbSchema.linkTable.getName(),
                                 str(datetime.datetime.now() - datetime.timedelta(30))))

    def updateParsedParameterForLinkWithId(self, linkId):
        self._executeSqlCommand(
            """UPDATE %s SET parsed = "True" WHERE l_id = "%d" """ % (self.dbSchema.linkTable.getName(), linkId))

