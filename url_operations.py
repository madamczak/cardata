#-*- coding: utf-8 -*-

import urllib
from bs4 import BeautifulSoup
import time
import unicodedata


def is_ascii(s):
    return all(ord(c) < 128 for c in s)



class URLOperations(object):
    forbiddenLinks = [
                    'http://allegro.pl/',
                    'http://allegro.pl/category_map.php',
                    'http://allegro.pl/logout.php',
                    'http://allegro.pl/strefamarek?ref=navbar',
                    'http://otomoto.pl'
                     ]
    @staticmethod
    def parseAllegroSite(url):
        keys = []
        vals = []
        try:
            r = urllib.urlopen(url).read()
        except:
            time.sleep(60)
            print 'sleep 60'
            return {}

        soup = BeautifulSoup(r, "lxml")
        tables = soup.findChildren('table')
        for t in tables[2:]:
            rows = t.findChildren(['th', 'tr'])
            for row in rows:
                cells = row.findChildren('td')
                if len(cells) == 4 and '<' not in row.text and row.text.strip() != "":
                    #for cell in cells:
                    for cell in cells:
                        if ":" in cell.text:
                            keys.append(unicodedata.normalize('NFKD', cell.text.strip()).encode('ascii','ignore').lower())
                        else:
                            vals.append(unicodedata.normalize('NFKD', cell.text.strip()).encode('ascii','ignore').lower())
        return dict(zip(keys, vals))

    @staticmethod
    def parseAllegroSite2(url):
        d = {'stan:':'',
             'rok produkcji:':'',
             'przebieg [km]:':'',
             'pojemnosc silnika [cm3]:': '',
             'moc [KM]:': '',
             'rodzaj paliwa:':'',
             'liczba drzwi:':'',
             'skrzynia biegow:':'',
             'kolor:':''
             }

        try:
            r = urllib.urlopen(url).read()
        except:
            print 'sleep 60'
            time.sleep(60)
            return {}

        soup = BeautifulSoup(r, "lxml")
        lis = soup.findChildren('li')
        for li in lis:
            spans = li.findChildren('span')
            if len(spans) == 2:
                if is_ascii(spans[0].text):
                    if spans[0].text in d.keys():
                        if 'wany' in spans[1].text:
                            d['stan:'] = 'uzywany'
                        else:
                            d[spans[0].text] = spans[1].text
                else:
                    if 'pojemno' in spans[0].text:
                        d['pojemnosc silnika [cm3]:'] = spans[1].text
                    elif 'skrzynia bieg' in spans[0].text:
                        d['skrzynia biegow:'] = spans[1].text
        return d

    @staticmethod
    def parseOtoMotoSite(url):
        keys = []
        vals = []
        try:
            r = urllib.urlopen(url).read()
        except:
            print 'sleep 60'
            time.sleep(60)
            return {}
        soup = BeautifulSoup(r, "lxml")
        tabele = soup.findChildren('ul')[6:10]
        for tabela in tabele:
            for li in tabela.findChildren('li'):
                for small, span in zip(li.findChildren('small'), li.findChildren('span')):
                    keys.append(unicodedata.normalize('NFKD', small.text).encode('ascii','ignore').lower())
                    vals.append(unicodedata.normalize('NFKD', span.text).encode('ascii','ignore').lower())
        return dict(zip(keys, vals))


    @staticmethod
    def parseOtoMotoSite2(url):
        d = {}
        try:
            r = urllib.urlopen(url).read()
        except:
            print 'sleep 60'
            time.sleep(60)
            return {}
        soup = BeautifulSoup(r, "lxml")

        for li in soup.findChildren('li', {'class': 'offer-params__item'}):
            span = li.findChildren('span')
            if 'rok produkcji' in span[0].text.lower():
                if li.findChildren('div')[0].text.strip() is not None:
                    d['rok produkcji'] = unicodedata.normalize('NFKD', li.findChildren('div')[0].text.strip()).encode('ascii','ignore').lower()
            elif 'przebieg' in span[0].text.lower():
                if li.findChildren('div')[0].text.strip() is not None:
                    d['przebieg'] = unicodedata.normalize('NFKD', li.findChildren('div')[0].text.strip()).encode('ascii','ignore').lower()
            elif 'rodzaj paliwa' in span[0].text.lower():
                if li.findChildren('div')[0].text.strip() is not None:
                    d['rodzaj paliwa'] = unicodedata.normalize('NFKD', li.findChildren('div')[0].text.strip()).encode('ascii','ignore').lower()
            elif 'typ' in span[0].text.lower():
                if li.findChildren('div')[0].text.strip() is not None:
                    d['typ'] = unicodedata.normalize('NFKD', li.findChildren('div')[0].text.strip()).encode('ascii','ignore').lower()
            elif 'kolor' in span[0].text.lower():
                if li.findChildren('div')[0].text.strip() is not None:
                    d['kolor'] = unicodedata.normalize('NFKD', li.findChildren('div')[0].text.strip()).encode('ascii','ignore').lower()
        return d


    @staticmethod
    def getAllBrands(topUrl):
        dictionary = {}
        crawled = []
        toCrawl = []
        try:
            r = urllib.urlopen(topUrl).read()
        except:
            print 'sleep 60'
            time.sleep(60)
            return {}
        soup = BeautifulSoup(r, "lxml")

        top = soup.find_all("li", { 'class' : 'sidebar-cat' })
        for t in top:
            if len(t.findChildren('a')) > 0:
                dictionary[t.findChildren("span")[0].text.strip()] = 'http://allegro.pl/' + t.findChildren('a')[0]['href']
        return dictionary

    @staticmethod
    def getAllModels(urlDict):
        #urlDict from getAllBrands method

        pass

    @staticmethod
    def getLinksFromCategorySite(url):

        #last
        try:
            r = urllib.urlopen(url).read()
        except:
            print 'sleep 60'
            time.sleep(60)
            return{}

        soup = BeautifulSoup(r, "lxml")
        try:
            top = soup.find_all("ul", { 'class' : 'pagination top' })[0]
        except:
            return []
        last = int(top.findChildren("li")[2].findChildren('a')[0].text)

        links = []
        for i in range(1, last+1):
            if i > 1:
                address = url + "?p=" + str(i)
            else:
                address = url
            try:
                r = urllib.urlopen(address).read()
            except:
                continue

            soup = BeautifulSoup(r, "lxml")

            for link in soup.find_all('a', href=True):
                if ('http://allegro.pl/' in link['href']\
                    and '/' not in link['href'][19:] \
                    and link['href'] not in URLOperations.forbiddenLinks) \
                        or 'http://otomoto.pl' in link['href']:

                    if link['href'] not in links:
                        links.append(link['href'])
        return links

    @staticmethod
    def getSubcategories(url):
        links = []
        try:
            r = urllib.urlopen(url).read()
        except:
            print 'sleep 60'
            time.sleep(60)
            return{}
        soup = BeautifulSoup(r, "lxml")

        top = soup.find_all("li", { 'class' : 'sidebar-cat' })
        for t in top:
            if len(t.findChildren('a')) > 0:
                links.append('http://allegro.pl/' + t.findChildren('a')[0]['href'])
        return links

    @staticmethod
    def getAllLinksToCategories(baseUrl):
        subcategories = []
        brands = URLOperations.getSubcategories(baseUrl)
        for brand in brands:
            toAdd = URLOperations.getSubcategories(brand)
            for newLink in toAdd:
                if newLink not in subcategories:
                    subcategories.append(newLink)

        return subcategories

    @staticmethod
    def getAllAdvertismentLinks(listOfCategoriesLinks):
        adverisments = []
        for cat in listOfCategoriesLinks[:2]:
            toAdd = URLOperations.getLinksFromCategorySite(cat)
            for newLink in toAdd:
                if newLink not in adverisments:
                    adverisments.append(newLink)

        return adverisments

    @staticmethod
    def GetAllAdvertisments(listOfCategories):
        result = []
        for category in listOfCategories:
            if 'osobowe' not in category:
                ads = URLOperations.getLinksFromCategorySite(category)
                for ad in ads:
                    result.append(ad)
        return result


