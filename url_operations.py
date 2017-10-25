#-*- coding: utf-8 -*-
import re

import urllib
from bs4 import BeautifulSoup
import time
import unicodedata
from data_operations import DataCleaning
from logger import Logger
import inspect

moduleLogger = Logger.setLogger("urlops")


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def _openLinkAndReturnSoup(url):
    try:
        r = urllib.urlopen(url).read()
    except Exception:
        time.sleep(60)
        methodName = inspect.stack()[0][3]
        moduleLogger.info("%s - Problems with parsing %s, sleep 60 seconds. Exception: %s" % (methodName, url))
        return None

    return BeautifulSoup(r, "lxml")


class URLOperations(object):
    forbiddenLinks = [
                    'https://allegro.pl/',
                    'https://allegro.pl/praca',
                    'https://allegro.pl/mapa-strony',
                    'https://allegro.pl/',
                    'https://allegro.pl/strefaokazji',
                    'https://allegro.pl/strefamarek?ref=navbar',
                    'https://allegro.pl/artykuly?ref=navbar',
                    'https://allegro.pl/category_map.php',
                    'https://allegro.pl/logout.php',
                    'https://allegro.pl/strefamarek?ref=navbar',
                    'https://otomoto.pl',
                    "https://allegro.pl/sklep?ref=navbar",
                    "https://allegro.pl/myaccount",
                    "https://allegro.pl/logout.php?ref=navbar"
                     ]

    @staticmethod
    def getAllegroPrice(url):
        soup = _openLinkAndReturnSoup(url)

        try:
            price = int(float(soup.findAll("div", { "class" : "price" })[0]['data-price']))

            return price
        except:
            methodName = inspect.stack()[0][3]
            moduleLogger.error("%s - Problems getting price from url: %s." % (methodName, url))
            return 0

    @staticmethod
    def getOtomotoPrice(url):
        soup = _openLinkAndReturnSoup(url)

        try:
            price = int(soup.findAll("span", {"class":
                                                   "offer-price__number" })[0].text.split('  ')[0].replace(' ', ''))
            # possible place for a debug log line
            return price
        except:
            methodName = inspect.stack()[0][3]
            moduleLogger.error("%s - Problems getting price from url: %s." % (methodName, url))
            return 0

    @staticmethod
    def parseAllegroSite(url):
        methodName = inspect.stack()[0][3]
        keys = []
        vals = []

        soup = _openLinkAndReturnSoup(url)
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
                        keys.append(unicodedata.normalize('NFKD', cell.text.strip()).encode('ascii', 'ignore').lower())
                    else:
                        value = unicodedata.normalize('NFKD', cell.text.strip()).encode('ascii', 'ignore').lower()

                        if value.isdigit():
                            value = int(value)

                        vals.append(value)
        else:
            moduleLogger.debug("%s - Allegro type 2 site." % methodName)
            #type 2 allegro site
            lis = [li.findChildren('span') for li in soup.findChildren('li') if len(li.findChildren('span')) == 2]
            keys, vals = \
                [unicodedata.normalize('NFKD', span[0].text.strip()).encode('ascii','ignore').lower() for span in lis],\
                [unicodedata.normalize('NFKD', span[1].text.strip()).encode('ascii','ignore').lower() for span in lis]
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

        soup = _openLinkAndReturnSoup(url)
        try:
            tabele = soup.findChildren('ul')[6:10]
        except:
            moduleLogger.debug("%s - Unable to parse site: %s. "
                               "Just at the beginning there was no 'ul' tag in the url." % (methodName, url))
            return {}

        for tabela in tabele:
            for li in tabela.findChildren('li'):
                for small, span in zip(li.findChildren('small'), li.findChildren('span')):
                    keys.append(unicodedata.normalize('NFKD', small.text).encode('ascii','ignore').lower())

                    value = unicodedata.normalize('NFKD', span.text).encode('ascii','ignore').lower()

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

        soup = _openLinkAndReturnSoup(url)
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
                        d['rok produkcji'] = \
                            int(unicodedata.normalize
                                ('NFKD', li.findChildren('div')[0].text.strip()).encode('ascii','ignore').lower())
                    except:
                        moduleLogger.debug("%s - Problems parsing url %s. "
                                           "There is something wrong with year of production." % (methodName, url))
                        d['rok produkcji'] = 0

            elif 'przebieg' in span[0].text.lower():
                if li.findChildren('div')[0].text.strip() is not None:
                    try:
                        decVal = DataCleaning.stripDecimalValue(\
                            (unicodedata.normalize
                             ('NFKD', li.findChildren('div')[0].text.strip()).encode('ascii','ignore').lower()))
                        d['przebieg'] = int(decVal)
                    except:
                        moduleLogger.debug("%s - Problems parsing url %s. "
                                           "There is something wrong with mileage." % (methodName, url))
                        d['przebieg'] = 0

            elif 'rodzaj paliwa' in span[0].text.lower():
                if li.findChildren('div')[0].text.strip() is not None:
                    d['rodzaj paliwa'] = unicodedata.normalize(
                        'NFKD', li.findChildren('div')[0].text.strip()).encode('ascii','ignore').lower()

            elif 'kolor' in span[0].text.lower():
                if li.findChildren('div')[0].text.strip() is not None:
                    d['kolor'] = unicodedata.normalize(
                        'NFKD', li.findChildren('div')[0].text.strip()).encode('ascii','ignore').lower()

            elif 'liczba drzwi' in span[0].text.lower():
                if li.findChildren('div')[0].text.strip() is not None:
                    d['liczba drzwi'] = DataCleaning.stripDecimalValue(
                        unicodedata.normalize(
                            'NFKD', li.findChildren('div')[0].text.strip()).encode('ascii','ignore').lower())

            elif 'moc' in span[0].text.lower():
                if li.findChildren('div')[0].text.strip() is not None:
                    try:
                        decVal = DataCleaning.stripDecimalValue(\
                            (unicodedata.normalize(
                                'NFKD', li.findChildren('div')[0].text.strip()).encode('ascii','ignore').lower()))
                        d['moc'] = int(decVal)
                    except:
                        moduleLogger.debug(
                            "%s - Problems parsing url %s. There is something wrong with power." % (methodName, url))
                        d['moc'] = 0

            elif 'stan' in span[0].text.lower():
                if li.findChildren('div')[0].text.strip() is not None:
                    d['stan'] = unicodedata.normalize(
                        'NFKD', li.findChildren('div')[0].text.strip()).encode('ascii','ignore').lower()

            elif re.match("pojemno.. skokowa", span[0].text.lower()):
                if li.findChildren('div')[0].text.strip() is not None:
                    try:
                        decVal = DataCleaning.stripDecimalValue( \
                            (unicodedata.normalize(
                                'NFKD', li.findChildren('div')[0].text.strip()).encode('ascii', 'ignore').lower()))
                        d['pojemnosc skokowa'] = int(decVal)
                    except:
                        moduleLogger.debug(
                            "%s - Problems parsing url %s. There is something wrong with capacity." % (methodName, url))
                        d['pojemnosc skokowa'] = 0

            elif re.match("skrzynia bieg.w", span[0].text.lower()):
                if li.findChildren('div')[0].text.strip() is not None:
                    d['skrzynia biegow'] = unicodedata.normalize(
                        'NFKD', li.findChildren('div')[0].text.strip()).encode('ascii','ignore').lower()

        if d:
            price = URLOperations.getOtomotoPrice(url)
            d['cena'] = price

        return d


    @staticmethod
    def getAllBrands(topUrl):
        methodName = inspect.stack()[0][3]
        dictionary = {}

        soup = _openLinkAndReturnSoup(topUrl)

        if soup is None:
            return {}

        top = soup.find_all("section", { 'class' : 'category-tree__category-tree__3Mj66' })

        if len(top) == 1:
            liElements = top[0].findChildren("li")
            for li in liElements:
                if len(li.findChildren("span")) != 0 and len(li.findChildren('a')) != 0:
                    dictionary[li.findChildren("span")[0].text.strip()] = li.findChildren('a')[0]['href']
        else:
            moduleLogger.debug("%s - Problems getting brands. There is no top parameter - 'section' tag." % methodName)
            return {}

        if len(dictionary.values()) > 50 and topUrl != "https://allegro.pl/kategoria/samochody-osobowe-4029":
            return {}
        else:
            return dictionary

    @staticmethod
    def getLinksFromCategorySite(url):
        methodName = inspect.stack()[0][3]
        try:
            lastLinkSiteNumber = int(_openLinkAndReturnSoup(url).find_all("li", {"class" : "quantity"})[0].text)
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

    @staticmethod
    def getSubcategories(url):
        methodName = inspect.stack()[0][3]
        links = []
        soup = _openLinkAndReturnSoup(url)

        top = soup.find_all("li", { 'class' : 'sidebar-cat' })
        for t in top:
            if len(t.findChildren('a')) > 0:
                links.append('http://allegro.pl/' + t.findChildren('a')[0]['href'])

        moduleLogger.debug("%s - There are %d new subcategories in %s category site url." %
                           (methodName, len(links), url))
        return links
