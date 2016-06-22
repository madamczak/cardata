from url_operations import URLOperations
from db_operations import DataBase
from data_operations import DataValidation
from collections import OrderedDict
import datetime

def ConstructBrandsTable(db):
    d = {}
    c = 0
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
                        s = """%d, "%s", "%s", "%s", "%s" """ % (c, it[0], model[0], ver[0], ver[1])
                        print s
                        db.insertStringData("Brands", s)
                        c+=1
                else:
                    s = """%d, "%s", "%s", NULL, "%s" """ % (c, it[0], model[0], model[1])
                    print s
                    db.insertStringData("Brands", s)
                    c+=1
        else:
            s = """%d, "%s", NULL, NULL, "%s" """ % (c, it[0], it[1])
            print s
            db.insertStringData("Brands", s)
            c+=1


# db = DataBase("cars.db")
#
# brandsDict = OrderedDict([('B_Id', "INT"), ('brandName', "TEXT"), ('modelName', "TEXT"), ('version', "TEXT"), ('link', "TEXT")])
# db.createTable('Brands', brandsDict)
#
#
# linksDict = OrderedDict([('L_Id', "INT"), ('B_Id', "TEXT"), ('time', "TEXT"), ('link', "TEXT")])
# db.createTable('Links', brandsDict)

def constructLinkTable(db):
    # switch this to select link from Links
    #current = [l[3] for l in db.readAllData('Links')]
    counter = 0
    current = []
    categories = db.readAllData('Brands')
    for cat in categories:
        links = URLOperations.getLinksFromCategorySite(cat[4])
        for link in links:
            if link not in current:
                s = """ %d, %d, "%s", "%s" """ % (counter, cat[0], str(datetime.datetime.now()), link)
                print s
                db.insertStringData("Links", s)
                counter += 1
                current.append(link)

# categoriesLinks = [l[4] for l in db.readAllData('Brands')]
# for link in categoriesLinks:
# #ConstructBrandsTable(db)
#     for l in URLOperations.getLinksFromCategorySite(link):
#         print l

def constructAllegroCarInsert(b_id, l_id, carDict):
    s = """ "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s" """ % \
                                     (b_id,\
                                      l_id,\
                                      carDict.get(u'Rok produkcji:'),\
                                      carDict.get(u'Przebieg [km]:'), \
                                      carDict.get(u'Moc [KM]:'),\
                                      carDict.get(u'Pojemno\u015b\u0107 silnika [cm3]:'),\
                                      carDict.get(u'Rodzaj paliwa:'),\
                                      carDict.get(u'Kolor:'),\
                                      carDict.get(u'Stan:'),\
                                      carDict.get(u'Liczba drzwi:'),\
                                      carDict.get(u'Skrzynia bieg\xf3w:')
                                      )
    return s

def constructOtomotoCarInsert(b_id, l_id, carDict):
    s = """ "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s" """ % \
                                     (b_id,\
                                      l_id,\
                                      carDict.get(u'Rok produkcji'),\
                                      carDict.get(u'Przebieg'), \
                                      carDict.get(u'Moc'),\
                                      carDict.get(u'Pojemno\u015b\u0107 skokowa'),\
                                      carDict.get(u'Rodzaj paliwa'),\
                                      carDict.get(u'Kolor'),\
                                      carDict.get(u'Stan'),\
                                      carDict.get(u'Liczba drzwi'),\
                                      carDict.get(u'Skrzynia bieg\xf3w')
                                      )
    return s



def ConstructCarsTable(db):
    for entry in db.readAllData('Links'):
        if 'allegro' in entry[3]:
            d = URLOperations.parseAllegroSite(entry[3])
            if not d:
                d = URLOperations.parseAllegroSite2(entry[3])
            try:
                out = DataValidation.validateAllegrCarDict(d)[0]
            except:
                out = False
            if out:
                s = constructAllegroCarInsert(entry[0], entry[1], d)
                print s, DataValidation.validateAllegrCarDict(d)[0]
                db.insertStringData("CarData", s)
            else:
                s = """ "%d", "%s", "%s" """ % (entry[0], str(datetime.datetime.now()), entry[3])
                print s, DataValidation.validateAllegrCarDict(d)[0]
                db.insertStringData("InvalidLinks", s)

        elif 'otomoto' in entry[3]:
            d = URLOperations.parseOtoMotoSite(entry[3])
            try:
                out = DataValidation.validateOtomotoCarDict(d)[0]
            except:
                out = False
            if out:
                s = constructOtomotoCarInsert(entry[0], entry[1], d)
                print s, DataValidation.validateOtomotoCarDict(d)[0]
                db.insertStringData("CarData", s)
            else:
                s = """ "%d", "%s", "%s" """ % (entry[0], str(datetime.datetime.now()), entry[3])
                print s, DataValidation.validateOtomotoCarDict(d)[0]
                db.insertStringData("InvalidLinks", s)

db = DataBase("cars.db")
carDataDict = OrderedDict([('B_Id', "INT"), ('L_Id', "INT"), ('year', "INT"), ('mileage', "INT"), ('power', "INT"),
                           ('capacity', "INT"), ('fuel', "TEXT"), ('color', "TEXT"), ('usedOrNew', "TEXT"), ('doors', "TEXT"), ('gearbox', "TEXT")])

InvalidLinksDict = OrderedDict([('L_Id', "INT"), ('time', "TEXT"), ('link', "TEXT")])

db.createTable('CarData', carDataDict)
db.createTable('InvalidLinks', InvalidLinksDict)
# linksDict = OrderedDict([('L_Id', "INT"), ('B_Id', "TEXT"), ('time', "TEXT"), ('link', "TEXT")])
# db.createTable('Links', linksDict)
# brandsDict = OrderedDict([('B_Id', "INT"), ('brandName', "TEXT"), ('modelName', "TEXT"), ('version', "TEXT"), ('link', "TEXT")])
# db.createTable('Brands', brandsDict)
#
#
# ConstructBrandsTable(db)
import time
now = time.time()
# constructLinkTable(db)



ConstructCarsTable(db)



print "Done in ", time.time() - now, ' seconds'
# for link in categoriesLinks:
# #ConstructBrandsTable(db)
#     for l in URLOperations.getLinksFromCategorySite(link):
#         print l

