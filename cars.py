from data_operations import DataValidation, NumpyArrayOperations
from plots import Plots
from url_operations import URLOperations
from db_operations import DataBase
import time
from collections import OrderedDict
import datetime

def ConstructBrandsTable(db):
    newBrands = 0
    d = {}

    try:
        c = max([int(str(el[0])) for el in db.readAllData('Brands')])
    except:
        c = 0

    currentBrandsLinks = [str(el[-1]) for el in db.readAllData('Brands')]

    top = URLOperations.getAllBrands("http://allegro.pl/samochody-osobowe-4029")
    for it in top.items():
        d[it[0]] = {}
        models = URLOperations.getAllBrands(it[1])
        if not all([k in top.keys() for k in models.keys()]):
            for model in models.items():
                d[it[0]][(model[0])] = []
                versions = URLOperations.getAllBrands(model[1])
                if not all([k in models.keys() for k in versions.keys()]):
                    for ver in versions.items():
                        d[it[0]][(model[0])].append(ver)
                        if ver[1] not in currentBrandsLinks:
                            s = """%d, "%s", "%s", "%s", "%s" """ % (c, it[0], model[0], ver[0], ver[1])
                            db.insertStringData("Brands", s)
                            c+=1
                            newBrands += 1
                else:
                    if model[1] not in currentBrandsLinks:
                        s = """%d, "%s", "%s", NULL, "%s" """ % (c, it[0], model[0], model[1])
                        db.insertStringData("Brands", s)
                        c+=1
                        newBrands += 1
        else:
            if it[1] not in currentBrandsLinks:
                s = """%d, "%s", NULL, NULL, "%s" """ % (c, it[0], it[1])
                db.insertStringData("Brands", s)
                c+=1
                newBrands += 1

    return newBrands

def constructLinkTable(db):
    newLinks = 0
    current = [str(l[3]) for l in db.readAllData('Links')]

    try:
        counter = max([int(l[0]) for l in db.readAllData('Links')]) + 1
    except ValueError:
        counter = 0

    categories = db.readAllData('Brands')
    for cat in categories:
        links = URLOperations.getLinksFromCategorySite(cat[4])
        for link in links:
            if link not in current:
                s = """ %d, %d, "%s", "%s", "%r" """ % (counter, cat[0], str(datetime.datetime.now()), link, False)
                db.insertStringData("Links", s)
                counter += 1
                newLinks += 1
                current.append(str(link))
    return newLinks

def constructAllegroCarInsert(b_id, l_id, carDict):
    s = """ "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s" """ % \
                                     (b_id,\
                                      l_id,\
                                      carDict.get('rok produkcji:'),\
                                      carDict.get('przebieg [km]:'), \
                                      carDict.get('moc [km]:'),\
                                      carDict.get('pojemnosc silnika [cm3]:'),\
                                      carDict.get('rodzaj paliwa:'),\
                                      carDict.get('kolor:'),\
                                      carDict.get('stan:'),\
                                      carDict.get('liczba drzwi:'),\
                                      carDict.get('skrzynia biegow:')
                                      )
    return s

def constructOtomotoCarInsert(b_id, l_id, carDict):
    s = """ "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s" """ % \
                                     (b_id,\
                                      l_id,\
                                      carDict.get('rok produkcji'),\
                                      carDict.get('przebieg'), \
                                      carDict.get('moc'),\
                                      carDict.get('pojemnosc skokowa'),\
                                      carDict.get('rodzaj paliwa'),\
                                      carDict.get('kolor'),\
                                      carDict.get('stan'),\
                                      carDict.get('liczba drzwi'),\
                                      carDict.get('skrzynia biegow')
                                      )
    return s



