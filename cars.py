import re

from OperationUtils.data_operations import DataCleaning
from OperationUtils.url_operations import URLOperations
from OperationUtils.db_operations import DataBase
import time
from collections import OrderedDict
import datetime
import inspect

from OperationUtils.logger import Logger
moduleLogger = Logger.setLogger("cars.py")


def ConstructBrandsTable(db, limit=2000):
    methodName = inspect.stack()[0][3]

    newBrands = 0
    d = {}

    c = db.getMaxFromColumnInTable("b_id", "cars_brand") + 1

    moduleLogger.debug("%s - ConstructBrandsTable - Current number of brands: %d." % (methodName, c - 1))

    pattern1 = re.compile(".*\(\d+-")
    pattern2 = re.compile(".*T\d")

    top = URLOperations.getAllBrands("https://allegro.pl/kategoria/samochody-osobowe-4029")
    for it in top.items():

        if newBrands > limit:
            moduleLogger.info("%s - Collected %d brands." % (methodName, newBrands))
            break

        d[it[0]] = {}
        models = URLOperations.getAllBrands(it[1])
        if not all([k in top.keys() for k in models.keys()]):
            for model in models.items():
                d[it[0]][(model[0])] = []
                versions = URLOperations.getAllBrands(model[1])
                if not all([k in models.keys() for k in versions.keys()]):
                    for ver in versions.items():
                        d[it[0]][(model[0])].append(ver)
                        versionName = DataCleaning.normalize(ver[0])
                        if not db.valueIsPresentInColumnOfATable(ver[1], 'link', "cars_brand") \
                                and (pattern1.match(str(versionName)) or pattern2.match(str(versionName))):

                            s = """%d, "%s", "%s", "%s", "%s" """ % (c, it[0], model[0], ver[0], ver[1])
                            moduleLogger.debug("%s - New version found: %s." % (methodName, s))
                            db.insertStringData("cars_brand", s)
                            c+=1
                            newBrands += 1
                else:
                    if not db.valueIsPresentInColumnOfATable(model[1], 'link', "cars_brand") \
                            and not db.valueIsPresentInColumnOfATable(model[0], 'modelname', "cars_brand"):
                        s = """%d, "%s", "%s", NULL, "%s" """ % (c, it[0], model[0], model[1])
                        moduleLogger.debug("%s - New model found: %s." % (methodName, s))
                        db.insertStringData("cars_brand", s)
                        c+=1
                        newBrands += 1
        else:
            if not db.valueIsPresentInColumnOfATable(it[1], 'link', "cars_brand") \
                    and not db.valueIsPresentInColumnOfATable(it[0], 'brandname', "cars_brand"):
                s = """%d, "%s", NULL, NULL, "%s" """ % (c, it[0], it[1])
                moduleLogger.debug("%s - New brand found: %s." % (methodName, s))
                db.insertStringData("cars_brand", s)
                c+=1
                newBrands += 1
    moduleLogger.debug("%s - Number of new brands found: %d." % (methodName, newBrands))
    return newBrands


def constructLinkTable(db, limit=1000):
    methodName = inspect.stack()[0][3]

    newLinks = 0
    counter = db.getMaxFromColumnInTable("l_id", "links") + 1

    moduleLogger.debug("%s - Current number of links: %d." % (methodName, counter - 1))

    categories = db.readAllDataGenerator('cars_brand')

    for cat in categories:
        if newLinks > limit:
            moduleLogger.info("%s - Collected %d links." % (methodName, limit))
            break

        #moduleLogger.info("%s - Currently getting links from category with B_id: %d ." % (methodName, cat[0]))
        moduleLogger.info("%s - %s - Working on category with id: %s, link: %s." %
                          (datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), methodName, cat[0], cat[4]))
        links = []
        for link in URLOperations.getLinksFromCategorySite(cat[4]):
            try:
                lnk = str(link)
                #get new way of inserting links into a table
                #do not check it here, collect all of them and after that insert them to database

                #multi threaded checking if link is in the table
                if not db.valueIsPresentInColumnOfATable(lnk, 'link', "links"):
                    links.append(lnk)
            except:
                moduleLogger.info("%s - Unable to add link to list: %s" % (methodName, link))
                continue

        for link in links:
            moduleLogger.debug("%s - Inserting link: %s to Links table." % (methodName, link))
            s = """ %d, %d, "%s", "%s", "%r" """ % (counter, cat[0], str(datetime.datetime.now()), link, False)
            db.insertStringData("links", s)
            counter += 1
            newLinks += 1


        if links:
            moduleLogger.info("%s - Number of new links: %d." % (methodName, len(links)))
        else:
            moduleLogger.info("%s - There weren't any new links in category with b_id: %d" % (methodName, cat[0]))

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
        return '"%s",' % DataCleaning.normalize(textValue)

