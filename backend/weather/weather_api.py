import requests
import json
from sqlalchemy import Column, Text, Integer, Float, ForeignKey, DateTime
from datetime import datetime

class WeatherAPI:
    def __init__(self, api_key="3d34a9a9b0e544269a3ddbb97ec89ba7", api_current="https://api.weatherbit.io/v2.0/current", api_forecast = "https://api.weatherbit.io/v2.0/forecast/hourly?"):
        """ inits weather request class """        
        # constants
        self.API_KEY = api_key

        # necessary data for request
        self.API_CURRENT = api_current
        self.API_FORECAST = api_forecast
  

    def getCurrent(self, lat, lon): 
        """ 
            queries the api for the current weather and returns the relevant information
            @return: weatherdata as dict:   
                timestamp
                temp in °celsius
                windSpeed in m/s
                pressure in Pa
                relativeHumidity in %
        """   
        payloadCurrent = {'lat': str(lat), 'lon':str(lon), 'key': self.API_KEY}    
        try:
            r = requests.get(self.API_CURRENT, payloadCurrent)
            if r.status_code != 200: 
                print("not successfull status code: ", r.status_code)
                print(r.text)
                return

            print("current weather data gathered")
            # returned data is in json 
            data = r.json()["data"][0]
            # TODO timestamp
            # timestamp with request is given in utc and not local time
            # timestamp is encoded like "2017-08-28:17"
            # timestampString = data["datetime"]
            # # convert from string to datetime object
            # timestamp = datetime.strptime(timestampString, '%Y-%m-%d:%H')
            timestamp = datetime.now()
            # timestamp has to be aligned to hourly basis
            timestamp = timestamp.replace(minute=0, second=0, microsecond=0)
            #  get needed attributes of json object
            tempData = {}
            tempData["timestamp"] = timestamp
            tempData["temp"] = data["temp"]
            tempData["windSpeed"] = data["wind_spd"]
            # pressure is returned in millibar 
            # needs to be converted to pascal
            tempData["pressure"] = data["pres"] * 100
            tempData["relativeHumidity"] = data["rh"]
            tempData["s_horizontal"] = data["ghi"]
            return tempData
        except requests.RequestException as e:
            print("request exception")
            print(e)

    def getForecast(self, lat, lon):
        """ 
        queries the api for the forecast weather and returns the relevant information 
        @return: Array of weatherdata as dict:   
                timestamp
                temp in °celsius
                windSpeed in m/s
                pressure in Pa
                relativeHumidity in %
        """   
        payloadForecast = {'lat': str(lat), 'lon':str(lon), 'key': self.API_KEY, 'hours': '48'}    
        try:
            r = requests.get(self.API_FORECAST, payloadForecast)
            if r.status_code != 200: 
                print("not successfull status code: ", r.status_code)
                print(r.text)
                return

            print("forecast weather data gathered")
            # returned data is in json 
            data = r.json()["data"]
            dataArray = []
            for dataElement in data:                
                # get needed attributes of json object
                # timestamp is encoded like "2018-04-02T00:00:00"
                timestampString = dataElement["timestamp_local"]
                # convert from string to datetime object
                timestamp = datetime.strptime(timestampString, '%Y-%m-%dT%H:%M:%S')
                tempData = {}
                tempData["timestamp"] = timestamp
                tempData["temp"] = dataElement["temp"]
                tempData["windSpeed"] = dataElement["wind_spd"]
                # pressure is returned in millibar 
                # needs to be converted to pascal
                tempData["pressure"] = dataElement["pres"] * 100
                tempData["relativeHumidity"] = dataElement["rh"]
                tempData["s_horizontal"] = dataElement["ghi"]
                dataArray.append(tempData)
                
            return dataArray
        except requests.RequestException as e:
            print("request exception")
            print(e)

if __name__ == "__main__":
    weather = WeatherAPI()
    print(weather.getForecast(48.78232, 9.17702))
