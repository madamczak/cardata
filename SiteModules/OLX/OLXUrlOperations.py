import datetime

from OperationUtils.data_operations import DataCleaning
from OperationUtils.db_operations import DataBase
from SiteModules.common_url_operations import openLinkAndReturnSoup
from OperationUtils.logger import Logger
import inspect

TOPLINK = "https://www.olx.pl/motoryzacja/samochody/"
moduleLogger = Logger.setLogger("OLX URL Operations")


class OLXCategoryFinder(object):
    def __init__(self, database_object):
        self.database = database_object

    #todo this should be unit tested as hell
    def categorizeOLXCar(self, modelName, yearOfProduction):
        #model
        if len(self.database.getAllBrandIdsOfModel(modelName)) <= 1:
            return self.database.getAllBrandIdsOfModel(modelName)[0]

        #version
        #todo is this really should be sorted? Newest first
        versions = sorted(self.database.getAllVersionNamesOfModel(modelName), key=lambda x: x[:4])

        for version in versions:
            productionBegin = DataCleaning.getVersionProductionBeginYear(version)
            productionEnd = DataCleaning.getVersionProductionEndYear(version)

            if productionBegin < yearOfProduction <= productionEnd or \
                    (productionEnd is None and productionBegin <= yearOfProduction):
                return self.database.getVersionID(modelName, version)

        return 0


class OLXURLOperations(object):
    # todo: tests, normalize values, internationalize values
    @staticmethod
    def parseOLXSite(url):
        dataDictionary = {}

        soup = openLinkAndReturnSoup(url)
        if soup is None:
            return {}

        tableItems = soup.find_all("table", {'class': 'item'})
        for item in tableItems:
            tableRow = item.find("tr")
            dataDictionary[tableRow.th.text.strip()] = tableRow.td.text.strip()

        price, currency = OLXURLOperations.getOLXPriceAndCurrency(soup)
        location = OLXURLOperations.getOLXLocation(soup)
        timeAdded = OLXURLOperations.getOLXTimeAdded(soup)
        dataDictionary["price"] = DataCleaning.stripDecimalValue(price)
        dataDictionary["currency"] = DataCleaning.normalize(currency)
        dataDictionary["location"] = location
        dataDictionary["time"] = timeAdded.strftime("%Y-%m-%d")

        return dataDictionary

    @staticmethod
    def categorizeOLXCar(brandName, modelName, year):
        finder = OLXCategoryFinder(None)
        b_id = 0

        return b_id

    @staticmethod
    def getOLXPriceAndCurrency(soup):
        priceAndCurrency = soup.find("div", {"class": "price-label"})
        if priceAndCurrency is not None:
            priceAndCurrency = priceAndCurrency.text.strip()
            currency = priceAndCurrency[-2:]
            price = DataCleaning.stripDecimalValue(priceAndCurrency)
            return price, currency
        else:
            return 0, "unknown"

    @staticmethod
    def getOLXLocation(soup):
        adDetails = soup.find("div", {"class": "offer-titlebox__details"})
        if adDetails is not None:
            location = adDetails.find("a")
            if location is not None:
                return location.text
        return "unknown"

    @staticmethod
    def getOLXTimeAdded(soup):
        adDetails = soup.find("div", {"class": "offer-titlebox__details"})
        if adDetails is not None:
            timeAdded = adDetails.find("em")
            if timeAdded is not None:
                return DataCleaning.convertOLXDate(timeAdded.text.split(",")[1].strip())
        return datetime.date.today()


    @staticmethod
    #todo: this is the same as for OtoMoto
    def getNumberOfPagesInBrandCategory(categoryLink):
        soup = openLinkAndReturnSoup(categoryLink)
        if soup:
            pages = soup.find_all("span", {'class': 'item fleft'})
            if pages:
                return int(pages[-1].text)
        return 0

    @staticmethod
    def getLinksFromCategorySite(categoryLink, oneDayOldOnly=True):
        categoryLinks = []

        for pageNumber in range(1, OLXURLOperations.getNumberOfPagesInBrandCategory(categoryLink) + 1):
            if pageNumber != 1:
                categoryLinkWithPage = categoryLink + "?page=%d" % pageNumber
            else:
                categoryLinkWithPage = categoryLink

            soup = openLinkAndReturnSoup(categoryLinkWithPage)
            if soup is not None:
                links = [href["href"] for href in soup.find_all("a", {'data-cy': 'listing-ad-title'})
                         if "olx." in href["href"]]
                categoryLinks.extend(links)

                lastLinksSoup = openLinkAndReturnSoup(links[-1])
                timeAdded = OLXURLOperations.getOLXTimeAdded(lastLinksSoup)
                timeDifference = (datetime.date.today() - timeAdded).days
                if oneDayOldOnly and timeDifference > 2:
                    moduleLogger.info("Links from category %s link are older than 2 days. "
                                      "No reason to check them. Skipping at page no: %d" % (categoryLink, pageNumber))
                    break

            else:
                continue

        return categoryLinks

    @staticmethod
    def getAllOLXBrands():
        brandLinks = []
        brandsList = ["aixam", "alfa-romeo", "audi", "bmw", "chevrolet", "cadillac", "chrysler", "citroen", 'dacia',
                      "daewoo", "daihatsu", "dodge", "fiat", "ford", "honda", "hyundai", "infinity", "jaguar", "jeep",
                      "kia", "lancia", "landrover", "lexus", "mazda", "mercedes-benz", "mini", "mitsubishi", "nissan",
                      "renault", "opel", "peugeot", "polonez", "porsche", "rover", "saab", "seat", "skoda", "smart",
                      "ssangyong", "subaru", "suzuki", "toyota", "volkswagen", "volvo"]

        for brand in brandsList:
            brandLinks.append("https://www.olx.pl/motoryzacja/samochody/" + brand + "/")

        return brandLinks

    @staticmethod
    def countLinks():
        count = 0

        for link in OLXURLOperations.getAllOLXBrands():
            amount = len(OLXURLOperations.getLinksFromCategorySite(link))
            count += amount
            print link, amount, "Total:", count


        return count

finder = OLXCategoryFinder(DataBase("../../crontest3TBT.db"))

carDict2 = OLXURLOperations.parseOLXSite("https://www.olx.pl/oferta/audi-a4-b8-s-line-ledy-CID5-IDzOYBb.html")
carDict3 = OLXURLOperations.parseOLXSite("https://www.olx.pl/oferta/audi-a4-2-0-avant-3x-s-line-quattro-190-km-2015-CID5-IDB3GDX.html")
carDict4 = OLXURLOperations.parseOLXSite("https://www.olx.pl/oferta/audi-a4-b9-prywatne-model-2017-2x-sline-CID5-IDB6yTA.html")
carDict = OLXURLOperations.parseOLXSite("https://www.olx.pl/oferta/audi-a2-2001r-154000km-klimatyzacja-CID5-IDBp0KY.html")
model = carDict4.get(u'Model')
rokprod = int(DataCleaning.normalize(carDict4.get(u'Rok produkcji')))
print finder.categorizeOLXCar(model, rokprod)
