import logging


class Logger(object):
    @staticmethod
    def setLogger(name, filePath = '/media/pi/usb/logCarData/cardata.log'):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(name)s - %(levelname)s: %(message)s')
        fh = logging.FileHandler(filePath)
        fh.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger


