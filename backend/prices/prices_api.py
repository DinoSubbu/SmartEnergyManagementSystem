import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

class PricesAPI():
    def __init__(self, periodStartDateTime=None, in_Domain="10Y1001A1001A82H", out_Domain="10Y1001A1001A82H"):
        """ inits prices request class """        

        # constants
        self.API_KEY = "42ee4b45-f276-4ef7-88ba-89e4964e54dd"
        self.API = "https://transparency.entsoe.eu/api?"
        
        self.documentType = "A44"
        self.in_Domain = in_Domain
        self.out_Domain = out_Domain             
        self.setTime(periodStartDateTime)
        # self.processType="A01"

        self.forgePayload()

    def setTime(self, periodStartDateTime):
         # compute periodStart and periodEnd (they are of form year month day hour minute  i.e. "201512312300")
        if (periodStartDateTime == None):
            periodStartDateTime = datetime.now()
        periodStartDateTime = periodStartDateTime.replace(minute=0, second=0, microsecond=0)
        
        self.periodStartDateTime = periodStartDateTime
        self.periodStart = periodStartDateTime.strftime("%Y%m%d%H%M")
        
        # periodEnd will be periodStart + one day
        periodEndDateTime = periodStartDateTime + timedelta(days=1)
        self.periodEnd = periodEndDateTime.strftime("%Y%m%d%H%M")

    def forgePayload(self):
        """ 
            forges the payload with the current attributes
            see https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html#_request_methods day ahead prices for details
        """
        self.payload = {
            'securityToken': self.API_KEY,
            'in_Domain': self.in_Domain,
            'out_Domain': self.out_Domain,
            'periodStart': self.periodStart,
            'periodEnd': self.periodEnd,
            # 'processType': self.processType,
            'documentType': self.documentType 
        }

    def getPriceForecast(self): 
        """ queries the api for the dynamic price data and returns the relevant information """       
        try:
            r = requests.get(self.API, self.payload)
            if r.status_code != 200: 
                print("not successfull status code: ", r.status_code)
                print(r.text)
                raise ConnectionError

            print("current prices gathered")
            # returned data is in xml 
            root = ET.fromstring(r.text)
            timeSeries = root[9]
            period = timeSeries[7]
            listOfPrices = []
            for index, point in enumerate(period):
                if (index > 1):
                    positionOfPoint = point[0].text
                    priceOfPoint = point[1].text
                    listOfPrices.append((positionOfPoint,priceOfPoint)) 

            return (self.periodStartDateTime, listOfPrices)         
            
        except requests.RequestException as e:
            print("request exception")
            print(e)
            raise e

if __name__ == "__main__":  
    prices = Prices()
    prices.forgePayload()
    priceList = prices.getPriceForecast()
    print(priceList)