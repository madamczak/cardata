from OperationUtils.logger import Logger

moduleLogger = Logger.setLogger("Common URL Operations")
from bs4 import BeautifulSoup
import requests
import time
import inspect



def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def openLinkAndReturnSoup(url):
    start = time.time()
    moduleLogger.debug("Opening: %s" % url)
    try:
        agent = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
        page = requests.get(url, headers=agent, timeout=600)
    except:
        methodName = inspect.stack()[0][3]
        moduleLogger.info("%s - Problems with parsing %s, sleep 60 seconds." % (methodName, url))
        return None

    bsObject = BeautifulSoup(page.content, "lxml")

    moduleLogger.debug("Returning bs object from url: %s. It took %d seconds to parse it." % (url, time.time() - start))
    return bsObject
