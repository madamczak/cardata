import matplotlib.pyplot as plt

from OperationUtils.data_operations import DataOperations
from OperationUtils.db_operations import DataBase


class Plots(object):

    @staticmethod
    def drawYearsHistogram(yearsList, minRange = 1980, maxRange = 2017):
        plt.hist(yearsList, bins=(maxRange-minRange), range=[minRange,maxRange])
        plt.title("Histogram of car age")
        plt.xlabel("Year of production")
        plt.ylabel("Frequency")
        plt.show()

    @staticmethod
    def drawYearsHistogramFromRows(rows, minRange=1980, maxRange=2017):
        yearsList = [car[2] for car in rows]
        plt.hist(yearsList, bins=(maxRange - minRange), range=[minRange, maxRange])
        plt.title("Histogram of car age")
        plt.xlabel("Year of production")
        plt.ylabel("Frequency")
        plt.show()


    @staticmethod
    def drawAverageMileagePlot(carsList):
        years = range(2001, 2007)

        avgMileages = []

        for yearOfProduction in range(2001, 2007):
            carsOfParticularYear = DataOperations.getCarsProducedInYear(carsList, yearOfProduction)
            avg = sum([car[3] for car in carsOfParticularYear])/len(carsOfParticularYear)
            avgMileages.append(avg)
            print avg

        plt.plot(years, avgMileages, 'r--', )
        plt.xlabel("Year of production")
        plt.ylabel("Average mileage")
        plt.title("Average mileage per year")
        plt.show()

    @staticmethod
    def drawCarPoints(carsList):
        years = [car[2] for car in carsList]

        mileages = [car[3] for car in carsList]

        plt.plot(years, mileages, 'ro', )
        plt.xlabel("Year of production")
        plt.ylabel("Mileage")
        plt.title("AAAAAAAAAA")
        plt.show()


db = DataBase("refactor_test6.db")
cars = db.getAllCarsOfModel("Fusion")
print len(cars)
yearCarMileageDict = {}
yearCarPriceDict = {}
for year in range(2002, 2013):
    # avg mileage
    yearCarMileageDict[year] = sum([car[3] for car in cars if car[2] == year])/len([car for car in cars if car[2] == year])
    #avg price
    yearCarPriceDict[year] = sum([car[-2] for car in cars if car[2] == year])/len([car for car in cars if car[2] == year])
#     for car in cars:
#         if car[2] == year:
#             yearCarDict[year].append(car)
#
# print len(yearCarDict[2003])



plt.plot([car[3] for car in cars if car[3] < 180000 and car[3] > 80000 and car[-2] < 20000],
         [car[-2] for car in cars if car[3] < 180000 and car[3] > 80000 and car[-2] < 20000], 'ro', )
plt.xlabel("Year of production")
plt.ylabel("Mileage")
plt.title("AAAAAAAAAA")
plt.show()