class BrandsCollector(object):
    def __init__(self, database):
        self.db = database

    def Collect(self):
        raise NotImplementedError("Not implemented")
