import matplotlib.pyplot as plt

class Plots(object):
    @staticmethod
    def drawYearsHistogram(yearsList):
        plt.hist(yearsList, bins=(2016-1980), range=[1980,2016])
        plt.title("Histogram of car age")
        plt.xlabel("Year of production")
        plt.ylabel("Frequency")
        plt.show()
