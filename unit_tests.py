# -*- coding: utf8 -*-
from collections import OrderedDict

from OperationUtils.data_operations import DataCleaning
from OperationUtils.db_operations import DataBase
from OperationUtils.url_operations import openLinkAndReturnSoup, URLOperations
import OperationUtils.url_operations
import unittest
from mock import patch
from bs4 import BeautifulSoup
import os


emptySoup = BeautifulSoup("", "lxml")
allegroSoup = BeautifulSoup(open("UnitTests/allegroSiteBMW7.html").read(), "lxml")
otomotoSoup = BeautifulSoup(open("UnitTests/otomotoSiteType2BMW7.html").read(), "lxml")
rootCategorySoup = BeautifulSoup(open("UnitTests/rootCategorySite.html").read(), "lxml")
acuraCategorySoup = BeautifulSoup(open("UnitTests/acuraCategorySite.html").read(), "lxml")
testDB = DataBase("UnitTests/test.db")


class AllegroUrlParsing(unittest.TestCase):

    @patch('OperationUtils.url_operations.openLinkAndReturnSoup', return_value=allegroSoup)
    def test_can_parse_price(self, mockSoup):
        price = URLOperations.getAllegroPrice(None)
        self.assertEqual(303000, price)

    @patch('OperationUtils.url_operations.openLinkAndReturnSoup', return_value=emptySoup)
    def test_returns_0_on_invalid_soup(self, mockSoup):
        price = URLOperations.getAllegroPrice(None)
        self.assertEqual(0, price)

    @patch('OperationUtils.url_operations.openLinkAndReturnSoup', return_value=allegroSoup)
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

    @patch('OperationUtils.url_operations.openLinkAndReturnSoup', return_value=emptySoup)
    def test_returns_empty_dict_on_invalid_soup(self, mockSoup):
        parsedDict = URLOperations.parseAllegroSite(None)
        self.assertEqual({}, parsedDict)

class OtomotoUrlParsing(unittest.TestCase):

    @patch('OperationUtils.url_operations.openLinkAndReturnSoup', return_value=otomotoSoup)
    def test_can_parse_price(self, mockSoup):
        price = URLOperations.getOtomotoPrice(None)
        self.assertEqual(729000, price)

    @patch('OperationUtils.url_operations.openLinkAndReturnSoup', return_value=emptySoup)
    def test_returns_0_on_invalid_soup(self, mockSoup):
        price = URLOperations.getOtomotoPrice(None)
        self.assertEqual(0, price)

    @patch('OperationUtils.url_operations.openLinkAndReturnSoup', return_value=otomotoSoup)
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

    @patch('OperationUtils.url_operations.openLinkAndReturnSoup', return_value=emptySoup)
    def test_returns_empty_dict_on_invalid_soup_from_type_2_site(self, mockSoup):
        parsedDict = URLOperations.parseOtoMotoSite2(None)
        self.assertEqual({}, parsedDict)

    #TODO: Catch type 1 site and test it
    # @patch('url_operations.openLinkAndReturnSoup', return_value=otomotoSoup)
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

    # @patch('url_operations.openLinkAndReturnSoup', return_value=emptySoup)
    # def test_returns_empty_dict_on_invalid_soup_from_type_2_site(self, mockSoup):
    #     parsedDict = URLOperations.parseAllegroSite(None)
    #     self.assertEqual({}, parsedDict)

class CategoriesUrlParsing(unittest.TestCase):
    @patch('OperationUtils.url_operations.openLinkAndReturnSoup', return_value=rootCategorySoup)
    def test_returns_categories(self, mockSoup):
        parsedDict = URLOperations.getAllBrands("https://allegro.pl/kategoria/samochody-osobowe-4029")
        self.assertNotEqual({}, parsedDict)
        self.assertTrue("Volkswagen" in parsedDict.keys())
        self.assertTrue("Opel" in parsedDict.keys())
        self.assertTrue("Renault" in parsedDict.keys())
        self.assertTrue("Alfa Romeo" in parsedDict.keys())

    @patch('OperationUtils.url_operations.openLinkAndReturnSoup', return_value=rootCategorySoup)
    def test_does_not_return_categories_with_invalid_url(self, mockSoup):
        parsedDict = URLOperations.getAllBrands("INVALID URL")
        self.assertEqual({}, parsedDict)

    @patch('OperationUtils.url_operations.openLinkAndReturnSoup', return_value=emptySoup)
    def test_returns_empty_dict_on_invalid_category_url(self, mockSoup):
        parsedDict = URLOperations.getAllBrands(None)
        self.assertEqual({}, parsedDict)

    @patch('OperationUtils.url_operations.openLinkAndReturnSoup', return_value=None)
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

    def test_normalize_number_of_doors(self):
        self.assertEqual(DataCleaning.normalizeNumberOfDoors("2"), "2/3")
        self.assertEqual(DataCleaning.normalizeNumberOfDoors("3"), "2/3")
        self.assertEqual(DataCleaning.normalizeNumberOfDoors("2/3"), "2/3")

        self.assertEqual(DataCleaning.normalizeNumberOfDoors("4"), "4/5")
        self.assertEqual(DataCleaning.normalizeNumberOfDoors("5"), "4/5")
        self.assertEqual(DataCleaning.normalizeNumberOfDoors("4/5"), "4/5")

        self.assertEqual(DataCleaning.normalizeNumberOfDoors("30"), "unknown")


