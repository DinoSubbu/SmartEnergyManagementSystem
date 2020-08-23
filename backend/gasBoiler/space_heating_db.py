from database.databasehandler import MariaDB_handler
import database.spaceHeatingModel as spaceHeatingModel
import database.models as entitymodel
from gasBoiler.space_heating_api import SpaceHeatingAPI
from datetime import datetime, timedelta
from flask import jsonify, json
import requests
import config

class SpaceHeatingDB():

    def __init__(self, spaceHeatingDBConfig, entityDBConfig):
        self.entityDB = MariaDB_handler(**entityDBConfig)
        self.spaceHeatingDBObject = MariaDB_handler(**spaceHeatingDBConfig)
        self.spaceHeatingDBObject.createTables(spaceHeatingModel.Base)
        self.buildings = self.getAllBuildingData()
        self.spaceHeatingAPI = SpaceHeatingAPI(spaceHeatingDBConfig)

    def getAllBuildingData(self):
        try:
            buildings = []
            session_entity = self.entityDB.create_session()
            for building in self.entityDB.getAll(session_entity, entitymodel.Building):
                mathematicalModel = {
                                    "thermalResistance" : building.thermalResistance,
                                    "heatCapacityAirIndoor" : building.heatCapacityAirIndoor
                                    }
                buildings.append((building.name, building.lat, building.long, mathematicalModel))
        except Exception as e:
            print("Please Update database with entities")
            print (e)
            raise e
        finally:
            self.entityDB.close_session(session_entity)

        print(buildings)
        return buildings


    def getPowerSH(self, timestamp, buildingName, latitude, longitude):
        try:
            session = self.spaceHeatingDBObject.create_session()
            latitude = round(float(latitude),4)
            longitude = round(float(longitude),4)
            print(timestamp, buildingName, latitude, longitude)
            powerSHValue = session.query(spaceHeatingModel.SpaceHeating).filter(spaceHeatingModel.SpaceHeating.timestamp == timestamp). \
                filter(spaceHeatingModel.SpaceHeating.buildingName == buildingName).first()
            if powerSHValue:
                powerSHDict = powerSHValue.toDict()
                print(powerSHDict)
            return powerSHDict['powerSH']
        except Exception as e:
            print(e)
            self.spaceHeatingDBObject.close_session(session)


    def writePowerSHToDB(self, timestamp):
        if self.buildings==None:
            self.building = self.getAllBuildingData()
        try:
            session = self.spaceHeatingDBObject.create_session()
            print("Pinging weather service")
            for building in self.buildings:
                buildingName = building[0]
                latitude = building[1]
                longitude = building[2]
                mathematicalModel = building[3]
                payload = { 'lat' : latitude, 'longi' : longitude }
                response = requests.get(config.URL_WEATHER_SERVICE + "/currentWeather", params=payload)
                response =  json.loads(response.text)
                currentWeather = response['currentWeatherData']
                response_code = response['response_code']

                if response_code!=200:
                    print("Weather Data Unavailable!!")

                currentTempOutdoor = currentWeather['temp']
                currentTempIndoor, thermalPowerSH = self.spaceHeatingAPI.calculateThermalPowerSH(timestamp, buildingName, currentTempOutdoor, mathematicalModel)
                print(currentTempIndoor, thermalPowerSH )
                spaceHeatingData = spaceHeatingModel.SpaceHeating(timestamp, buildingName, latitude, longitude, currentTempIndoor, currentTempOutdoor, thermalPowerSH)
                self.spaceHeatingDBObject.addElementToDatabase(session, spaceHeatingData)
            self.spaceHeatingDBObject.close_session(session)
            
        except Exception as e:
            print(e)
            self.spaceHeatingDBObject.close_session(session)

if __name__ == "__main__":
    configDB = {'user':'myusr', 'password':'myusrpass', 'host':'localhost', 'port':'3306', 'database':'mydb'}
    spaceHeatingDB = SpaceHeatingDB(configDB, configDB)
    timestamp = datetime.strftime(datetime.now().replace(minute=0, second=0, microsecond=0), "%Y%m%d%H%M")
    spaceHeatingDB.writePowerSHToDB(timestamp)
