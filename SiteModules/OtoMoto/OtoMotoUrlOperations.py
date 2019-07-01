from OperationUtils.data_operations import DataCleaning
from OperationUtils.db_operations import DataBase
from SiteModules.common_url_operations import openLinkAndReturnSoup
from OperationUtils.logger import Logger
import inspect


TOPLINK = "https://www.otomoto.pl/osobowe/"
moduleLogger = Logger.setLogger("OtoMoto URL Operations")
database = DataBase('..\..\crontest3 - Kopia.db')





class OtoMotoURLOperations(object):
    @staticmethod
    def getAllBrandsMatch(databaseObject):
        brandLinks = {} #b_id: link_otomoto
        try:
            brandTuples = [brand for brand in databaseObject.readAllBrands()]
        except Exception as e:
            moduleLogger.error("No database to match brands for OtoMoto website: %s" % e.message)
            return {}

        for brandTuple in brandTuples:
            brandName, model, version = brandTuple[1].replace(" ", "-"), brandTuple[2], brandTuple[3]
            brandLink = TOPLINK + brandName + "/"

            if model is None:
                brandLinks[brandTuple[0]] = brandLink.lower()
            else:
                #model is present
                model = model.replace(" ", "-")
                if brandName == "Mercedes-Benz" and "Klasa" in model:
                    modelLink = brandLink + model[-1].lower() + "-klasa" + "/"
                elif brandName == "Mercedes-Benz" and (
                        model in ["SL", "CLK", "SLK", "CLA", "CLS", "GL", "GLA", "GLC", "GLE", "GLK", "GLS"]):
                    modelLink = brandLink + model.lower() + "-klasa" + "/"
                elif brandName == "Mercedes-Benz" and model == "ML":
                    modelLink = brandLink + "m-klasa" + "/"
                elif brandName == 'Mercedes-Benz' and "W201" in model:
                    modelLink = brandLink + "w201-190/"
                elif brandName == 'Mercedes-Benz' and "W124" in model:
                    modelLink = brandLink + "W124-1984-1993/"

                elif brandName == "Kia" and "'" in model:
                    if "pro" in model.lower():
                        modelLink = brandLink + model.replace("'", "").replace("_", "-") + "/"
                    else:
                        modelLink = brandLink + model.replace("'", "") + "/"
                elif brandName == "Toyota" and model == "Corolla":
                    modelLink = brandLink + model.replace("'", "") + "/"
                elif brandName == "Toyota" and model == "FJ-Cruiser":
                    modelLink = brandLink + "fj/"

                elif brandName == "Mitsubishi" and model == "Lancer-Evolution":
                    modelLink = brandLink + model + "-x" + "/"
                elif brandName == "Mitsubishi" and model == "3000GT":
                    modelLink = brandLink + "3000-gt/"
                elif (brandName == "Suzuki" and "wagon" in model.lower()) or (
                        brandName == "Nissan" and model.lower() == "qashqai+2"):
                    modelLink = brandLink + model.replace("+", "-") + "/"
                elif brandName == "Honda" and model == "S2000":
                    modelLink = brandLink + "S-2000" + "/"
                elif brandName == 'Volkswagen' and model == "up!":
                    modelLink = brandLink + "up/"
                elif brandName == "Ferrari" and model == "488":
                    modelLink = brandLink + model + "-gtb" + "/"
                elif brandName == "Polonez" and "." in model:
                    modelLink = brandLink + model.replace(".", "")
                elif brandName == "Chrysler" and "country" in model.lower():
                    modelLink = brandLink + model.replace("-&-", "-") + "/"
                    model = model.replace("-&-", " & ")
                elif "pozosta" in model.lower():
                    modelLink = brandLink + "inny" + "/"
                else:
                    modelLink = brandLink + model + "/"

                if version is None:
                    brandLinks[brandTuple[0]] = modelLink.lower()
                else:
                    #version is present

                    if (brandName == 'Toyota' and model == "Corolla" and "E15" in version) or \
                            (brandName == 'Volvo' and model == "S40" and "ii" in version.lower()) or \
                            (brandName == 'Citroen' and model == "C3" and "2008" in version.lower()) or \
                            (brandName == 'Seat' and model == "Ibiza" and "iv" in version.lower()) or \
                            (brandName == 'Hyundai' and model == "i30" and "ii (2012-2016)" in version.lower()) or \
                            (brandName == 'Saab' and model == "9-3" and "ii" in version.lower()) or \
                            (brandName == 'Opel' and model == "Agila" and "b" in version.lower()) or \
                            (brandName == 'Nissan' and model == "Micra" and "k13" in version.lower()) or \
                            (brandName == 'Nissan' and model == "Primera" and "p12" in version.lower()) or \
                            (brandName == 'Volkswagen' and model == "Touareg" and "ii (" in version.lower()) or \
                            (brandName == 'Suzuki' and model == "Swift" and "v (2010" in version.lower()) or \
                            (brandName == 'Volkswagen' and model == "Polo" and "v (2009" in version.lower()) or \
                            (brandName == 'Mercedes-Benz' and model == "Vito" and "w639" in version.lower()) or \
                            (brandName == 'Skoda' and model == "Superb" and "ii (" in version.lower()):

                        versionLink = modelLink + version[:version.rfind("-")].replace(" (", "-").replace("-)",
                                                                                                          "").replace(
                            ")", "").replace(
                            " ", '-')
                    elif brandName == 'Citroen' and model == "Berlingo" and "ii" in version.lower():
                        versionLink = modelLink + version.replace(" (", "-").replace("-)", "").replace(")", "").replace(
                            " ", '-')[:-2]
                    elif brandName == 'Opel' and model == "Astra" and "j" in version.lower():
                        versionLink = modelLink + "j-2009-2015/"

                    elif brandName == 'Opel' and model == "Astra" and "h" in version.lower():
                        versionLink = modelLink + "h-2004-2013/"

                    elif brandName == 'Audi' and model == "A7" and "c7" in version.lower():
                        versionLink = modelLink + "c7-2011-2018/"

                    elif brandName == 'Renault' and model == "Scenic" and "iii" in version.lower():
                        versionLink = modelLink + "iii-2009-2013/"

                    elif brandName == 'Mercedes-Benz' and model == "SL" and "r230" in version.lower():
                        versionLink = modelLink + "r230-2001-2013/"

                    elif (brandName == 'Nissan' and model == "Primera" and "p10" in version.lower()) or (
                            brandName == 'Nissan' and model == "Sunny" and "b13" in version.lower()):
                        versionLink = modelLink + version.replace(" (", "-").replace("-)", "").replace(")", "").replace(
                            " ", '-').replace("/", "-")

                    elif brandName == 'Subaru' and model == "Impreza":
                        if "GD" in version:
                            versionLink = modelLink + "gd-2001-2007/"
                        elif "GC" in version:
                            versionLink = modelLink + "gc-1992-2001/"
                        else:
                            versionLink = modelLink + "gh-2007/"
                    else:
                        versionLink = modelLink + version.replace(" (", "-").replace("-)", "").replace(")", "").replace(
                            " ", '-')

                    brandLinks[brandTuple[0]] = versionLink.lower() + "/"
        return brandLinks

    @staticmethod
    def getLinksFromCategorySite(categoryLink):
        categoryLinks = []
        for pageNumber in range(1, OtoMotoURLOperations.getNumberOfPagesInBrandCategory(categoryLink) + 1):

            if pageNumber != 1:
                categoryLinkWithPage = categoryLink + "?page=%d" % pageNumber
            else:
                categoryLinkWithPage = categoryLink

            soup = openLinkAndReturnSoup(categoryLinkWithPage)
            if soup is not None:
                links = [href["data-href"] for href in soup.find_all("article", {'role': 'link'})]
                categoryLinks.extend(links)
            else:
                continue

        return categoryLinks

    @staticmethod
    def getOtoMotoLocation(soup):
        location = soup.find("span", {"class": "seller-box__seller-address__label"}).text.strip()
        return location

    @staticmethod
    def getOtoMotoPrice(soup):
        priceAndCurrency = soup.find("span", {"class": "offer-price__number"}).text.strip()
        currency = priceAndCurrency[-3:]
        price = DataCleaning.stripDecimalValue(priceAndCurrency)
        return price, currency


    @staticmethod
    def getOtoMotoDateAdded(soup):
        dateAdded = soup.find("span", {"class": "offer-meta__value"}).text.strip()
        # convert to datetime string
        return dateAdded

    #todo: test this properly for errors, probably should be private
    @staticmethod
    def getNumberOfPagesInBrandCategory(categoryLink):
        soup = openLinkAndReturnSoup(categoryLink)
        pages = soup.find_all("span", {'class': 'page'})
        if pages:
            return int(pages[-1].text)
        return 0

    @staticmethod
    #todo: tests, normalize values, internationalize values
    def parseOtomotoSite(url):
        dataDictionary = {}
        soup = openLinkAndReturnSoup(url)
        elements = soup.find_all("li", {'class': 'offer-params__item'})
        for element in elements:
            dataDictionary[DataCleaning.normalize(element.span.text.strip().lower())] = element.div.text.strip().lower()

        location = OtoMotoURLOperations.getOtoMotoLocation(soup)
        price, currency = OtoMotoURLOperations.getOtoMotoPrice(soup)
        timeAdded = OtoMotoURLOperations.getOtoMotoDateAdded(soup)
        dataDictionary["price"] = price
        dataDictionary["currency"] = currency
        dataDictionary["location"] = location
        dataDictionary["time"] = timeAdded

        return dataDictionary

    @staticmethod
    def insertOtomotoBrands():
        for brand_id, link in OtoMotoURLOperations.getAllBrandsMatch(database).items():
            print(brand_id, link)
            database.insertOtoMotoBrandLink(DataCleaning.normalize(link), brand_id)




