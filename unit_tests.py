# -*- coding: utf8 -*-
from collections import OrderedDict
import time
import datetime

from OperationUtils.data_operations import DataCleaning
from OperationUtils.db_operations import DataBase
from SiteModules.Allegro.AllegroUrlOperations import AllegroURLOperations

import unittest
from mock import patch
from bs4 import BeautifulSoup
import os


emptySoup = BeautifulSoup("", "lxml")
testDB = DataBase("UnitTests/test.db")


class AllegroUrlParsing(unittest.TestCase):
    @patch('SiteModules.common_url_operations.openLinkAndReturnSoup', return_value=emptySoup)
    def test_returns_0_on_invalid_soup(self, mockSoup):
        price = AllegroURLOperations.getAllegroPrice(None)
        self.assertEqual(0, price)

    @patch('SiteModules.common_url_operations.openLinkAndReturnSoup', return_value=emptySoup)
    def test_returns_empty_dict_on_invalid_soup(self, mockSoup):
        parsedDict = AllegroURLOperations.parseAllegroSite(None)
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

class DataCleaningCarList(unittest.TestCase):
    def setUp(self):
        self.listOfCars = [
            (1087, 13281, 2009, 155278, 80, 1229, u'petrol', u'black', u'used', u'4/5', u'manual',
             u'\u0141\xf3d\u017a, woj. \u0142\xf3dzkie', 17900, u'2018-08-18 17:46:51.642188'),
            (1087, 13281, 1000, 1, 10, 10, u'petrol', u'black', u'used', u'4/5', u'unknown',
             u'\u0141\xf3d\u017a, woj. \u0142\xf3dzkie', 200, u'2018-08-18 17:46:51.642188'),
            (1087, 13281, datetime.date.today().year + 5, 9999999, 1500, 10000, u'petrol', u'black', u'used',
             u'4/5', u'unknown', u'\u0141\xf3d\u017a, woj. \u0142\xf3dzkie', 2000000, u'2018-08-18 17:46:51.642188')
        ]
    def test_clean_year(self):
        self.assertEqual(len(DataCleaning.cleanYear(self.listOfCars)), 1)

    def test_clean_mileage(self):
        self.assertEqual(len(DataCleaning.cleanMileage(self.listOfCars)), 1)

    def test_clean_power(self):
        self.assertEqual(len(DataCleaning.cleanPower(self.listOfCars)), 1)

    def test_clean_capacity(self):
        self.assertEqual(len(DataCleaning.cleanCapacity(self.listOfCars)), 1)

    def test_clean_price(self):
        self.assertEqual(len(DataCleaning.cleanPrice(self.listOfCars)), 1)

    def test_clean_unknown(self):
        lst = DataCleaning.cleanUnknowns(self.listOfCars)
        self.assertEqual(len(lst), 1)

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

    def test_get_all_brand_names(self):
        self.assertTrue("Honda" in testDB.getAllBrandNames())

    def test_get_all_model_names(self):
        models = testDB.getAllModelNamesOfBrand("Honda")
        self.assertTrue("Civic" in models)
        self.assertTrue("Accord" in models)

    def test_get_all_versions(self):
        versions = testDB.getAllVersionNamesOfModel("Civic")
        self.assertTrue("IV (1987-1991)" in versions)
        self.assertTrue("III (1983-1987)" in versions)
        self.assertTrue("VII (2001-2006)" in versions)



class DataCleaningVersionYears(unittest.TestCase):
    def test_version_production_begin_year_two_values(self):
        versionText = "E60 (2003-2010)"
        self.assertEquals(DataCleaning.getVersionProductionBeginYear(versionText), 2003)

    def test_version_production_begin_year_one_value(self):
        versionText = "F30 (2012-)"
        self.assertEquals(DataCleaning.getVersionProductionBeginYear(versionText), 2012)

    def test_version_production_begin_year_invalid_value(self):
        versionText = "E60"
        self.assertEquals(DataCleaning.getVersionProductionBeginYear(versionText), None)

    def test_version_production_end_year_two_values(self):
        versionText = "E60 (2003-2010)"
        self.assertEquals(DataCleaning.getVersionProductionEndYear(versionText), 2010)

    def test_version_production_end_year_one_values(self):
        versionText = "F30 (2012-)"
        self.assertEquals(DataCleaning.getVersionProductionEndYear(versionText), None)

    def test_version_production_begin_year_invalid_value(self):
        versionText = "F30"
        self.assertEquals(DataCleaning.getVersionProductionBeginYear(versionText), None)

class DataCleaningVersionText(unittest.TestCase):
    def test_version_name_Text2Years(self):
        versionText = "E60 (2003-2010)"
        self.assertEquals(DataCleaning.getVersionName(versionText), "E60")

    def test_version_name_Text1Year(self):
        versionText = "F30 (2012-)"
        self.assertEquals(DataCleaning.getVersionName(versionText), "F30")

    def test_version_name_1YearWithoutSpace(self):
        versionText = "F30(2012-)"
        self.assertEquals(DataCleaning.getVersionName(versionText), "F30")

    def test_version_name_1YearTooManySpaces(self):
        versionText = "F30   (2012-)"
        self.assertEquals(DataCleaning.getVersionName(versionText), "F30")

    def test_version_name_1YearTooManySpacesAtBegin(self):
        versionText = "    F30   (2012-)"
        self.assertEquals(DataCleaning.getVersionName(versionText), "F30")

    def test_version_name_OneSign(self):
        versionText = "V (2017-)"
        self.assertEquals(DataCleaning.getVersionName(versionText), "V")

    def test_version_name_TwoWords(self):
        versionText = "Seria E9 (1987-1992)"
        self.assertEquals(DataCleaning.getVersionName(versionText), "Seria E9")

    def test_version_name_ThreeWords(self):
        versionText = "GR I Y60 (1987-1997)"
        self.assertEquals(DataCleaning.getVersionName(versionText), "GR I Y60")

    def test_version_name_Slashes(self):
        versionText = "P10/W10 (1990-1998)"
        self.assertEquals(DataCleaning.getVersionName(versionText), "P10/W10")

    def test_version_name_Numbers(self):
        versionText = "996 (1997-2004)"
        self.assertEquals(DataCleaning.getVersionName(versionText), "996")





if __name__ == "__main__":
    unittest.main()