class DataCleaningInternationalize(unittest.TestCase):
#FUEL
    def test_internationalizes_fuel_petrol(self):
        toInternationalize = "benzyna"
        self.assertEqual(DataCleaning.internationalizeFuel(toInternationalize), "petrol")

    def test_internationalizes_fuel_petrol_lpg(self):
        toInternationalize = "benzyna + lpg"
        self.assertEqual(DataCleaning.internationalizeFuel(toInternationalize), "petrol + lpg")

    def test_internationalizes_fuel_petrol_lpg2(self):
        toInternationalize = "benzyna+lpg"
        self.assertEqual(DataCleaning.internationalizeFuel(toInternationalize), "petrol + lpg")

    def test_internationalizes_fuel_petrol_cng(self):
        toInternationalize = "benzyna + cng"
        self.assertEqual(DataCleaning.internationalizeFuel(toInternationalize), "petrol + cng")

    def test_internationalizes_fuel_petrol_cng2(self):
        toInternationalize = "benzyna+cng"
        self.assertEqual(DataCleaning.internationalizeFuel(toInternationalize), "petrol + cng")

    def test_internationalizes_fuel_electric(self):
        toInternationalize = "elektryczny"
        self.assertEqual(DataCleaning.internationalizeFuel(toInternationalize), "electric")

    def test_internationalizes_fuel_hydrogen(self):
        toInternationalize = "wodor"
        self.assertEqual(DataCleaning.internationalizeFuel(toInternationalize), "hydrogen")

    def test_internationalizes_fuel_ethanol(self):
        toInternationalize = "etanol"
        self.assertEqual(DataCleaning.internationalizeFuel(toInternationalize), "ethanol")

    def test_internationalizes_fuel_other(self):
        toInternationalize = "inny"
        self.assertEqual(DataCleaning.internationalizeFuel(toInternationalize), "other")

    def test_internationalizes_fuel_hybrid(self):
        toInternationalize = "hybryda"
        self.assertEqual(DataCleaning.internationalizeFuel(toInternationalize), "hybrid")

    def test_internationalizes_fuel_unknown(self):
        toInternationalize = "aaabbb"
        self.assertEqual(DataCleaning.internationalizeFuel(toInternationalize), "unknown")
