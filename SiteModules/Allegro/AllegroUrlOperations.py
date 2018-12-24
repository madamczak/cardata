#-*- coding: utf-8 -*-
from OperationUtils.data_operations import DataCleaning
from OperationUtils.logger import Logger
import inspect
from SiteModules.common_url_operations import openLinkAndReturnSoup

moduleLogger = Logger.setLogger("Allegro URL Operations")


class AllegroURLOperations(object):
    @staticmethod
    def getAllegroPrice(soup):
        try:
            meta = soup.find_all("meta", {"itemprop" : "price"})
            if meta:
                price = int(float(DataCleaning.stripDecimalValue(meta[0]['content'])))
            else:
                price = int(float(DataCleaning.stripDecimalValue(soup.findAll("div", { "class" : "m-price" })[0]['data-price'])))
            return price
        except:
            return 0

    @staticmethod
    def findLocationInSoup(soupObject):
        try:
            for link in soupObject.find_all('a', href=True):
                if "#location" in link['href'] and "," in link.text:
                    return link.text
        except:
            return "unknown"

    @staticmethod
    def parseAllegroSite(url):
        soup = openLinkAndReturnSoup(url)
        if soup is None:
            return {}


        liElements = []
        for li in soup.findChildren('li'):
            if len(li.findChildren('div')) == 3:
                liElements.append(li.findChildren('div'))

        keys, vals = \
            [DataCleaning.normalize(span[1].text) for span in liElements],\
            [DataCleaning.normalize(span[2].text) for span in liElements]

        if keys and vals:
            keys.append('cena')#price
            keys.append('miejsce')#location
            try:
                vals.append(AllegroURLOperations.getAllegroPrice(soup))
                vals.append(AllegroURLOperations.findLocationInSoup(soup))
            except:
                vals.append(0)

        return dict(zip(keys, vals))

    @staticmethod
    def getAllBrands(topUrl):
        methodName = inspect.stack()[0][3]
        brandsDictionary = {}

        soup = openLinkAndReturnSoup(topUrl)
        if soup is None:
            return {}

        top = soup.find_all("section", { 'class' : '_53938a6' })

        if len(top) == 1:
            liElements = top[0].findChildren("li")
            for li in liElements:
                if len(li.findChildren("span")) != 0 and len(li.findChildren('a')) != 0:
                    key = li.findChildren("a")[0].text.strip()
                    val = "https://allegro.pl" + li.findChildren('a')[0]['href']
                    brandsDictionary[key] = val
        else:
            moduleLogger.debug("%s - Problems getting brands. There is no top parameter - 'section' tag." % methodName)
            return {}

        #TODO fix magic number 50
        if len(brandsDictionary.values()) > 50 and topUrl != "https://allegro.pl/kategoria/samochody-osobowe-4029":
            return {}
        else:
            return brandsDictionary

    @staticmethod
    def getLinksFromCategorySite(url, startTimeParameter="&startingTime=7"):
        methodName = inspect.stack()[0][3]
        try:
            lastLinkSiteNumber = int(openLinkAndReturnSoup(url).find_all("span", {"class" : "m-pagination__text"})[0].text)
        except:
            lastLinkSiteNumber = 1

        links = []
        for i in range(1, lastLinkSiteNumber + 1):
            if i > 1:
                address = url + "?p=" + str(i)
            else:
                address = url

            if startTimeParameter is not None:
                if "?" in address:
                    address += "&startingTime=7" #get links only from last 1 weeks for performance reasons
                else:
                    address += "?startingTime=7"

            soup = openLinkAndReturnSoup(address)

            if soup is None:
                return []

            allHrefs = soup.find_all('a', href=True)
            for link in allHrefs:
                if "https://allegro.pl/ogloszenie" in link['href'] and link['href'] not in links:
                    links.append(link['href'])

        moduleLogger.debug("%s - There are %d new links in %s category site url." % (methodName, len(links), url))
        return links
