import re
import unicodedata

from url_operations import URLOperations
from db_operations import DataBase
import time
from collections import OrderedDict
import datetime
import inspect

from logger import Logger
moduleLogger = Logger.setLogger("cars.py")

def ConstructBrandsTable(db):
    methodName = inspect.stack()[0][3]

    newBrands = 0
    currentBrandsTable = db.readAllData('Brands')
    d = {}

    try:
        c = int(currentBrandsTable[-1][0])
    except:
        c = 0

    moduleLogger.debug("%s - ConstructBrandsTable - Current number of brands: %d." % (methodName, c))

    currentBrandsLinks = [str(el[-1]) for el in currentBrandsTable]

    currentBrands = []
    currentBrandsModels = []

    for brand in currentBrandsTable:
        try:
            currentBrands.append(str(brand[1]))
            currentBrandsModels.append(str(brand[2]))
        except:
            pass

    pattern1 = re.compile(".*\(\d+-")
    pattern2 = re.compile(".*T\d")

    top = URLOperations.getAllBrands("https://allegro.pl/kategoria/samochody-osobowe-4029")
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
                        versionName = unicodedata.normalize('NFKD', ver[0]).encode('ascii','ignore').lower()
                        if ver[1] not in currentBrandsLinks and (pattern1.match(str(versionName)) or pattern2.match(str(versionName))):

                            s = """%d, "%s", "%s", "%s", "%s" """ % (c, it[0], model[0], ver[0], ver[1])
                            moduleLogger.debug("%s - New version found: %s." % (methodName, s))
                            db.insertStringData("Brands", s)
                            c+=1
                            newBrands += 1
                else:
                    if model[1] not in currentBrandsLinks and model[0] not in currentBrandsModels:
                        s = """%d, "%s", "%s", NULL, "%s" """ % (c, it[0], model[0], model[1])
                        moduleLogger.debug("%s - New model found: %s." % (methodName, s))
                        db.insertStringData("Brands", s)
                        c+=1
                        newBrands += 1
        else:
            if it[1] not in currentBrandsLinks and it[0] not in currentBrands:
                s = """%d, "%s", NULL, NULL, "%s" """ % (c, it[0], it[1])
                moduleLogger.debug("%s - New brand found: %s." % (methodName, s))
                db.insertStringData("Brands", s)
                c+=1
                newBrands += 1
    moduleLogger.debug("%s - Number of new brands found: %d." % (methodName, newBrands))
    return newBrands


def constructLinkTable(db):
    methodName = inspect.stack()[0][3]

    newLinks = 0
    linksTable = db.readAllData('Links')

    current = [str(l[3]) for l in linksTable]

    try:
        counter = int(linksTable[-1][0]) + 1
    except:
        counter = 0

    moduleLogger.debug("%s - Current number of links: %d." % (methodName, counter))

    categories = db.readAllData('Brands')
    for cat in categories:
        moduleLogger.debug("%s - Working on category link: %s." % (methodName, cat[4]))
        links = [str(link) for link in URLOperations.getLinksFromCategorySite(cat[4]) if link not in current]
        for link in links:
            moduleLogger.debug("%s - Inserting link: %s to Links table." % (methodName, link))
            s = """ %d, %d, "%s", "%s", "%r" """ % (counter, cat[0], str(datetime.datetime.now()), link, False)
            db.insertStringData("Links", s)
            counter += 1
            newLinks += 1

    moduleLogger.debug("%s - Number of new links: %d." % (methodName, newLinks))
    return newLinks


def _checkDigit(textValue):
    if type(textValue) == int or textValue.isdigit():
        return '%d,' % int(textValue)
    else:
        return '0,'


def _checkString(textValue):
    if type(textValue) == str:
        return '"%s",' % textValue
    else:
        return '"%s",' % unicodedata.normalize('NFKD', textValue).encode('ascii','ignore').lower()


def constructAllegroCarInsert(b_id, l_id, carDict):
    methodName = inspect.stack()[0][3]

    s = """"""
    s+= '%d,' % int(b_id)
    s+= '%d,' % int(l_id)
    s += _checkDigit(carDict.get('rok produkcji:', 0))#
    s += _checkDigit(carDict.get('przebieg [km]:', 0))#
    s += _checkDigit(carDict.get('moc [KM]:', 0))#
    s += _checkDigit(carDict.get('pojemnosc silnika [cm3]:', 0))#

    s+= '"%s",' % str(carDict.get('rodzaj paliwa:', ""))#
    s += _checkString(carDict.get('kolor:', u""))#
    s+= '"%s",' % carDict.get('stan:', "")#
    s+= '"%s",' % str(carDict.get('liczba drzwi:', ""))#

    gearboxValue = carDict.get('skrzynia biegow:', u"")#
    if type(gearboxValue) == str:
        s+= '"%s",' % gearboxValue
    else:
        s+= '"%s",' % unicodedata.normalize('NFKD', gearboxValue).encode('ascii','ignore').lower()

    try:

        s += '"%d"' % int(carDict.get('cena', 0))
    except:
        s += "0"

    moduleLogger.debug("%s - %s " % (methodName, s))

    return s


