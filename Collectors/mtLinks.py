
from Queue import Queue
import threading

class mtLinksCollector(object):
    def __init__(self, listOfLinks):
        self.queue = Queue()
        self.outcomeDict = {}
        self.condition = threading.Condition()

    def populateQueue(self, listOfCategoryLinks):
        with self.condition:
            for link in listOfCategoryLinks:
                self.queue.put(link)

            self.condition.notifyAll()

    def collectTask(self, collectMethod):
        with self.condition:
            while self.queue.empty():
                self.condition.wait()
            else:
                catLink = self.queue.get()
                ##COLLECT STUFF FROM LINK AND SAVE IT TO DICTIONARY
            self.queue.task_done()
