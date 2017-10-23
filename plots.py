import matplotlib.pyplot as plt

from data_operations import DataOperations
from db_operations import DataBase


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


db = DataBase("cars_work_2.db")
cars = db.getAllCarsOfVersion("Civic", "VII (2001-2006)")

Plots.drawCarPoints(cars)