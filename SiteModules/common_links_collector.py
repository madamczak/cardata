class LinksCollector(object):
    def __init__(self, database):
        self.db = database
        self.result_dict = {}

    def Collect(self):
        raise NotImplementedError("Not implemented")
