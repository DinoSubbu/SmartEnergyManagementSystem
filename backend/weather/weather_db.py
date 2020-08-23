import database.weatherModel as weathermodel
import database.models as entitymodel
from database.databasehandler import MariaDB_handler
from weather.weather_api import WeatherAPI
from sqlalchemy.exc import IntegrityError

class WeatherDB():

    def __init__(self, weatherDBConfig, entityDBConfig):
        self.weatherDB = MariaDB_handler(**weatherDBConfig)
        self.weatherDB.createTables(weathermodel.Base)
        self.entityDB = MariaDB_handler(**entityDBConfig)
        self.entityDB.createTables(entitymodel.Base)
        self.weatherAPI = WeatherAPI()

    def writeWeatherToDB(self):
        locations = []
        try:
            session_entity = self.entityDB.create_session()
            for solarpanel in self.entityDB.getAll(session_entity, entitymodel.SolarPanel):
                locations.append((solarpanel.lat, solarpanel.long))
            for windturbine in self.entityDB.getAll(session_entity, entitymodel.WindTurbine):
                locations.append((windturbine.lat, windturbine.long))
        except Exception as e:
            print("Please Update database with entities")
            print (e)
            raise e
        finally:
            self.entityDB.close_session(session_entity)
        # remove duplicates
        locations = set(locations)
        print(locations)
        try:
            session_weather = self.weatherDB.create_session()
            for location in locations:
                lat = location[0]
                long = location[1]
                currentWeatherData = self.weatherAPI.getCurrent(lat, long)
                currentWeather = session_weather.query(weathermodel.WeatherCurrent).filter_by(lat=lat, long=long, timestamp=currentWeatherData["timestamp"]).first()
                if currentWeather:
                    currentWeather.temp = currentWeatherData["temp"]
                    currentWeather.windSpeed = currentWeatherData["windSpeed"]
                    currentWeather.pressure = currentWeatherData["pressure"]
                    currentWeather.relativeHumidity = currentWeatherData["relativeHumidity"]
                    currentWeather.s_horizontal = currentWeatherData["s_horizontal"]
                    self.weatherDB.commitOrRollback(session_weather)
                else:
                    currentWeather = weathermodel.WeatherCurrent(lat, long, **currentWeatherData)
                    self.weatherDB.addElementToDatabase(session_weather, currentWeather)

            
            for location in locations:
                lat = location[0]
                long = location[1]
                forecastWeatherList = self.weatherAPI.getForecast(lat, long)
                for forecastWeatherData in forecastWeatherList:
                    forecastWeather = session_weather.query(weathermodel.WeatherForecast).filter_by(lat=lat, long=long, timestamp=forecastWeatherData["timestamp"]).first()
                    if forecastWeather:
                        forecastWeather.temp = forecastWeatherData["temp"]
                        forecastWeather.windSpeed = forecastWeatherData["windSpeed"]
                        forecastWeather.pressure = forecastWeatherData["pressure"]
                        forecastWeather.relativeHumidity = forecastWeatherData["relativeHumidity"]
                        forecastWeather.s_horizontal = forecastWeatherData["s_horizontal"]
                        self.weatherDB.commitOrRollback(session_weather)
                    else:
                        forecastWeather = weathermodel.WeatherForecast(lat, long, **forecastWeatherData)
                        self.weatherDB.addElementToDatabase(session_weather, forecastWeather)
        except Exception as e:
            raise e
        finally:
            self.weatherDB.close_session(session_weather)
        

            

if __name__ == "__main__":
    configDB = {'user':'myusr', 'password':'myusrpass', 'host':'localhost', 'port':'3306', 'database':'mydb'}
    weatherDb = WeatherDB(configDB, configDB)
    weatherDb.writeWeatherToDB()