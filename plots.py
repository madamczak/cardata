import matplotlib.pyplot as plt

class Plots(object):
    @staticmethod
    def drawYearsHistogram(yearsList):
        plt.hist(yearsList, bins=(2016-1980), range=[1980,2016])
        plt.title("Histogram of car age")
        plt.xlabel("Year of production")
        plt.ylabel("Frequency")
        plt.show()

    @staticmethod
    def drawAverageMileagePlot(mileageList, yearsList, rangeOfYears):
        avg = []
        for year in rangeOfYears:
            listOfEachYearMileages = [m for m, y in zip(mileageList, yearsList) if y == year]
            avg.append(sum(listOfEachYearMileages)/float(len(listOfEachYearMileages)))
        plt.plot(range(1980, 2017), avg)
        plt.xlabel("Year of production")
        plt.ylabel("Average mileage")
        plt.title("Average mileage per year")
        plt.show()