def _getAllegroDictRegexKey(text, carDict):
    regex = re.compile("%s .+:" % text)

    for key in carDict.keys():
        if text in key:
            value = _checkDigit(carDict.get(re.match(regex, key).group(), 0))
            return value


def constructAllegroCarInsert(b_id, l_id, carDict):
    methodName = inspect.stack()[0][3]

    s = """"""
    s += '%d,' % int(b_id)
    s += '%d,' % int(l_id)
    s += _checkDigit(carDict.get('rok produkcji:', 0))

    s += _getAllegroDictRegexKey("przebieg", carDict)

    #TODO: use regex here
    s += _getAllegroDictRegexKey("moc", carDict)

    #s += _checkDigit(carDict.get('pojemnosc silnika [cm3]:', 0))

    s += _getAllegroDictRegexKey("pojemnosc silnika", carDict)
    s += '"%s",' % DataCleaning.internationalizeFuel(str(carDict.get('rodzaj paliwa:', "")))
    s += '"%s",' % DataCleaning.internationalizeColor(_checkString(carDict.get('kolor:', u"")))
    s += '"%s",' % DataCleaning.internationalizeState(carDict.get('stan:', ""))
    s += '"%s",' % DataCleaning.normalizeNumberOfDoors(str(carDict.get('liczba drzwi:', "")))

    gearboxValue = carDict.get('skrzynia biegow:', u"")#
    if type(gearboxValue) == str:
        s += '"%s",' % DataCleaning.internationalizeGearbox(gearboxValue)
    else:
        s += '"%s",' % DataCleaning.internationalizeGearbox(DataCleaning.normalize(gearboxValue))

    try:

        s += '"%d",' % int(carDict.get('cena', 0))
    except:
        s += "0,"

    s += '"%s"' % str(datetime.datetime.now())

    moduleLogger.debug("%s - %s " % (methodName, s))

    return s


def constructOtomotoCarInsert(b_id, l_id, carDict):
    methodName = inspect.stack()[0][3]

    s = """"""
    s += '%d,' % int(b_id)
    s += '%d,' % int(l_id)
    s += '%d,' % carDict.get('rok produkcji', 0)
    s += '%d,' % carDict.get('przebieg', 0)
    s += '%d,' % carDict.get('moc', 0)
    s += '%d,' % carDict.get('pojemnosc skokowa', 0)
    s += '"%s",' % DataCleaning.internationalizeFuel(str(carDict.get('rodzaj paliwa', "")))
    s += '"%s",' % DataCleaning.internationalizeColor(carDict.get('kolor', ""))
    s += '"%s",' % DataCleaning.internationalizeState(carDict.get('stan', ""))
    s += '"%s",' % DataCleaning.normalizeNumberOfDoors(str(carDict.get('liczba drzwi', "")))
    s += '"%s",' % DataCleaning.internationalizeGearbox(str(carDict.get('skrzynia biegow', "")))
    try:

        s += '"%d",' % int(carDict.get('cena', 0))
    except:
        s += "0,"

    s += '"%s"' % str(datetime.datetime.now())

    moduleLogger.debug("%s - %s" % (methodName, s))

    return s

def logDebugDict(dct, param):
    msg = ""
    for k,v in dct.items():
        msg += "%s - %s" % (k, v)

    moduleLogger.debug("Car does not have %s parsed.\n Rest of dictionary: %s\n" % (param, msg))