#COLOR
    def test_internationalizes_color_white(self):
        toInternationalize = "biay"
        self.assertEqual(DataCleaning.internationalizeColor(toInternationalize), "white")

    def test_internationalizes_color_white2(self):
        toInternationalize = "biel"
        self.assertEqual(DataCleaning.internationalizeColor(toInternationalize), "white")

    def test_internationalizes_color_black(self):
        toInternationalize = "czarny"
        self.assertEqual(DataCleaning.internationalizeColor(toInternationalize), "black")

    def test_internationalizes_color_black2(self):
        toInternationalize = "czern"
        self.assertEqual(DataCleaning.internationalizeColor(toInternationalize), "black")

    def test_internationalizes_color_green(self):
        toInternationalize = "zielony"
        self.assertEqual(DataCleaning.internationalizeColor(toInternationalize), "green")

    def test_internationalizes_color_maroon(self):
        toInternationalize = "bordowy"
        self.assertEqual(DataCleaning.internationalizeColor(toInternationalize), "maroon")

    def test_internationalizes_color_silver(self):
        toInternationalize = "srebrny"
        self.assertEqual(DataCleaning.internationalizeColor(toInternationalize), "silver")

    def test_internationalizes_color_gray(self):
        toInternationalize = "szary"
        self.assertEqual(DataCleaning.internationalizeColor(toInternationalize), "gray")

    def test_internationalizes_color_red(self):
        toInternationalize = "czerwony"
        self.assertEqual(DataCleaning.internationalizeColor(toInternationalize), "red")

    def test_internationalizes_color_other(self):
        toInternationalize = "inny kolor"
        self.assertEqual(DataCleaning.internationalizeColor(toInternationalize), "other")

    def test_internationalizes_color_other2(self):
        toInternationalize = "inny"
        self.assertEqual(DataCleaning.internationalizeColor(toInternationalize), "other")

    def test_internationalizes_color_gold(self):
        toInternationalize = "zloty"
        self.assertEqual(DataCleaning.internationalizeColor(toInternationalize), "gold")

    def test_internationalizes_color_brown(self):
        toInternationalize = "brazowy"
        self.assertEqual(DataCleaning.internationalizeColor(toInternationalize), "brown")

    def test_internationalizes_color_beige(self):
        toInternationalize = "bezowy"
        self.assertEqual(DataCleaning.internationalizeColor(toInternationalize), "beige")

    def test_internationalizes_color_violet(self):
        toInternationalize = "fioletowy"
        self.assertEqual(DataCleaning.internationalizeColor(toInternationalize), "violet")

    def test_internationalizes_color_yellow(self):
        toInternationalize = "zolty"
        self.assertEqual(DataCleaning.internationalizeColor(toInternationalize), "yellow")

    def test_internationalizes_color_orange(self):
        toInternationalize = "pomaranczowy"
        self.assertEqual(DataCleaning.internationalizeColor(toInternationalize), "orange")

    def test_internationalizes_color_blue(self):
        toInternationalize = "niebieski"
        self.assertEqual(DataCleaning.internationalizeColor(toInternationalize), "blue")

    def test_internationalizes_color_blue(self):
        toInternationalize = "niebieski"
        self.assertEqual(DataCleaning.internationalizeColor(toInternationalize), "blue")

    def test_internationalizes_color_unknown(self):
        toInternationalize = "aaabbb"
        self.assertEqual(DataCleaning.internationalizeColor(toInternationalize), "unknown")

#STATE
    def test_internationalizes_state_new(self):
        toInternationalize = "nowy"
        self.assertEqual(DataCleaning.internationalizeState(toInternationalize), "new")

    def test_internationalizes_state_used(self):
        toInternationalize = "uzywany"
        self.assertEqual(DataCleaning.internationalizeState(toInternationalize), "used")

    def test_internationalizes_state_unknown(self):
        toInternationalize = "aaabbb"
        self.assertEqual(DataCleaning.internationalizeState(toInternationalize), "unknown")

#GEARBOX
    def test_internationalizes_gearbox_manual(self):
        toInternationalize = "manualna"
        self.assertEqual(DataCleaning.internationalizeGearbox(toInternationalize), "manual")

    def test_internationalizes_gearbox_half_automatic(self):
        toInternationalize = "poautomatyczna (asg)"
        self.assertEqual(DataCleaning.internationalizeGearbox(toInternationalize), "half-automatic")

    def test_internationalizes_gearbox_half_automatic2(self):
        toInternationalize = "poautomatyczna (asg, tiptronic)"
        self.assertEqual(DataCleaning.internationalizeGearbox(toInternationalize), "half-automatic")

    def test_internationalizes_gearbox_automatic(self):
        toInternationalize = "automatyczna"
        self.assertEqual(DataCleaning.internationalizeGearbox(toInternationalize), "automatic")

    def test_internationalizes_gearbox_automatic2(self):
        toInternationalize = "automatyczna hydrauliczna (klasyczna)"
        self.assertEqual(DataCleaning.internationalizeGearbox(toInternationalize), "automatic")

    def test_internationalizes_gearbox_dsg(self):
        toInternationalize = "automatyczna dwusprzeglowa (dct, dsg)"
        self.assertEqual(DataCleaning.internationalizeGearbox(toInternationalize), "automatic - dct, dsg")

    def test_internationalizes_gearbox_cvt(self):
        toInternationalize = "automatyczna bezstopniowa (cvt)"
        self.assertEqual(DataCleaning.internationalizeGearbox(toInternationalize), "automatic - cvt")

    def test_internationalizes_gearbox_cvt2(self):
        toInternationalize = "automatyczna bezstopniowa cvt"
        self.assertEqual(DataCleaning.internationalizeGearbox(toInternationalize), "automatic - cvt")

    def test_internationalizes_gearbox_unknown(self):
        toInternationalize = "aaabbb"
        self.assertEqual(DataCleaning.internationalizeGearbox(toInternationalize), "unknown")