def ConstructCarsTable(db):
    newCars = 0
    for entry in db.readAllData('Links'):
        if entry[4] == 'False' :
            if 'allegro' in entry[3]:
                d = URLOperations.parseAllegroSite(entry[3])
                if not d:
                    d = URLOperations.parseAllegroSite2(entry[3])

                if d:
                    s = constructAllegroCarInsert(entry[1], entry[0], d)
                    db.insertStringData("CarData", s)
                    newCars += 1
                else:
                    s = """ "%d", "%s", "%s" """ % (entry[0], str(datetime.datetime.now()), entry[3])
                    db.insertStringData("InvalidLinks", s)

            elif 'otomoto' in entry[3]:
                d = URLOperations.parseOtoMotoSite(entry[3])
                if not d:
                    d = URLOperations.parseOtoMotoSite2(entry[3])
                if d:
                    s = constructOtomotoCarInsert(entry[1], entry[0], d)
                    db.insertStringData("CarData", s)
                    newCars += 1
                else:
                    s = """ "%d", "%s", "%s", "True" """ % (entry[0], str(datetime.datetime.now()), entry[3])
                    db.insertStringData("InvalidLinks", s)

            db.executeSqlCommand("""UPDATE Links SET parsed = "True" WHERE link = "%s" """ % entry[3])
    return newCars


def collect():

    db = DataBase("cars_work.db")

    brandsDict = OrderedDict([('B_Id', "INT"), ('brandName', "TEXT"), ('modelName', "TEXT"), ('version', "TEXT"), ('link', "TEXT")])
    linksDict = OrderedDict([('L_Id', "INT"), ('B_Id', "TEXT"), ('time', "TEXT"), ('link', "TEXT"), ('parsed', 'TEXT')])
    InvalidLinksDict = OrderedDict([('L_Id', "INT"), ('time', "TEXT"), ('link', "TEXT"), ('parsed', 'TEXT')])
    carDataDict = OrderedDict([('B_Id', "INT"), ('L_Id', "INT"), ('year', "TEXT"), ('mileage', "TEXT"), ('power', "TEXT"),
                             ('capacity', "TEXT"), ('fuel', "TEXT"), ('color', "TEXT"), ('usedOrNew', "TEXT"), ('doors', "TEXT"), ('gearbox', "TEXT")])

    db.createTable('Brands', brandsDict)
    db.createTable('Links', linksDict)
    db.createTable('CarData', carDataDict)
    db.createTable('InvalidLinks', InvalidLinksDict)
    while True:
        now = time.time()
        currentDate = datetime.datetime.now()
        newBrands = ConstructBrandsTable(db)
        print "Brands done. %s" % datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        newLinks = constructLinkTable(db)
        print "Links done. %s" % datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        newCars = ConstructCarsTable(db)
        print "Cars done. %s\n\n" % datetime.datetime.now().strftime("%d-%m-%Y %H:%M")

        message = '%s\n' % currentDate.strftime("%d-%m-%Y %H:%M")
        message += "New Brands: %d\nNew Links: %d\nNew Cars: %d\n" % (newBrands, newLinks, newCars)
        message += "All done in %f seconds\n\n" % (time.time() - now)

        with open('logTxt.txt', "a") as myfile:
            myfile.write(message)
        print message


db = DataBase("cars.db")

print db.getAllBrandIdsOfParticularBrand('Volkswagen')
print db.getAllBrandIdsOfParticularModel('Passat')
print db.getVersionID('II (1983-1985)')

# brandsDict = OrderedDict([('B_Id', "INT"), ('brandName', "TEXT"), ('modelName', "TEXT"), ('version', "TEXT"), ('link', "TEXT")])
# db.createTable('Brands', brandsDict)
#collect()

#ConstructBrandsTable(db)
# data = db.readAllData('CarData')
# years = []
# miles = []
# for i in data:
#     if i[3] != u'None' and i[2] != u'None' and i[3] and int(DataValidation.stripDecimalValue(i[3])) < 900000 and int(DataValidation.stripDecimalValue(i[3])) > 50:
#         years.append(int(DataValidation.stripDecimalValue(i[2])))
#         miles.append(int(DataValidation.stripDecimalValue(i[3])))
#         #data.append((int(DataValidation.stripDecimalValue(i[2])), int(DataValidation.stripDecimalValue(i[3]))))
#
# Plots.drawAverageMileagePlot(miles, years, range(1980, 2017))

#collect()



