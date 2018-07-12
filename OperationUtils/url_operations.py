#-*- coding: utf-8 -*-
import re
import requests
import urllib
from bs4 import BeautifulSoup
import time
from OperationUtils.data_operations import DataCleaning
from OperationUtils.logger import Logger
import inspect

moduleLogger = Logger.setLogger("urlops")


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def openLinkAndReturnSoup(url):
    start = time.time()
    moduleLogger.debug("Opening: %s" % url)
    try:
        agent = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
        page = requests.get(url, headers=agent)
    except:
        time.sleep(60)
        methodName = inspect.stack()[0][3]
        moduleLogger.info("%s - Problems with parsing %s, sleep 60 seconds." % (methodName, url))
        return None

    bsObject = BeautifulSoup(page.content, "lxml")

    moduleLogger.debug("Returning bs object from url: %s. It took %d seconds to parse it." % (url, time.time() - start))
    return bsObject


class URLOperations(object):
    #todo: remove this and change it to regex link checking
    forbiddenLinks = [
                    'https://allegro.pl/',
                    'https://allegro.pl/listing?string=',
                    'https://allegro.pl/newItem',
                    'https://allegro.pl/moje-konto',
                    'https://allegro.pl/dla-sprzedajacych',
                    'https://allegro.pl/artykuly',
                    'https://allegro.pl/pomoc',
                    'https://allegro.pl/praca',
                    'https://allegro.pl/mapa-strony',
                    'https://allegro.pl/',
                    'https://allegro.pl/strefamarek',
                    'https://allegro.pl/inspiracje',
                    'https://allegro.pl/strefaokazji',
                    'https://allegro.pl/strefamarek?ref=navbar',
                    'https://allegro.pl/artykuly?ref=navbar',
                    'https://allegro.pl/category_map.php',
                    'https://allegro.pl/logout.php',
                    'https://allegro.pl/strefamarek?ref=navbar',
                    'https://otomoto.pl',
                    "https://allegro.pl/sklep?ref=navbar",
                    "https://allegro.pl/myaccount",
                    "https://allegro.pl/logout.php?ref=navbar",
                    "https://allegro.pl/listing?string=Spod"
                     ]

    @staticmethod
    def getAllegroPrice(url):
        soup = openLinkAndReturnSoup(url)

        try:
            price = int(float(DataCleaning.stripDecimalValue(soup.findAll("div", { "class" : "m-price" })[0]['data-price'])))
            return price
        except:
            methodName = inspect.stack()[0][3]
            moduleLogger.error("%s - Problems getting price from url: %s." % (methodName, url))
            return 0

    @staticmethod
    def getOtomotoPrice(url):
        soup = openLinkAndReturnSoup(url)

        try:
            price = int(soup.findAll("span",
                                 {"class": "offer-price__number" })[0].text.split('  ')[0].replace(' ', ''))
            return price
        except:
            methodName = inspect.stack()[0][3]
            moduleLogger.error("%s - Problems getting price from url: %s." % (methodName, url))
            return 0

    @staticmethod
    #todo: test if a site has specific structure for that method
    def parseAllegroSite(url):
        methodName = inspect.stack()[0][3]
        keys = []
        vals = []

        soup = openLinkAndReturnSoup(url)
        try:
            tables = soup.findChildren('table')
        except:
            moduleLogger.error("%s - Unable to parse site: %s. "
                               "Just at the beginning there was no 'table' tag in the url." % (methodName, url))
            return {}

        if len(tables) != 0:
            moduleLogger.debug("%s - Allegro type 1 site." % methodName)
            #type 1 allegro site
            for t in tables[2:]:
                rows = [row for row in t.findChildren(['th', 'tr']) if '<' not in row.text and row.text.strip()]

                validCells = []
                for row in rows:
                    cells = row.findChildren('td')
                    validCells.extend([cell for cell in cells if len(cells) == 4])

                for cell in validCells:
                    if ":" in cell.text:
                        keys.append(DataCleaning.normalize(cell.text))
                    else:
                        value = DataCleaning.normalize(cell.text)

                        if value.isdigit():
                            value = int(value)

                        vals.append(value)
        else:
            moduleLogger.debug("%s - Allegro type 2 site." % methodName)
            #type 2 allegro site

            lis = []
            for li in soup.findChildren('li'):
                if len(li.findChildren('div')) == 3:
                    lis.append(li.findChildren('div'))
            #lis = [li.findChildren('div') for li in soup.findChildren('li')]# if len(li.findChildren('span')) == 2]

            keys, vals = \
                [DataCleaning.normalize(span[1].text) for span in lis],\
                [DataCleaning.normalize(span[2].text) for span in lis]
        if keys and vals:
            keys.append('cena')
            try:
                vals.append(URLOperations.getAllegroPrice(url))
            except:
                vals.append(0)

        toRet = dict(zip(keys, vals))

        if all([val == "0" or val == "" for val in toRet.values()]):
            moduleLogger.debug("%s - Something went wrong. Empty dictionary is returned. "
                               "Check out the link: %s." % (methodName, url))
            return {}
        else:
            return toRet

    @staticmethod
    def parseOtoMotoSite(url):
        methodName = inspect.stack()[0][3]
        keys = []
        vals = []

        soup = openLinkAndReturnSoup(url)
        try:
            tabele = soup.findChildren('ul')[6:10]
        except:
            moduleLogger.debug("%s - Unable to parse site: %s. "
                               "Just at the beginning there was no 'ul' tag in the url." % (methodName, url))
            return {}

        for tabela in tabele:
            for li in tabela.findChildren('li'):
                for small, span in zip(li.findChildren('small'), li.findChildren('span')):
                    keys.append(DataCleaning.normalize(small.text))

                    value = DataCleaning.normalize(span.text)

                    if value.isdigit():
                        value = int(value)

                    vals.append(value)

        if keys and vals:
            keys.append('cena')
            vals.append(URLOperations.getOtomotoPrice(url))

        toRet = dict(zip(keys, vals))
        if all([val == "0" or val == "" for val in toRet.values()]):
            moduleLogger.debug("%s - Unable to parse site: %s. "
                               "Just at the beginning there was no 'ul' tag in the url." % (methodName, url))
            return {}

        else:
            return toRet

    @staticmethod
    def parseOtoMotoSite2(url):
        #TODO: Refactor this.
        methodName = inspect.stack()[0][3]
        d = {}

        soup = openLinkAndReturnSoup(url)
        try:
            lis = soup.findChildren('li', {'class': 'offer-params__item'})
        except:
            moduleLogger.debug("%s - Unable to parse site: %s. "
                               "Just at the beginning there was no 'li' tags in the url." % (methodName, url))
            return d

        for li in lis:
            span = li.findChildren('span')
            if 'rok produkcji' in span[0].text.lower():
                if li.findChildren('div')[0].text.strip() is not None:

                    try:
                        d['rok produkcji'] = int(DataCleaning.normalize(li.findChildren('div')[0].text))
                    except:
                        moduleLogger.debug("%s - Problems parsing url %s. "
                                           "There is something wrong with year of production." % (methodName, url))
                        d['rok produkcji'] = 0

            elif 'przebieg' in span[0].text.lower():
                if li.findChildren('div')[0].text.strip() is not None:
                    try:
                        decVal = DataCleaning.stripDecimalValue(DataCleaning.normalize(li.findChildren('div')[0].text))
                        d['przebieg'] = int(decVal)
                    except:
                        moduleLogger.debug("%s - Problems parsing url %s. "
                                           "There is something wrong with mileage." % (methodName, url))
                        d['przebieg'] = 0

            elif 'rodzaj paliwa' in span[0].text.lower():
                if li.findChildren('div')[0].text.strip() is not None:
                    d['rodzaj paliwa'] = DataCleaning.normalize(li.findChildren('div')[0].text)

            elif 'kolor' in span[0].text.lower():
                if li.findChildren('div')[0].text.strip() is not None:
                    d['kolor'] = DataCleaning.normalize(li.findChildren('div')[0].text)

            elif 'liczba drzwi' in span[0].text.lower():
                if li.findChildren('div')[0].text.strip() is not None:
                    d['liczba drzwi'] = DataCleaning.normalize(li.findChildren('div')[0].text)

            elif 'moc' in span[0].text.lower():
                if li.findChildren('div')[0].text.strip() is not None:
                    try:
                        decVal = DataCleaning.stripDecimalValue(DataCleaning.normalize(li.findChildren('div')[0].text))
                        d['moc'] = int(decVal)
                    except:
                        moduleLogger.debug(
                            "%s - Problems parsing url %s. There is something wrong with power." % (methodName, url))
                        d['moc'] = 0

            elif 'stan' in span[0].text.lower():
                if li.findChildren('div')[0].text.strip() is not None:
                    d['stan'] = DataCleaning.normalize(li.findChildren('div')[0].text)

            elif re.match("pojemno.. skokowa", span[0].text.lower()):
                if li.findChildren('div')[0].text.strip() is not None:
                    try:
                        decVal = DataCleaning.stripDecimalValue(DataCleaning.normalize(li.findChildren('div')[0].text))
                        d['pojemnosc skokowa'] = int(decVal)
                    except:
                        moduleLogger.debug(
                            "%s - Problems parsing url %s. There is something wrong with capacity." % (methodName, url))
                        d['pojemnosc skokowa'] = 0

            elif re.match("skrzynia bieg.w", span[0].text.lower()):
                if li.findChildren('div')[0].text.strip() is not None:
                    d['skrzynia biegow'] = DataCleaning.normalize(li.findChildren('div')[0].text)

        if d:
            price = URLOperations.getOtomotoPrice(url)
            d['cena'] = price

        return d

    #TODO simple integration test
    @staticmethod
    def getAllBrands(topUrl):
        methodName = inspect.stack()[0][3]
        dictionary = {}

        soup = openLinkAndReturnSoup(topUrl)

        if soup is None:
            return {}

        top = soup.find_all("section", { 'class' : '_53938a6' })

        if len(top) == 1:
            liElements = top[0].findChildren("li")
            for li in liElements:
                if len(li.findChildren("span")) != 0 and len(li.findChildren('a')) != 0:
                    a = li.findChildren("a")[0].text
                    key = li.findChildren("a")[0].text.strip()
                    val = "https://allegro.pl" + li.findChildren('a')[0]['href']
                    dictionary[key] = val
        else:
            moduleLogger.debug("%s - Problems getting brands. There is no top parameter - 'section' tag." % methodName)
            return {}

        #TODO fix magic number 50
        if len(dictionary.values()) > 50 and topUrl != "https://allegro.pl/kategoria/samochody-osobowe-4029":
            return {}
        else:
            return dictionary

    @staticmethod
    def getLinksFromCategorySite(url, startTimeParameter="&startingTime=13"):
        methodName = inspect.stack()[0][3]
        try:
            lastLinkSiteNumber = int(openLinkAndReturnSoup(url).find_all("li", {"class" : "quantity"})[0].text)
            moduleLogger.debug("%s - There are currently %d categories in DB." % (methodName, lastLinkSiteNumber))
        except:
            lastLinkSiteNumber = 1
            moduleLogger.debug("%s - There are no categories in DB." % methodName)

        pattern = re.compile("(http|https)://(www.)?otomoto.pl")

        links = []
        for i in range(1, lastLinkSiteNumber + 1):
            if i > 1:
                address = url + "?p=" + str(i)
            else:
                address = url

            if startTimeParameter is not None:
                if "?" in address:
                    address += "&startingTime=13" #get links only from last 1 weeks for performance reasons
                else:
                    address += "?startingTime=13"

            try:
                r = urllib.urlopen(address).read()
            except:
                moduleLogger.error("%s - Unable to open %s. Skipping." % (methodName, address))
                continue

            soup = BeautifulSoup(r, "lxml")

            for link in soup.find_all('a', href=True):
                if (('https://allegro.pl/' in link['href'] or 'http://allegro.pl/' in link['href'])\
                    and '/' not in link['href'][19:] \
                    and link['href'].strip() not in URLOperations.forbiddenLinks
                    and "ref=navbar" not in link['href'].strip()) \
                        or pattern.match(link['href']):

                    if link['href'] not in links:
                        links.append(link['href'])
        moduleLogger.debug("%s - There are %d new links in %s category site url." % (methodName, len(links), url))
        return links