#TODO refactor
def _verifyDictionary(carDict):
    #verify keys
    if carDict and len(carDict.keys()) < 15:
        if carDict.get('cena') is not None and carDict.get('cena') == 0:
            logDebugDict(carDict, "Price")
            return False

        if ":" not in carDict.keys()[0]:
            if carDict.get('rok produkcji') is not None and carDict.get('rok produkcji') == 0:
                logDebugDict(carDict, "Year of production")
                return False
            if carDict.get('przebieg') is not None:
                if carDict.get('przebieg') == 0:
                    logDebugDict(carDict, "Mileage")
                    return False
            else:
                return False
            if carDict.get('moc') is not None:
                if carDict.get('moc') == 0:
                    logDebugDict(carDict, "power")
                    return False
            else:
                return False
            if carDict.get('pojemnosc skokowa') is not None:
                if carDict.get('pojemnosc skokowa') == 0:
                    logDebugDict(carDict, "capacity")
                    return False
            else:
                return False
        else:
            if carDict.get('rok produkcji:') is not None:
                if carDict.get('rok produkcji:') == 0:
                    logDebugDict(carDict, "Year of production")
                    return False
            else:
                return False

            if carDict.get(_getAllegroDictRegexKey("przebieg", carDict)) is not None:
                if carDict.get(_getAllegroDictRegexKey("przebieg", carDict)) == 0:
                    logDebugDict(carDict, "Mileage")
                    return False
            else:
                return False

            if carDict.get(_getAllegroDictRegexKey("moc [km]:", carDict)) is not None:
                if carDict.get(_getAllegroDictRegexKey("moc", carDict)) == 0:
                    logDebugDict(carDict, "power")
                    return False
            else:
                return False

            if carDict.get(_getAllegroDictRegexKey("pojemnosc silnika", carDict)) is not None:
                if carDict.get(_getAllegroDictRegexKey("pojemnosc silnika", carDict)) == 0:
                    logDebugDict(carDict, "capacity")
                    return False
            else:
                return False


        return True

    else:
        moduleLogger.debug("Car dictionary has less than 15 keys. Number of keys: %d" % len(carDict))
        return False


def ConstructCarsTable(db, limit=300000):
    methodName = inspect.stack()[0][3]

    newCars = 0
    currentB_id = ""

    counter = 0
    for entry in db.readAllDataGenerator('links', where='WHERE parsed = "False"'):
        if counter > limit:
            moduleLogger.info("%s - Collected %d cars." % (methodName, limit))
            break
        counter += 1

        if currentB_id != entry[1]:
            currentB_id = entry[1]
            moduleLogger.info("%s - %s - Currently working on links from %s b_id. It has %s l_id" %
                              (datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), methodName, entry[1], entry[0]))

        if entry[4] == 'False':

            if 'allegro' in entry[3]:
                d = URLOperations.parseAllegroSite(entry[3])

                if _verifyDictionary(d):
                    moduleLogger.debug("%s - Verified positively. Will be inserted in cars_car table." % methodName)
                    s = constructAllegroCarInsert(entry[1], entry[0], d)
                    db.insertStringData("cars_car", s)
                    newCars += 1
                else:
                    moduleLogger.debug("%s - Verified negatively. Will be inserted in InvalidLinks table." % methodName)
                    s = """ "%d", "%s", "%s", "True" """ % (entry[0], str(datetime.datetime.now()), entry[3])
                    db.insertStringData("invalidlinks", s)

            elif 'otomoto' in entry[3]:

                d = URLOperations.parseOtoMotoSite2(entry[3])
                if not d:
                    d = URLOperations.parseOtoMotoSite(entry[3])

                if _verifyDictionary(d):
                    moduleLogger.debug("%s - Verified positively. Will be inserted in CarData table." % methodName)
                    s = constructOtomotoCarInsert(entry[1], entry[0], d)
                    db.insertStringData("cars_car", s)
                    newCars += 1
                else:
                    moduleLogger.debug("%s - Verified negatively. Will be inserted in InvalidLinks table." % methodName)
                    s = """ "%d", "%s", "%s", "True" """ % (entry[0], str(datetime.datetime.now()), entry[3])
                    db.insertStringData("invalidlinks", s)

            db.executeSqlCommand("""UPDATE links SET parsed = "True" WHERE link = "%s" """ % entry[3])
    return newCars


