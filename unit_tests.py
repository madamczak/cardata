# -*- coding: utf8 -*-

from OperationUtils.data_operations import DataCleaning
from OperationUtils.url_operations import _openLinkAndReturnSoup, URLOperations
import OperationUtils.url_operations
import unittest
from mock import patch
from bs4 import BeautifulSoup


emptySoup = BeautifulSoup("", "lxml")
allegroSoup = BeautifulSoup(open("UnitTests/allegroSiteBMW7.html").read(), "lxml")
otomotoSoup = BeautifulSoup(open("UnitTests/otomotoSiteType2BMW7.html").read(), "lxml")
rootCategorySoup = BeautifulSoup(open("UnitTests/rootCategorySite.html").read(), "lxml")
acuraCategorySoup = BeautifulSoup(open("UnitTests/acuraCategorySite.html").read(), "lxml")


class AllegroUrlParsing(unittest.TestCase):

    @patch('OperationUtils.url_operations._openLinkAndReturnSoup', return_value=allegroSoup)
    def test_can_parse_price(self, mockSoup):
        price = URLOperations.getAllegroPrice(None)
        self.assertEqual(303000, price)

    @patch('OperationUtils.url_operations._openLinkAndReturnSoup', return_value=emptySoup)
    def test_returns_0_on_invalid_soup(self, mockSoup):
        price = URLOperations.getAllegroPrice(None)
        self.assertEqual(0, price)

    @patch('OperationUtils.url_operations._openLinkAndReturnSoup', return_value=allegroSoup)
    def test_can_parse_site_properly(self, mockSoup):
        parsedDict = URLOperations.parseAllegroSite(None)
        self.assertNotEqual({}, parsedDict)
        self.assertEqual('2016', parsedDict.get("rok produkcji:"))
        self.assertEqual('23000', parsedDict.get('przebieg [km]:'))
        self.assertEqual('450', parsedDict.get('moc [km]:'))
        self.assertEqual('benzyna', parsedDict.get('rodzaj paliwa:'))
        self.assertEqual('4400', parsedDict.get('pojemnosc silnika [cm3]:'))
        self.assertEqual('biay', parsedDict.get('kolor:'))
        self.assertEqual('4/5', parsedDict.get('liczba drzwi:'))
        self.assertEqual('uzywany', parsedDict.get('stan:'))
        self.assertEqual('automatyczna dwusprzegowa (dct, dsg)', parsedDict.get('skrzynia biegow:'))

    @patch('OperationUtils.url_operations._openLinkAndReturnSoup', return_value=emptySoup)
    def test_returns_empty_dict_on_invalid_soup(self, mockSoup):
        parsedDict = URLOperations.parseAllegroSite(None)
        self.assertEqual({}, parsedDict)

class OtomotoUrlParsing(unittest.TestCase):

    @patch('OperationUtils.url_operations._openLinkAndReturnSoup', return_value=otomotoSoup)
    def test_can_parse_price(self, mockSoup):
        price = URLOperations.getOtomotoPrice(None)
        self.assertEqual(729000, price)

    @patch('OperationUtils.url_operations._openLinkAndReturnSoup', return_value=emptySoup)
    def test_returns_0_on_invalid_soup(self, mockSoup):
        price = URLOperations.getOtomotoPrice(None)
        self.assertEqual(0, price)

    @patch('OperationUtils.url_operations._openLinkAndReturnSoup', return_value=otomotoSoup)
    def test_can_parse_type_2_site_properly(self, mockSoup):
        parsedDict = URLOperations.parseOtoMotoSite2(None)
        self.assertNotEqual({}, parsedDict)
        self.assertEqual(2017, parsedDict.get("rok produkcji"))
        self.assertEqual(4186, parsedDict.get('przebieg'))
        self.assertEqual(609, parsedDict.get('moc'))
        self.assertEqual('benzyna', parsedDict.get('rodzaj paliwa'))
        self.assertEqual(6592, parsedDict.get('pojemnosc skokowa'))
        self.assertEqual('niebieski', parsedDict.get('kolor'))
        self.assertEqual('4', parsedDict.get('liczba drzwi'))
        self.assertEqual('automatyczna hydrauliczna (klasyczna)', parsedDict.get('skrzynia biegow'))

    @patch('OperationUtils.url_operations._openLinkAndReturnSoup', return_value=emptySoup)
    def test_returns_empty_dict_on_invalid_soup_from_type_2_site(self, mockSoup):
        parsedDict = URLOperations.parseOtoMotoSite2(None)
        self.assertEqual({}, parsedDict)

    #TODO: Catch type 1 site and test it
    # @patch('url_operations._openLinkAndReturnSoup', return_value=otomotoSoup)
    # def test_can_parse_type_2_site_properly(self):
    #
    #     parsedDict = URLOperations.parseOtoMotoSite("https://www.otomoto.pl/oferta/audi-a8-audi-a8-long-po-oplatach-w-pl-ID6zhvz9.html")
    #     self.assertNotEqual({}, parsedDict)
    #     self.assertEqual(2017, parsedDict.get("rok produkcji"))
    #     self.assertEqual(4186, parsedDict.get('przebieg'))
    #     self.assertEqual(609, parsedDict.get('moc'))
    #     self.assertEqual('benzyna', parsedDict.get('rodzaj paliwa'))
    #     self.assertEqual(6592, parsedDict.get('pojemnosc skokowa'))
    #     self.assertEqual('niebieski', parsedDict.get('kolor'))
    #     self.assertEqual('4', parsedDict.get('liczba drzwi'))
    #     self.assertEqual('automatyczna hydrauliczna (klasyczna)', parsedDict.get('skrzynia biegow'))

    # @patch('url_operations._openLinkAndReturnSoup', return_value=emptySoup)
    # def test_returns_empty_dict_on_invalid_soup_from_type_2_site(self, mockSoup):
    #     parsedDict = URLOperations.parseAllegroSite(None)
    #     self.assertEqual({}, parsedDict)

