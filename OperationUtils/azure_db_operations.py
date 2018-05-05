import pyodbc
import psycopg2
from collections import OrderedDict

import pyodbc
# server = 'cloudcardataserver.database.windows.net'
# database = 'cloudcardata'
# username = 'madamczak'
# password = 'QAZwsx11!'
# driver= '{SQL Server}'
# cnxn = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
# cursor = cnxn.cursor()

# dsn = 'cloudcardatadatasource'
# user = 'madamczak@cloudcardataserver'
# password = 'QAZwsx11!'
# database = 'cloudcardata'
#connString = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (dsn, user, password, database)

host = "cloudcardatapostgres.postgres.database.azure.com"
user = "madamczak@cloudcardatapostgres"
dbname = "postgres"
password = "QAZwsx11!"
sslmode = "require"

# Construct connection string
conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)

class AzureDB(object):
    def __init__(self, host, user, dbname, password, sslmode):
        conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password,
                                                                                     sslmode)
        self.connection = psycopg2.connect(conn_string)
        self.cursor = self.connection.cursor()

    def createTable(self, name, columnDict, primaryKey=None):
        #command = "IF NOT EXISTS(SELECT * FROM sysobjects WHERE name='%s' AND xtype='U') " % name
        command = "CREATE TABLE IF NOT EXISTS %s(" % name
        for item in columnDict.items():
            if primaryKey is not None and item[0] == primaryKey:
                command += " %s %s PRIMARY KEY," % item
            else:
                command += " %s %s," % item
        command = command[:-1] + ")"
        self.cursor.execute(command)
        self.connection.commit()


    def _insertStringData(self, tableName, stringData):
        command = "INSERT INTO %s VALUES(%s)" % (tableName, stringData)
        self.cursor.execute(command)
        self.connection.commit()

    def insertDataIfIDIsNotPresentInTable(self, tableName, stringData, whatId):
        if whatId == "B_Id":
            ID = stringData.split(",")[0]
        else:
            ID = stringData.split(",")[1]


        if not self.valueIsPresentInColumnOfATable(ID, whatId, tableName):
            self._insertStringData(tableName, stringData)
            print stringData
        else:
            print stringData + "Is already in DB"


    def valueIsPresentInColumnOfATable(self, value, column, table):
        cmd = "SELECT 1 FROM %s WHERE %s = %s" % (table, column, value)
        self.cursor.execute(cmd)
        valueIsPresentInDb = self.cursor.fetchall() != []

        return valueIsPresentInDb






# brandsDict = OrderedDict(
#         [('B_Id', "INT"), ('brandName', "TEXT"), ('modelName', "TEXT"), ('version', "TEXT"), ('link', "TEXT")])
# #
# adb = AzureDB(server, database, username, password, driver)
# adb.createTable("EEEE", brandsDict, primaryKey="B_Id")
# adb.insertDataIfIDIsNotPresentInTable("EEEE", "12, 'asd', 'dsa', 'qwe', 'ewq'", "B_Id")
# print adb.valueIsPresentInColumnOfATable(111, "B_Id", "EEEE")
#adb.insertStringData("EEEE", "11, 'asd', 'dsa', 'qwe', 'ewq'")
#
# cmd = """CREATE TABLE Brands
#    (B_Id int PRIMARY KEY NOT NULL,
#     brandName text NOT NULL,
#     modelName text NULL,
#     version text NULL,
#     link text NULL)
# """
# #
# adb.cursor.execute(cmd)
# # adb.connection.commit()
# cmd2 = """INSERT Brands (B_Id, brandName, modelName, version, link)
#     VALUES (50, 'AA', 'BB', 'CC', 'DD')"""
#
# cmd3 = """INSERT Brands (B_Id, brandName, modelName, version, link)
#     VALUES (1, 'as', 'ds', 'fd', 'gf')"""
#
# adb.cursor.execute(cmd2)
# adb.cursor.execute(cmd3)
# adb.connection.commit()
#
# adb.cursor.execute("SELECT * FROM Brands2")
# print adb.cursor.fetchall()

# adb.cursor.execute("SELECT * FROM Brands")
# print adb.cursor.fetchall()
# adb = AzureDB(server, database, username, password, driver)
# adb.createTable("CCC", brandsDict)
#adb.insertStringData("Brands", "11, 'asd', 'dsa', 'qwe', 'ewq'")
#adb.checkIfTableExits("Brands")

# print "OK"


#cursor.execute("SELECT TOP 20 pc.Name as CategoryName, p.name as ProductName FROM [SalesLT].[ProductCategory] pc JOIN [SalesLT].[Product] p ON pc.productcategoryid = p.productcategoryid")
#row = cursor.fetchone()
# while row:
#     print (str(row[0]) + " " + str(row[1]))
#     row = cursor.fetchone()