def constructDBTables(db):
    methodName = inspect.stack()[0][3]

    brandsDict = OrderedDict(
        [('b_id', "INT"), ('brandname', "TEXT"), ('modelname', "TEXT"), ('version', "TEXT"), ('link', "TEXT")])
    linksDict = OrderedDict([('l_id', "INT"), ('b_id', "INT"), ('time', "TEXT"), ('link', "TEXT"), ('parsed', 'BOOL')])
    oldLinksDict = OrderedDict([('l_id', "INT"), ('b_id', "INT"), ('time', "TEXT"), ('link', "TEXT"), ('parsed', 'BOOL')])
    InvalidLinksDict = OrderedDict([('l_id', "INT"), ('time', "TEXT"), ('link', "TEXT"), ('parsed', 'BOOL')])
    carDataDict = OrderedDict([('b_id', "INT"), ('l_id', "INT"), ('year', "INT"), ('mileage', "INT"), ('power', "INT"),
                               ('capacity', "INT"), ('fuel', "TEXT"), ('color', "TEXT"), ('usedornew', "TEXT"),
                               ('doors', "TEXT"), ('gearbox', "TEXT"), ('price', "INT"), ('time', "TEXT")])
    CycleDict = OrderedDict([('start_brands', "TEXT"), ('start_links', "TEXT"), ('start_cars', "TEXT"),
                             ('end_time', "TEXT"), ('new_brands', "INT"), ('new_links', "INT"), ('new_cars', "INT")])

    db.createTable('cars_brand', brandsDict)
    db.createTable('links', linksDict)
    db.createTable('oldlinks', oldLinksDict)
    db.createTable('cars_car', carDataDict)
    db.createTable('invalidlinks', InvalidLinksDict)
    db.createTable('collectcycle', CycleDict)

def collect(nameOfDb, brandsLimit=2000, linksLimit=100000, carslimit=200000):
    methodName = inspect.stack()[0][3]

    moduleLogger.info('%s - Started: %s' % (methodName, datetime.datetime.now().strftime("%d-%m-%Y %H:%M")))

    while True:
        #start brands
        dbmsg = """ "%s",  """ % str(datetime.datetime.now())
        db = DataBase(nameOfDb)
        constructDBTables(db)

        beginBrands = time.time()
        currentDate = datetime.datetime.now()
        newBrands = ConstructBrandsTable(db, limit=brandsLimit)
        #newBrands = 0
        moduleLogger.info("%s - Brands done. %s. Number of new brands: %d. Done in %d seconds." % (methodName,
            datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), newBrands, time.time() - beginBrands))

        #start links
        dbmsg += """ "%s", """ % str(datetime.datetime.now())
        beginLinks = time.time()
        newLinks = constructLinkTable(db, limit=linksLimit)
        #newLinks = 0
        moduleLogger.info("%s - Links done.  %s. Number of new links:  %d. Done in %d seconds." % (methodName,
            datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), newLinks, time.time() - beginLinks))
        now = time.time()

        # start cars
        dbmsg += """ "%s", """ % str(datetime.datetime.now())

        beginCars = time.time()
        newCars = ConstructCarsTable(db, limit=carslimit)
        moduleLogger.info("%s - Cars done.   %s. Number of new cars:   %d. Done in %d seconds." % (methodName,
            datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), newCars, time.time() - beginCars))

        # end time
        dbmsg += """ "%s", """ % str(datetime.datetime.now())

        dbmsg += "%d, " % newBrands
        dbmsg += "%d, " % newLinks
        dbmsg += "%d " % newCars

        message = '\nStarted: %s\n' % currentDate.strftime("%d-%m-%Y %H:%M")
        message += "New Brands: %d\nNew Links:  %d\nNew Cars:   %d\n" % (newBrands, newLinks, newCars)
        message += "All done in %d seconds\n\n" % (time.time() - now)
        message += "End date: %s" % datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        moduleLogger.info("%s - %s" % (methodName, message))

        db.insertStringData("collectcycle", dbmsg)

        #clean old links from db
        db.clearParsedLinks()
        #transfer to azure

        del db

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='CarDataCollector')
    parser.add_argument('database_name', metavar='DATABASE_NAME', type=str, nargs=1,
                        help='Name of a database file. If such file name does not exists, it will be created.')

    parser.add_argument("--brands_limit", type=int, required=False, default=2000,
                        help='Maximum number of brands to be collected in one cycle.')
    parser.add_argument("--links_limit", type=int, required=False, default=100000,
                        help='Maximum number of links to be collected in one cycle.')
    parser.add_argument("--cars_limit", type=int, required=False, default=200000,
                        help='Maximum number of cars to be collected in one cycle.')

    args = parser.parse_args()

    collect(args.database_name[0], args.brands_limit, args.links_limit, args.cars_limit)