class DataBaseOpsCreation(unittest.TestCase):
    def setUp(self):
        self.newDb = DataBase("UnitTests/test2.db")

    def test_db_new_file_created(self):
        self.assertTrue(os.path.exists("UnitTests/test2.db"))

    def test_db_new_table(self):
        newDict = OrderedDict([('ID', "INT"), ('name', "TEXT")])
        self.assertFalse(self.newDb.tableExists("NewTable"))
        self.newDb.createTable("NewTable", newDict)
        self.assertTrue(self.newDb.tableExists("NewTable"))

    def tearDown(self):
        del(self.newDb)
        self.addCleanup(os.remove, "UnitTests/test2.db")

class DataBaseOpsUsage(unittest.TestCase):
    def test_db_read_all_data_by_generator(self):
        allLinks = []

        for lnk in testDB.readAllDataGenerator("Links", 5):
            allLinks.append(lnk)

        self.assertEquals(len(allLinks), 15)

    def test_db_read_all_data_by_generator_with_interruption(self):
        allLinks = []

        for lnk in testDB.readAllDataGenerator("Links", 5):
            allLinks.append(lnk)
            testDB.tableExists("Links")

        self.assertEquals(len(allLinks), 15)

    def test_db_read_all_unparsed_links(self):
        allLinks = []

        for lnk in testDB.readAllDataGenerator("Links", where='WHERE parsed = "False"'):
            allLinks.append(lnk)

        self.assertEquals(len(allLinks), 0)
        testDB.executeSqlCommand("""UPDATE Links SET parsed = "False" """)
        self.assertFalse(testDB.valueIsPresentInColumnOfATable('True', "parsed", "Links"))

        allLinks = []

        for lnk in testDB.readAllDataGenerator("Links", where='WHERE parsed = "False"'):
            allLinks.append(lnk)

        self.assertEquals(len(allLinks), 15)
        testDB.executeSqlCommand("""UPDATE Links SET parsed = "True" """)
        self.assertFalse(testDB.valueIsPresentInColumnOfATable('False', "parsed", "Links"))


    def test_db_read_all_data(self):
        allLinks = []

        for lnk in testDB.readAllData("Links"):
            allLinks.append(lnk)

        self.assertEquals(len(allLinks), 15)

    def test_db_execute_custom_command(self):
        self.assertFalse(testDB.valueIsPresentInColumnOfATable('False', "parsed", "Links"))
        testDB.executeSqlCommand("""UPDATE Links SET parsed = "False" """)
        self.assertFalse(testDB.valueIsPresentInColumnOfATable('True', "parsed", "Links"))
        testDB.executeSqlCommand("""UPDATE Links SET parsed = "True" """)
        self.assertFalse(testDB.valueIsPresentInColumnOfATable('False', "parsed", "Links"))

    def test_db_get_all_ids_of_particular_brand(self):
        ids = testDB.getAllBrandIdsOfBrand("Honda")
        self.assertEquals(len(ids), 5)
        self.assertTrue(25 in ids)
        self.assertTrue(27 in ids)
        self.assertTrue(45 in ids)
        self.assertTrue(46 in ids)
        self.assertTrue(47 in ids)


    def test_db_get_all_ids_of_particular_model(self):
        ids = testDB.getAllBrandIdsOfModel("Accord")
        self.assertEquals(len(ids), 2)
        self.assertTrue(25 in ids)
        self.assertTrue(27 in ids)

    def test_db_get_id_of_version(self):
        iD = testDB.getVersionID("Accord", "V (1993-1998)")
        self.assertEquals(iD, 25)

    def test_db_get_all_cars(self):
        allCars = []

        for lnk in testDB.getAllCars():
            allCars.append(lnk)

        self.assertEquals(len(allCars), 14)

    def test_db_get_all_cars_of_brand(self):
        allCars = []

        for lnk in testDB.getAllCarsOfBrand("Honda"):
            allCars.append(lnk)

        self.assertEquals(len(allCars), 14)

    def test_db_get_all_cars_of_model(self):
        allCars = []

        for lnk in testDB.getAllCarsOfModel("Civic"):
            allCars.append(lnk)

        self.assertEquals(len(allCars), 7)

    def test_db_get_all_cars_of_version(self):
        allCars = []

        for lnk in testDB.getAllCarsOfVersion("Civic", "VII (2001-2006)"):
            allCars.append(lnk)

        self.assertEquals(len(allCars), 3)

    def test_db_get_all_cars_of_model(self):
        allCars = []

        for lnk in testDB.getAllCarsOfVersion("Civic", "VII (2001-2006)"):
            allCars.append(lnk)

        self.assertEquals(len(allCars), 3)

    def test_db_get_count_of_records(self):
        self.assertEquals(testDB.countRecordsInTable("links"), 15)

    def test_db_get_max_value(self):
        self.assertEquals(testDB.getMaxFromColumnInTable("l_id", "links"), 246)


if __name__ == "__main__":
    unittest.main()
