import datetime

from OperationUtils.logger import Logger
from SiteModules.common_brands_collector import BrandsCollector
import inspect


moduleLogger = Logger.setLogger("OtoMotoBrandsCollector")
TOPLINK = "https://www.otomoto.pl/"

# otomoto brands should not be collected for now. Brands should be in the db as they are created from allegro site
class OtoMotoBrandsCollector(BrandsCollector):
    def Collect(self, limit=2000):
        methodName = inspect.stack()[0][3]
        return 0, datetime.datetime.now()
