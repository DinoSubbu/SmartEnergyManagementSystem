from database.databasehandler import MariaDB_handler
import database.hotWaterModel as hotWaterModel
import database.models as entitymodel
from gasBoiler.hot_water_demand_api import HotWaterAPI
from datetime import datetime, timedelta

class HotWaterDB():

    def __init__(self, hotWaterDBConfig, entityDBConfig):
        self.entityDB = MariaDB_handler(**entityDBConfig)
        self.hotWaterAPI = HotWaterAPI()
        self.hotWaterDBObject = MariaDB_handler(**hotWaterDBConfig)
        self.hotWaterDBObject.createTables(hotWaterModel.Base)

                
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
        print(buildings)
        return buildings


    def getPowerDHW(self, timestamp, buildingName, latitude, longitude):
            try:
                session = self.hotWaterDBObject.create_session()
                latitude = round(float(latitude),4)
                longitude = round(float(longitude),4)
                powerDHWValue = session.query(hotWaterModel.HotWater).filter(hotWaterModel.HotWater.timestamp == timestamp). \
                    filter(hotWaterModel.HotWater.buildingName == buildingName).first()
                if powerDHWValue:
                    powerDHWDict = powerDHWValue.toDict()
                print(powerDHWDict)
                return powerDHWDict['powerDHW']
            except Exception as e:
                print(e)
                self.hotWaterDBObject.close_session(session)


    def writePowerDHWToDB(self, timestamp):
        buildings = self.getAllBuildingData()
        session = self.hotWaterDBObject.create_session()
        try:
            for building in buildings:
                buildingName = building[0]
                latitude = building[1]
                longitude = building[2]
                powerDHW = self.hotWaterAPI.getThermalPowerDHW(buildingName)
                hotWaterDBData = hotWaterModel.HotWater(timestamp, buildingName, latitude, longitude, powerDHW)
                self.hotWaterDBObject.addElementToDatabase(session, hotWaterDBData)
        except Exception as e:
            print(e)
        finally:
            self.hotWaterDBObject.close_session(session)
        

if __name__ == "__main__":
    configDB = {'user':'myusr', 'password':'myusrpass', 'host':'localhost', 'port':'3306', 'database':'mydb'}
    hotWaterDB = HotWaterDB(configDB, configDB)
    timestamp = datetime.strftime(datetime.now().replace(minute=0), "%Y%m%d%H%M")
    hotWaterDB.writePowerDHWToDB(timestamp)
