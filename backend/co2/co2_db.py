from database.databasehandler import MariaDB_handler
import database.co2Model as co2model
from co2.co2_api import CarbonIntensityAPI
from datetime import datetime, timedelta

class Co2DB():

    def __init__(self, carbonIntensityDBConfig):
        self.carbonIntensityAPI = CarbonIntensityAPI()
        self.carbonIntensityDB = MariaDB_handler(**carbonIntensityDBConfig)
        self.carbonIntensityDB.createTables(co2model.Base)


    def writeCo2ValuesToDB(self):
        try:
            self.carbonIntensityAPI.getPowerGenData()
            response = self.carbonIntensityAPI.calculateCarbonIntensity()
            session = self.carbonIntensityDB.create_session()
            for timestamp in response:
                carbonIntensity = co2model.Co2ForecastProxy(timestamp, response[timestamp])
                self.carbonIntensityDB.addElementToDatabase(session, carbonIntensity)

        except Exception as e:
            print(e)
            return
  
        finally:
            self.carbonIntensityDB.close_session(session)
        

if __name__ == "__main__":
    configDB = {'user':'myusr', 'password':'myusrpass', 'host':'localhost', 'port':'3306', 'database':'mydb'}
    Co2DB = Co2DB(configDB)
    Co2DB.writeCo2ValuesToDB()