class CategoriesUrlParsing(unittest.TestCase):
    @patch('OperationUtils.url_operations._openLinkAndReturnSoup', return_value=rootCategorySoup)
    def test_returns_categories(self, mockSoup):
        parsedDict = URLOperations.getAllBrands("https://allegro.pl/kategoria/samochody-osobowe-4029")
        self.assertNotEqual({}, parsedDict)
        self.assertTrue("Volkswagen" in parsedDict.keys())
        self.assertTrue("Opel" in parsedDict.keys())
        self.assertTrue("Renault" in parsedDict.keys())
        self.assertTrue("Alfa Romeo" in parsedDict.keys())

    @patch('OperationUtils.url_operations._openLinkAndReturnSoup', return_value=rootCategorySoup)
    def test_does_not_return_categories_with_invalid_url(self, mockSoup):
        parsedDict = URLOperations.getAllBrands("INVALID URL")
        self.assertEqual({}, parsedDict)

    @patch('OperationUtils.url_operations._openLinkAndReturnSoup', return_value=emptySoup)
    def test_returns_empty_dict_on_invalid_category_url(self, mockSoup):
        parsedDict = URLOperations.getAllBrands(None)
        self.assertEqual({}, parsedDict)

    @patch('OperationUtils.url_operations._openLinkAndReturnSoup', return_value=None)
    def test_returns_empty_dict_on_None_soup(self, mockSoup):
        parsedDict = URLOperations.getAllBrands(None)
        self.assertEqual({}, parsedDict)

class DataCleaningStripDecimalValue(unittest.TestCase):
    def test_strips_power(self):
        toStrip = "1 598 cm3"
        self.assertEqual(DataCleaning.stripDecimalValue(toStrip), '1598')

    def test_strips_price(self):
        toStrip = "39 600,00 zl"
        self.assertEqual(float(DataCleaning.stripDecimalValue(toStrip)), 39600.0)

    def test_strips_mileage(self):
        toStrip = "48 000 km"
        self.assertEqual(DataCleaning.stripDecimalValue(toStrip), "48000")

    def test_strips_number_of_doors(self):
        toStrip = "2/3"
        self.assertEqual(DataCleaning.stripDecimalValue(toStrip), "2/3")

    def test_strips_number_of_doors(self):
        toStrip = "4/5"
        self.assertEqual(DataCleaning.stripDecimalValue(toStrip), "4/5")

    def test_strips_simple_integer(self):
        toStrip = "123"
        self.assertEqual(DataCleaning.stripDecimalValue(toStrip), "123")

    def test_strips_simple_float(self):
        toStrip = "21.1"
        self.assertEqual(DataCleaning.stripDecimalValue(toStrip), "21.1")

    def test_strips_simple_literal(self):
        toStrip = "AAAaaa"
        self.assertEqual(DataCleaning.stripDecimalValue(toStrip), "")

class DataCleaningNormalize(unittest.TestCase):
    def test_normalizes_year(self):
        toNormalize = u"\n    2016         \n"
        self.assertEqual(DataCleaning.normalize(toNormalize), "2016")

    def test_normalizes_color(self):
        toNormalize = u"\n    Biały        \n"
        self.assertEqual(DataCleaning.normalize(toNormalize), "biay")


    def test_normalizes_color2(self):
        toNormalize = u"\n    Złoty        \n"
        self.assertEqual(DataCleaning.normalize(toNormalize), "zloty")

    def test_normalizes_color3(self):
        toNormalize = u"\n    Żółty        \n"
        self.assertEqual(DataCleaning.normalize(toNormalize), "zolty")


    def test_normalizes_state(self):
        toNormalize = u"\n    Używany        \n"
        self.assertEqual(DataCleaning.normalize(toNormalize), "uzywany")

    def test_normalizes_power(self):
        toNormalize = u"200KM"
        self.assertEqual(DataCleaning.normalize(toNormalize), "200km")

    def test_normalizes_capacity(self):
        toNormalize = u"1400cm3"
        self.assertEqual(DataCleaning.normalize(toNormalize), "1400cm3")


if __name__ == "__main__":
    unittest.main()