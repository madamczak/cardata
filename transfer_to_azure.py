from OperationUtils.db_operations import DataBase
from OperationUtils.azure_db_operations import AzureDB
from collections import OrderedDict

import pyodbc


# server = 'cloudcardataserver.database.windows.net'
# database = 'cloudcardata'
# username = 'madamczak'
# password = 'QAZwsx11!'
# driver= '{ODBC Driver 11 for SQL Server}'
dsn = 'cloudcardatadatasource'
user = 'madamczak@cloudcardataserver'
password = 'QAZwsx11!'
database = 'cloudcardata'
# config = {
#   'host':'cloudcardataserver.database.windows.net',
#   'user':'madamczak',
#   'password':'QAZwsx11!',
#   'database':'cloudcardata'
# }

# conn = mysql.connector.connect(**config)
# cnxn = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
# cursor = cnxn.cursor()


sqliteDB = DataBase("refactor_test6.db")

host = "cloudcardatapostgres.postgres.database.azure.com"
user = "madamczak@cloudcardatapostgres"
dbname = "postgres"
password = "QAZwsx11!"
sslmode = "require"

adb = AzureDB(host, user, dbname, password, sslmode)

brds = sqliteDB.readAllData("Brands")

class AzureTransfer(object):
    def __init__(self, sqliteDbPath, host, user, dbname, password, sslmode):
        self.azureDb = AzureDB( host, user, dbname, password, sslmode)
        self.sqliteDb = DataBase(sqliteDbPath)

    def transferToAzure(self):
        self.transferBrands()
        self.transferCars()

    def transferBrands(self):
        brandsDict = OrderedDict(
            [('b_id', "INT"), ('brandname', "TEXT"), ('modelname', "TEXT"), ('version', "TEXT"), ('link', "TEXT")])

        self.azureDb.createTable("cars_brand", brandsDict, "b_id")
        for brand in self.sqliteDb.readAllDataGenerator("Brands"):
            string = """ """

            #brandString = ", ".join([str(element) for element in brand])
            #This has to be that long and bad looking because of Kia Cee'd
            for el in brand:
                if type(el) == int:
                    string += str(el)
                    string += ","
                else:
                    if el is not None and "'" in el:
                        string += "'%s''%s'," % (el.split("'")[0], el.split("'")[1])
                    else:
                        string += "'%s'," % el
            print string[:-1]
            adb.insertDataIfIDIsNotPresentInTable("cars_brand", string[:-1], "B_Id")


    def transferCars(self):
        carDataDict = OrderedDict(
            [('B_Id', "INT"), ('L_Id', "INT"), ('year', "INT"), ('mileage', "INT"), ('power', "INT"),
             ('capacity', "INT"), ('fuel', "TEXT"), ('color', "TEXT"), ('usedOrNew', "TEXT"),
             ('doors', "TEXT"), ('gearbox', "TEXT"), ('price', "INT"), ('time', "TEXT"), ('country', "TEXT")])

        self.azureDb.createTable("cars_car2", carDataDict, "L_Id")

        for car in self.sqliteDb.readAllDataGenerator("CarData", where="WHERE L_Id > 0"):
            carString = ""
            insert = True
            for element in car:
                if type(element) == int:
                    carString += str(element) + ", "
                elif type(element) == long:
                    insert = False
                    break

                else:
                    carString += "'" + element + "', "


            #carString = ", ".join([str(element) for element in car])
            carString += " 'PL'"
            if insert:
                adb.insertDataIfIDIsNotPresentInTable("cars_car2", carString, "L_Id")
                print carString



trsfr = AzureTransfer("refactor_test6.db", host, user, dbname, password, sslmode)
trsfr.transferCars()
