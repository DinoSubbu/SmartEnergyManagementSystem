from database.databasehandler import MariaDB_handler
import database.gasBoilerModel as gasBoilerModel
import database.models as entitymodel
from gasBoiler.gas_boiler_api import GasBoilerAPI
from datetime import datetime, timedelta
import config
import requests
import json

class GasBoilerDB():

    def __init__(self, gasBoilerDBConfig, entityDBConfig):
        self.entityDB = MariaDB_handler(**entityDBConfig)
        self.gasBoilerAPI = GasBoilerAPI()
        self.gasBoilerDBObject = MariaDB_handler(**gasBoilerDBConfig)
        self.gasBoilerDBObject.createTables(gasBoilerModel.Base)
        self.buildings = self.getAllBuildingData()

    def getAllBuildingData(self):
            try:
                buildings = []
                session_entity = self.entityDB.create_session()
                for building in self.entityDB.getAll(session_entity, entitymodel.Building):
                    buildings.append((building.name, building.lat, building.long))
            except Exception as e:
                print("Please Update database with entities")
                print (e)
                raise e
            finally:
                self.entityDB.close_session(session_entity)
            return buildings

    def prepareInputForAPI(self, timestamp, buildingName, latitude, longitude):
        payload = {'timestamp':timestamp, 'buildingName':buildingName, 'latitude':latitude, 'longitude':longitude}
        responseDHW = requests.get(config.URL_HOT_WATER_SERVICE + "/getHotWaterPower", params=payload)
        responseDHW =  json.loads(responseDHW.text)
        print(responseDHW)
        powerDHW = responseDHW['powerDHW']
        responseSH = requests.get(config.URL_SPACE_HEATING_SERVICE + "/getSpaceHeatingPower", params=payload)
        responseSH =  json.loads(responseSH.text)
        print(responseSH)
        powerSH = responseSH['powerSH']
        return powerDHW, powerSH
        
    def writeFuelInputToDB(self, timestamp):
        session = self.gasBoilerDBObject.create_session()
        try:
            for building in self.buildings:
                buildingName = building[0]
                latitude = building[1]
                longitude = building[2]
                powerDHW, powerSH = self.prepareInputForAPI(timestamp, buildingName, latitude, longitude)
                powerDHW, powerSH, powerOutputBoiler, fuelInputBoiler = self.gasBoilerAPI.calculateFuelInput(powerDHW, powerSH)
                gasBoilerData = gasBoilerModel.GasBoiler(timestamp, buildingName, latitude, longitude, powerDHW, powerSH, powerOutputBoiler, fuelInputBoiler)
                self.gasBoilerDBObject.addElementToDatabase(session, gasBoilerData)
        except Exception as e:
            print(e)
            return
        finally:
            self.gasBoilerDBObject.close_session(session)
        
    
