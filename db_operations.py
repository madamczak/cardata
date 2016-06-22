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
