import requests
import schedule
import time
from datetime import datetime
import config
from flask import json

class Scheduler:
    def __init__(self, price_query_time = "0"):
        """ inits scheduler class """ 
        self.init_schedule()
        print("Init Scheduler")
          
    def init_schedule(self):
        # update weather
        schedule.every().hour.at(":00").do(self.updateWeatherData)
        schedule.every().hour.at(":05").do(self.updateWeatherData)
        schedule.every().hour.at(":15").do(self.updateWeatherData)

        # update prices
        schedule.every().hour.at(":01").do(self.updatePriceData)

        # update simulation
        schedule.every().hour.at(":20").do(self.simulateForecast)
        schedule.every().hour.at(":20").do(self.simulateNextHour)

        # update boiler power and fuel input
        schedule.every().hour.at(":03").do(self.updateBoilerInputOutput)

        # generate schedule
        schedule.every().day.at("19:05").do(self.generateSchedule)
        schedule.every().day.at("21:05").do(self.generateSchedule)
        schedule.every().day.at("23:05").do(self.generateSchedule)
        

    def updateWeatherData(self):
        r = requests.post(config.URL_WEATHER_SERVICE + "/updateWeather")
        print(self.formatTime(time.time()), "Update Weather", r)

    def updatePriceData(self):
        r = requests.post(config.URL_PRICE_SERVICE + "/updateprices")
        print(self.formatTime(time.time()), "Update Prices", r)

    def simulateNextHour(self):
        now = datetime.now()
        r = requests.post(config.URL_SIMULATION_SERVICE + "/simulation/nextHour/" + now.strftime("%Y-%m-%dT%H:%M:%S"))
        print(self.formatTime(time.time()), "Simulate Next Hour", r)

    def simulateForecast(self):
        r = requests.post(config.URL_SIMULATION_SERVICE + "/simulation/forecast")
        print(self.formatTime(time.time()), "Simulate Forecast", r)

    def generateSchedule(self):
        r = requests.post(config.URL_OPTIMIZER_SERVICE + "/optimizer/generateSchedule")
        print(self.formatTime(time.time()), "Generate Schedule", r)

    def updateBoilerInputOutput(self):
        responseSH = requests.post(config.URL_SPACE_HEATING_SERVICE + "/updateSpaceHeatingPower")
        print(self.formatTime(time.time()), "Update Space Heating Power", responseSH)

        responseDHW = requests.post(config.URL_HOT_WATER_SERVICE + "/updateHotWaterPower")
        print(self.formatTime(time.time()), "Update Hot Water Power", responseDHW)

        r = requests.post(config.URL_GAS_BOILER_SERVICE + "/gasBoilerService")
        print(self.formatTime(time.time()), "Update Gas Boiler Input", r)

    def formatTime(self, timestamp):
        return time.strftime("%b %d %Y %H:%M:%S", time.gmtime(timestamp))
    

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(10)



if __name__ == '__main__':
    s = Scheduler()
    s.run()

    

 
