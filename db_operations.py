import sqlite3
from cars import setUpLogger

class DataBase(object):
    def __init__(self, databaseName):
        self.logger = setUpLogger("DataBase")
        self.conn = sqlite3.connect(databaseName)
        self.c = self.conn.cursor()
        self.logger.info("Connection to db: '%d' is set up." % databaseName)

    def __del__(self):
        self.c.close()
        self.conn.close()
        self.logger.info("Connection to db is closed.")

    def createTable(self, name, columnDict):
        command = "CREATE TABLE IF NOT EXISTS %s(" % name
        for item in columnDict.items():
            command += " %s %s," % item
        command = command[:-1] + ")"

        self.logger.debug("Command: %s will be executed." % command)
        self.c.execute(command)
        self.logger.info("Command: %s executed successfully." % command)

    def insertStringData(self, tableName, stringData):
        command = "INSERT INTO %s VALUES(%s)" % (tableName, stringData)
        self.logger.debug("Command: %s will be executed." % command)
        self.c.execute(command)
        self.conn.commit()
        self.logger.info("Command: %s executed successfully." % command)

    def readAllData(self, tableName):
        command = "SELECT * FROM %s" % tableName
        self.logger.debug("Command: %s will be executed." % command)
        self.c.execute(command)
        self.logger.info("Command: %s executed successfully." % command)
        items = self.c.fetchall()
        self.logger.info("Number of items returned: %d." % len(items))
        return items

    def executeSqlCommand(self, command):
        self.logger.debug("Command: %s will be executed." % command)
        self.c.execute(command)
        self.conn.commit()
        self.logger.info("Command: %s executed successfully." % command)


    def _getAllIds(self, colName, name):
        command = """SELECT B_Id FROM Brands WHERE %s = "%s" """ % (colName, name)
        self.logger.debug("Command: %s will be executed." % command)
        self.c.execute(command)
        self.logger.info("Command: %s executed successfully." % command)
        output = self.c.fetchall()

        if output:
            items = [element[0] for element in output]
            self.logger.debug("Number of items returned: %d." % len(items))
            return items
        else:
            raise Exception('There is no %s name called %s'  % (colName, name))

    def _getCarsById(self,  brandId):
        command = """SELECT * FROM CarData WHERE B_Id = "%s" """ %  brandId
        self.logger.debug("Command: %s will be executed." % command)
        self.c.execute(command)
        self.logger.info("Command: %s executed successfully." % command)
        output = self.c.fetchall()

        if output:
            self.logger.debug("Number of items returned: %d." % len(output))
            return output
        else:
            raise Exception('There are no cars with B_Id %s'  % brandId)

    def getAllBrandIdsOfBrand(self, brandName):
        return self._getAllIds('brandName', brandName)

    def getAllBrandIdsOfModel(self, modelName):
        return self._getAllIds('modelName', modelName)

    def getVersionID(self, modelName, version):
        command = """SELECT B_Id FROM Brands WHERE "modelName" = "%s" and "version" = "%s" """ % (modelName, version)
        self.logger.debug("Command: %s will be executed." % command)
        self.c.execute(command)
        self.logger.info("Command: %s executed successfully." % command)
        output = self.c.fetchall()

        if output:
            items = [element[0] for element in output]
            self.logger.debug("Number of items returned: %d." % len(items))
            return items
        else:
            raise Exception('There is no version "%s" of model called "%s"'  % (version, modelName))

    def getAllCars(self):
        command = """SELECT * FROM CarData """
        self.logger.debug("Command: %s will be executed." % command)
        self.c.execute(command)
        self.logger.info("Command: %s executed successfully." % command)
        output = self.c.fetchall()

        if output:
            self.logger.debug("Number of items returned: %d." % len(output))
            return output

        else:
            raise Exception('Problems with getting all car data')

    def getAllCarsOfModel(self, modelName):
        cars = []
        modelIds = self.getAllBrandIdsOfModel(modelName)
        for brandId in modelIds:
            cars.extend(self._getCarsById(brandId))

        self.logger.debug("Number of cars returned: %d which have a model name: %s." % (len(cars), modelName))
        return cars

    def getAllCarsOfBrand(self, brandName):
        cars = []
        modelIds = self.getAllBrandIdsOfBrand(brandName)
        for brandId in modelIds:
            cars.extend(self._getCarsById(brandId))
        self.logger.debug("Number of cars returned: %d which have a brand name: %s." % (len(cars), brandName))
        return cars

    def getAllCarsOfVersion(self, modelName, versionName):
        cars = self._getCarsById(self.getVersionID(modelName, versionName)[0])
        self.logger.debug("Number of cars returned: %d which have a model  and version name: %s - %s." % (len(cars), modelName, versionName))
        return cars
