import sqlite3

class DataBase(object):
    def __init__(self, databaseName):
        # if os.path.exists(databaseName):
        #     raise ValueError("File already exists.")

        self.conn = sqlite3.connect(databaseName)
        self.c = self.conn.cursor()

    def __del__(self):
        self.c.close()
        self.conn.close()

    def createTable(self, name, columnDict):
        command = "CREATE TABLE IF NOT EXISTS %s(" % name
        for item in columnDict.items():
            command += " %s %s," % item
        command = command[:-1] + ")"
        self.c.execute(command)

    def insertDictData(self, tableName, dataDict):
        command = "INSERT INTO %s VALUES(%s)" % (tableName, ", ".join(dataDict.values()))
        self.c.execute(command)
        self.conn.commit()

    def insertStringData(self, tableName, stringData):
        command = "INSERT INTO %s VALUES(%s)" % (tableName, stringData)
        self.c.execute(command)
        self.conn.commit()

    def insertMany(self, tableName, listOfDataDictionaries):
        for element in listOfDataDictionaries:
            self.insertData(tableName, element)

    def readAllData(self, tableName):
        command = "SELECT * FROM %s" %tableName
        self.c.execute(command)
        return self.c.fetchall()

    def executeReadCommand(self, command):
        self.c.execute(command)
        return self.c.fetchall()

    def executeSqlCommand(self, command):
        self.c.execute(command)
        self.conn.commit()


    def _getAllIds(self, colName, name):
        command = """SELECT B_id FROM Brands WHERE %s = "%s" """ % (colName, name)
        self.c.execute(command)
        output = self.c.fetchall()

        if output:
            return [element[0] for element in output]
        else:
            raise Exception('There is no %s name called %s'  % (colName, name))

    def getAllBrandIdsOfParticularBrand(self, brandName):
        return self._getAllIds('brandName', brandName)

    def getAllBrandIdsOfParticularModel(self, modelName):
        return self._getAllIds('modelName', modelName)

    def getVersionID(self, version):
        return self._getAllIds('version', version)[0]