def constructOtomotoCarInsert(b_id, l_id, carDict):
    methodName = inspect.stack()[0][3]

    s = """"""
    s+= '%d,' % int(b_id)
    s+= '%d,' % int(l_id)
    s+= '%d,' % carDict.get('rok produkcji', 0)
    s+= '%d,' % carDict.get('przebieg', 0)
    s+= '%d,' % carDict.get('moc', 0)
    s+= '%d,' % carDict.get('pojemnosc skokowa', 0)
    s+= '"%s",' % str(carDict.get('rodzaj paliwa', ""))
    s+= '"%s",' % carDict.get('kolor', "")
    s+= '"%s",' % carDict.get('stan', "")
    s+= '"%s",' % str(carDict.get('liczba drzwi', ""))
    s+= '"%s",' % str(carDict.get('skrzynia biegow', ""))
    try:

        s += '"%d"' % int(carDict.get('cena', 0))
    except:
        s += "0"

    moduleLogger.debug("%s - %s" % (methodName, s))

    return s


def _scoreFour(carDict):
    score = 0

    for val in carDict.values():
        if val == 0 or val == "":
            score += 1

    return score < 5


def _verifyDictionary(carDict):
    return (carDict and _scoreFour(carDict))


def ConstructCarsTable(db):
    methodName = inspect.stack()[0][3]

    newCars = 0

    for entry in db.readAllData('Links'):
        if entry[4] == 'False':
            moduleLogger.debug("%s - Link has not been parsed. Link: %s" % (methodName, entry[3]))

            if 'allegro' in entry[3]:
                d = URLOperations.parseAllegroSite(entry[3])

                if _verifyDictionary(d):
                    moduleLogger.debug("%s - Verified positively. Will be inserted in CarData table." % methodName)
                    s = constructAllegroCarInsert(entry[1], entry[0], d)
                    db.insertStringData("CarData", s)
                    newCars += 1
                else:
                    moduleLogger.debug("%s - Verified negatively. Will be inserted in InvalidLinks table." % methodName)
                    s = """ "%d", "%s", "%s", "True" """ % (entry[0], str(datetime.datetime.now()), entry[3])
                    db.insertStringData("InvalidLinks", s)

            elif 'otomoto' in entry[3]:

                d = URLOperations.parseOtoMotoSite2(entry[3])
                if not d:
                    d = URLOperations.parseOtoMotoSite(entry[3])

                if _verifyDictionary(d):
                    moduleLogger.debug("%s - Verified positively. Will be inserted in CarData table." % methodName)
                    s = constructOtomotoCarInsert(entry[1], entry[0], d)
                    db.insertStringData("CarData", s)
                    newCars += 1
                else:
                    moduleLogger.debug("%s - Verified negatively. Will be inserted in InvalidLinks table.")
                    s = """ "%d", "%s", "%s", "True" """ % (methodName, entry[0], str(datetime.datetime.now()), entry[3])
                    db.insertStringData("InvalidLinks", s)

            db.executeSqlCommand("""UPDATE Links SET parsed = "True" WHERE link = "%s" """ % entry[3])
        #else:
            moduleLogger.debug("%s - Link has been parsed. Link: %s" % (methodName, entry[3]))

    return newCars


def constructDBTables(db):
    methodName = inspect.stack()[0][3]

    brandsDict = OrderedDict(
        [('B_Id', "INT"), ('brandName', "TEXT"), ('modelName', "TEXT"), ('version', "TEXT"), ('link', "TEXT")])
    linksDict = OrderedDict([('L_Id', "INT"), ('B_Id', "INT"), ('time', "TEXT"), ('link', "TEXT"), ('parsed', 'BOOL')])
    InvalidLinksDict = OrderedDict([('L_Id', "INT"), ('time', "TEXT"), ('link', "TEXT"), ('parsed', 'BOOL')])
    carDataDict = OrderedDict([('B_Id', "INT"), ('L_Id', "INT"), ('year', "INT"), ('mileage', "INT"), ('power', "INT"),
                               ('capacity', "INT"), ('fuel', "TEXT"), ('color', "TEXT"), ('usedOrNew', "TEXT"),
                               ('doors', "TEXT"), ('gearbox', "TEXT"), ('price', "INT")])
    db.createTable('Brands', brandsDict)
    db.createTable('Links', linksDict)
    db.createTable('CarData', carDataDict)
    db.createTable('InvalidLinks', InvalidLinksDict)


def collect():
    methodName = inspect.stack()[0][3]

    moduleLogger.info('%s - Started: %s' % (methodName, datetime.datetime.now().strftime("%d-%m-%Y %H:%M")))

    db = DataBase("cars_work4.db")
    constructDBTables(db)

    while True:
        beginBrands = time.time()
        currentDate = datetime.datetime.now()
        newBrands = ConstructBrandsTable(db)
        moduleLogger.info("%s - Brands done. %s. Number of new brands: %d. Done in %d seconds." % (methodName,
            datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), newBrands, time.time() - beginBrands))

        beginLinks = time.time()
        newLinks = constructLinkTable(db)
        moduleLogger.info("%s - Links done.  %s. Number of new links:  %d. Done in %d seconds." % (methodName,
            datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), newLinks, time.time() - beginLinks))
        now = time.time()

        beginCars = time.time()
        newCars = ConstructCarsTable(db)
        moduleLogger.info("%s - Cars done.   %s. Number of new cars:   %d. Done in %d seconds." % (methodName,
            datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), newCars, time.time() - beginCars))

        message = '\n%s\n' % currentDate.strftime("%d-%m-%Y %H:%M")
        message += "New Brands: %d\nNew Links:  %d\nNew Cars:   %d\n" % (newBrands, newLinks, newCars)
        message += "All done in %d seconds\n\n" % (time.time() - now)
        moduleLogger.info("%s - %s" % (methodName, message))


if __name__ == "__main__":
    collect()
