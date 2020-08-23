from database.databasehandler import MariaDB_handler
import database.pricesModel as pricemodel
from prices.prices_api import PricesAPI
from datetime import datetime, timedelta

class PriceDB():

    def __init__(self, priceDBConfig):
        self.priceAPI = PricesAPI()
        self.priceDB = MariaDB_handler(**priceDBConfig)
        self.priceDB.createTables(pricemodel.Base)


    def writePriceToDB(self, time = None):
        currentTime = datetime.now()
        if not time:
            time = currentTime 
        self.priceAPI.setTime(time)
        self.priceAPI.forgePayload()
        try:
            response = self.priceAPI.getPriceForecast()
        except Exception as e:
            print(e)
            return
        print(response)
        day = response[0].replace(hour=0)
        prices = response[1]
        try:
            session = self.priceDB.create_session()
            for price in prices:
                timestamp = day + timedelta(hours=int(price[0])-1)
                forecastPrice = session.query(pricemodel.PriceForecast).filter_by(timestamp=timestamp).first()
                if forecastPrice:
                    forecastPrice.price = price[1]
                    forecastPrice.retrivalTime = currentTime
                    self.priceDB.commitOrRollback(session)
                else:
                    forecastPrice = pricemodel.PriceForecast(timestamp, currentTime, price[1])
                    self.priceDB.addElementToDatabase(session, forecastPrice)
        finally:
            self.priceDB.close_session(session)
        

if __name__ == "__main__":
    configDB = {'user':'myusr', 'password':'myusrpass', 'host':'localhost', 'port':'3306', 'database':'mydb'}
    priceDB = PriceDB(configDB)
    priceDB.writePriceToDB()
    priceDB.writePriceToDB(datetime.now() + timedelta(days =1))