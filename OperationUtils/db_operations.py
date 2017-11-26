import sqlite3
from OperationUtils.logger import Logger
import inspect


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

    def readAllDataGenerator(self, tableName, amount=1000, where=""):
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

    def valueIsPresentInColumnOfATable(self, value, column, table):
        methodName = inspect.stack()[0][3]

        command = """SELECT * FROM %s WHERE "%s" = "%s" """ % (table, column, value)
        self.c.execute(command)
        moduleLogger.debug("%s - Command: %s executed successfully." % (methodName, command))
        valueIsPresentInDb = self.c.fetchall() != []

        if valueIsPresentInDb:
            moduleLogger.debug("%s - Value: %s is present in table: %s." % (methodName, value, table))
        else:
            moduleLogger.debug("%s - Value: %s is NOT present in table: %s." % (methodName, value, table))

        return valueIsPresentInDb

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
