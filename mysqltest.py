# import pyodbc
# server = 'cloudcardatapostgres.postgres.database.azure.com'
# database = 'postgres'
# username = 'madamczak@cloudcardatapostgres'
# password = 'QAZwsx11!'
# cnxn = pyodbc.connect('DRIVER={PostgreSQL};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
import psycopg2

# Update connection string information obtained from the portal
host = "cloudcardatapostgres.postgres.database.azure.com"
user = "madamczak@cloudcardatapostgres"
dbname = "postgres"
password = "QAZwsx11!"
sslmode = "require"

# Construct connection string
conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)
conn = psycopg2.connect(conn_string)
print "Connection established"

cursor = conn.cursor()

# Drop previous table of same name if one exists
cursor.execute("DROP TABLE IF EXISTS inventory;")
print "Finished dropping table (if existed)"

# Create table
cursor.execute("CREATE TABLE inventory (id serial PRIMARY KEY, name VARCHAR(50), quantity INTEGER);")
print "Finished creating table"

# Insert some data into table
cursor.execute("INSERT INTO inventory (name, quantity) VALUES (%s, %s);", ("banana", 150))
cursor.execute("INSERT INTO inventory (name, quantity) VALUES (%s, %s);", ("orange", 154))
cursor.execute("INSERT INTO inventory (name, quantity) VALUES (%s, %s);", ("apple", 100))
print "Inserted 3 rows of data"

# Cleanup
conn.commit()
cursor.close()
conn.close()



# cursor = cnxn.cursor()
# cursor.execute("SELECT @@version;")
# row = cursor.fetchone()
# while row:
#     print row
#     row = cursor.fetchone()

# import pyodbc
# conn_str = (
#     "DRIVER={PostgreSQL Unicode};"
#     "DATABASE=postgres;"
#     "UID=madamczak@cloudcardatapostgres;"
#     "PWD=QAZwsx11!;"
#     "SERVER=cloudcardatapostgres.postgres.database.azure.com;"
#     "PORT=5432;"
#     )
# conn = pyodbc.connect(conn_str)
# crsr = conn.execute("SELECT 123 AS n")
# row = crsr.fetchone()
# print(row)
# crsr.close()
# conn.close()

#
# import pyodbc
#
# dsn = 'cloudcardatadatasource'
#
# user = 'madamczak@cloudcardataserver'
#
# password = 'QAZwsx11!'
#
# database = 'cloudcardata'
#
# connString = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (dsn,user,password,database)
#
# conn = pyodbc.connect(connString) #If anything went wrong during configuration, it will happen here
#
# cursor = conn.cursor()
#
# cursor.execute('select * from Brands')
#
# row = cursor.fetchone()
#
# if row:
#     print(row)
#
# conn.close()
# print "Done"
# quit()



# import pyodbc
# server = 'tcp:cloudcardataserver.database.windows.net'
# database = 'cloudcardata'
# username = 'madamczak@cloudcardataserver'
# password = 'QAZwsx11!'
# cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
# cursor = cnxn.cursor()
# cursor.execute("SELECT @@version;")
# row = cursor.fetchone()
# while row:
#     print row
#     row = cursor.fetchone()


# import pymssql
# conn = pymssql.connect(server='cloudcardataserver.database.windows.net', user='madamczak@cloudcardataserver', password='QAZwsx11!', database='cloudcardata')
#
# cursor = conn.cursor()
# cursor.execute('SELECT * FROM Brands')
# row = cursor.fetchone()
# while row:
#     print str(row[0]) + " " + str(row[1]) + " " + str(row[2])
#     row = cursor.fetchone()
# import pyodbc
#
# # Obtain connection string information from the portal
# # config = {
# #   'host':'myserver4demo.mysql.database.azure.com',
# #   'user':'myadmin@myserver4demo',
# #   'password':'yourpassword',
# #   'database':'quickstartdb'
# # }
#
# # config = {
# #   'host':'tcp:cloudcardataserver.database.windows.net',
# #   'port':"1433",
# #   'user':'madamczak',
# #   'password':'QAZwsx11!',
# #   'database':'cloudcardata'
# # }
#
# # Construct connection string
# try:
#    conn = pyodbc.connector.connect(**config)
#    print("Connection established")
# except mysql.connector.Error as err:
#   if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
#     print("Something is wrong with the user name or password")
#   elif err.errno == errorcode.ER_BAD_DB_ERROR:
#     print("Database does not exist")
#   else:
#     print(err)
# else:
#   cursor = conn.cursor()
#
#   # Drop previous table of same name if one exists
#   cursor.execute("DROP TABLE IF EXISTS inventory;")
#   print("Finished dropping table (if existed).")
#
#   # Create table
#   cursor.execute("CREATE TABLE inventory (id serial PRIMARY KEY, name VARCHAR(50), quantity INTEGER);")
#   print("Finished creating table.")
#
#   # Insert some data into table
#   cursor.execute("INSERT INTO inventory (name, quantity) VALUES (%s, %s);", ("banana", 150))
#   print("Inserted",cursor.rowcount,"row(s) of data.")
#   cursor.execute("INSERT INTO inventory (name, quantity) VALUES (%s, %s);", ("orange", 154))
#   print("Inserted",cursor.rowcount,"row(s) of data.")
#   cursor.execute("INSERT INTO inventory (name, quantity) VALUES (%s, %s);", ("apple", 100))
#   print("Inserted",cursor.rowcount,"row(s) of data.")
#
#   # Cleanup
#   conn.commit()
#   cursor.close()
#   conn.close()
#   print("Done.")