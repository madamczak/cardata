from url_operations import URLOperations
from db_operations import DataBase
import time
from collections import OrderedDict
import datetime

def ConstructBrandsTable(db):
    d = {}
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
                            print s
                            db.insertStringData("Brands", s)
                            c+=1
                        else:
                            print 'Skipping %s beacause it is already present in Brands table.' % ver[1]
                else:
                    if model[1] not in currentBrandsLinks:
                        s = """%d, "%s", "%s", NULL, "%s" """ % (c, it[0], model[0], model[1])
                        print s
                        db.insertStringData("Brands", s)
                        c+=1
                    else:
                        print 'Skipping %s beacause it is already present in Brands table.' % model[1]
        else:
            if it[1] not in currentBrandsLinks:
                s = """%d, "%s", NULL, NULL, "%s" """ % (c, it[0], it[1])
                print s
                db.insertStringData("Brands", s)
                c+=1
            else:
                print 'Skipping %s beacause it is already present in Brands table.' % it[1]


def constructLinkTable(db):
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
                print s
                db.insertStringData("Links", s)
                counter += 1
                current.append(str(link))
            else:
                print 'Skipping %s beacause it is already present in Links table.' % link


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
    for entry in db.readAllData('Links'):
        if entry[4] == 'False' :
            if 'allegro' in entry[3]:
                d = URLOperations.parseAllegroSite(entry[3])
                if not d:
                    d = URLOperations.parseAllegroSite2(entry[3])

                print d

                if d:
                    s = constructAllegroCarInsert(entry[0], entry[1], d)
                    print s
                    db.insertStringData("CarData", s)
                else:
                    s = """ "%d", "%s", "%s" """ % (entry[0], str(datetime.datetime.now()), entry[3])
                    print s
                    db.insertStringData("InvalidLinks", s)

            elif 'otomoto' in entry[3]:
                d = URLOperations.parseOtoMotoSite(entry[3])
                if not d:
                    d = URLOperations.parseOtoMotoSite2(entry[3])
                print d
                if d:
                    s = constructOtomotoCarInsert(entry[0], entry[1], d)
                    print s
                    db.insertStringData("CarData", s)
                else:
                    s = """ "%d", "%s", "%s" """ % (entry[0], str(datetime.datetime.now()), entry[3])
                    print s
                    db.insertStringData("InvalidLinks", s)

            db.executeSqlCommand("""UPDATE Links SET parsed = "True" WHERE link = "%s" """ % entry[3])
        else:
            print "Link %s was already parsed." % entry[3]



def collect():

    db = DataBase("cars.db")

    brandsDict = OrderedDict([('B_Id', "INT"), ('brandName', "TEXT"), ('modelName', "TEXT"), ('version', "TEXT"), ('link', "TEXT")])
    linksDict = OrderedDict([('L_Id', "INT"), ('B_Id', "TEXT"), ('time', "TEXT"), ('link', "TEXT"), ('parsed', 'TEXT')])
    InvalidLinksDict = OrderedDict([('L_Id', "INT"), ('time', "TEXT"), ('link', "TEXT"), ('parsed', 'TEXT')])
    carDataDict = OrderedDict([('B_Id', "INT"), ('L_Id', "INT"), ('year', "TEXT"), ('mileage', "TEXT"), ('power', "TEXT"),
                             ('capacity', "TEXT"), ('fuel', "TEXT"), ('color', "TEXT"), ('usedOrNew', "TEXT"), ('doors', "TEXT"), ('gearbox', "TEXT")])

    now = time.time()
    db.createTable('Brands', brandsDict)
    db.createTable('Links', linksDict)
    db.createTable('CarData', carDataDict)
    db.createTable('InvalidLinks', InvalidLinksDict)

    ConstructBrandsTable(db)
    print "Brands done"
    constructLinkTable(db)
    print "Links done"
    ConstructCarsTable(db)
    print 'Car data done'

    print "All done in ", time.time() - now, ' seconds'


collect()


