from url_operations import _openLinkAndReturnSoup, URLOperations
import unittest
from mock import patch
from bs4 import BeautifulSoup


emptySoup = BeautifulSoup("", "lxml")
allegroSoup = BeautifulSoup(open("allegroSiteBMW7.html").read(), "lxml")
otomotoSoup = BeautifulSoup(open("otomotoSiteType2BMW7.html").read(), "lxml")


class AllegroUrlParsing(unittest.TestCase):

    @patch('url_operations._openLinkAndReturnSoup', return_value=allegroSoup)
    def test_can_parse_price(self, mockSoup):
        price = URLOperations.getAllegroPrice(None)
        self.assertEqual(303000, price)

    @patch('url_operations._openLinkAndReturnSoup', return_value=emptySoup)
    def test_returns_0_on_invalid_soup(self, mockSoup):
        price = URLOperations.getAllegroPrice(None)
        self.assertEqual(0, price)

    @patch('url_operations._openLinkAndReturnSoup', return_value=allegroSoup)
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

    @patch('url_operations._openLinkAndReturnSoup', return_value=emptySoup)
    def test_returns_empty_dict_on_invalid_soup(self, mockSoup):
        parsedDict = URLOperations.parseAllegroSite(None)
        self.assertEqual({}, parsedDict)

class OtomotoUrlParsing(unittest.TestCase):

    @patch('url_operations._openLinkAndReturnSoup', return_value=otomotoSoup)
    def test_can_parse_price(self, mockSoup):
        price = URLOperations.getOtomotoPrice(None)
        self.assertEqual(729000, price)

    @patch('url_operations._openLinkAndReturnSoup', return_value=emptySoup)
    def test_returns_0_on_invalid_soup(self, mockSoup):
        price = URLOperations.getOtomotoPrice(None)
        self.assertEqual(0, price)

    @patch('url_operations._openLinkAndReturnSoup', return_value=otomotoSoup)
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

    @patch('url_operations._openLinkAndReturnSoup', return_value=emptySoup)
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



if __name__ == "__main__":
    unittest.main()