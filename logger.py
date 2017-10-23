import logging


def setUpLogger(loggerName):
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG)
    # logging.basicConfig(filename='myapp.log', format='%(levelname)s:%(message)s', level=logging.DEBUG)
    formatter = logging.Formatter('%(name)s - %(levelname)s: %(message)s')
    fh = logging.FileHandler('cardata.log')
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger