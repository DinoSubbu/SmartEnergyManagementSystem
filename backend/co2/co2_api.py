import requests
import json
from datetime import datetime
import xml.etree.ElementTree as ET
from datetime import timedelta
from io import StringIO 
import pprint
import sys

pp = pprint.PrettyPrinter(indent=4)

ENTSOE_GENERATION_TYPE_CODES ={
    'B01': 'Biomass',
    'B02': 'Fossil Brown coal/Lignite',
    'B03': 'Fossil Coal-derived gas', # Not applicable for Germany
    'B04': 'Fossil Gas',
    'B05': 'Fossil Hard coal',
    'B06': 'Fossil Oil',
    'B07': 'Fossil Oil shale', # Not applicable for Germany
    'B08': 'Fossil Peat', # Not applicable for Germany
    'B09': 'Geothermal',
    'B10': 'Hydro Pumped Storage',
    'B11': 'Hydro Run-of-river and poundage',
    'B12': 'Hydro Water Reservoir',
    'B13': 'Marine', # Not applicable for Germany
    'B14': 'Nuclear',
    'B15': 'Other renewable',
    'B16': 'Solar',
    'B17': 'Waste',
    'B18': 'Wind Offshore',
    'B19': 'Wind Onshore',
    'B20': 'Other',
}

ENTSOE_GENERATION_TYPE_GROUPS = {
    'biomass': ['B01', 'B17'],
    'coal': ['B02', 'B05', 'B07', 'B08'],
    'gas': ['B03', 'B04'],
    'geothermal': ['B09'],
    'hydro': ['B11', 'B12'],
    'nuclear': ['B14'],
    'oil': ['B06'],
    'solar': ['B16'],
    'wind': ['B18', 'B19'],
    'unknown': ['B20', 'B13', 'B15'],
    'hydro storage': ['B10']
}

# Source: IPCC 2014 Standards and Electricity Map
# CIPK - Carbon Intensity Per Kilowatt Hour
CIPK_VALUES_GENERATION_TYPE_GROUPS = {
    'biomass': 230,
    'coal': 820,
    'gas': 490,
    'geothermal': 38,
    'hydro': 24,
    'nuclear': 12,
    'oil': 650,
    'solar': 45,
    'wind': 11,
    'unknown': 700,
    'hydro storage': 345
}

CIPK_VALUES_FOR_PSR_TYPES = {
    'B01': 230,
    'B02': 820,
    'B03': 490, # Not applicable for Germany
    'B04': 490,
    'B05': 820,
    'B06': 650,
    'B07': 820, # Not applicable for Germany
    'B08': 820, # Not applicable for Germany
    'B09': 38,
    'B10': 345,
    'B11': 24,
    'B12': 24,
    'B13': 700, # Not applicable for Germany
    'B14': 12,
    'B15': 700,
    'B16': 45,
    'B17': 230,
    'B18': 11,
    'B19': 11,
    'B20': 700,
}



class CarbonIntensityAPI:
    def __init__(self, in_Domain = '10Y1001A1001A83F', startPeriod = None, endPeriod = None ):
        # Constants
        self.API_KEY = "42ee4b45-f276-4ef7-88ba-89e4964e54dd"
        self.API = "https://transparency.entsoe.eu/api?"

        self.documentType = 'A75' # Actual generation data per type
        self.in_Domain = in_Domain # Domain code for Germany
        self.processType = 'A16' # Realised - Actual Value
        self.genDataDict = {} # Dictionary which holds generation data for every generation group
        self.timestamps = []
        self.CIPKvalues = {}
        self.startPeriod = startPeriod
        self.endPeriod = endPeriod

        self.generateTimestamps(startPeriod, endPeriod)

    # Generates timestamps between 'startPeriod' and 'endPeriod'
    def generateTimestamps(self, startPeriod = None, endPeriod = None):
        if startPeriod == None or endPeriod == None:
            self.startPeriod = datetime.strftime(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1), "%Y%m%d%H%M")
            self.endPeriod = datetime.strftime(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0), "%Y%m%d%H%M")
            for i in range(0,24):
                # Previous day value is used as proxy for today's value. Add timedelta of 1 day
                timestampGeneration = datetime.strptime(self.startPeriod,"%Y%m%d%H%M") + timedelta( hours=(i),days=1 ) 
                self.timestamps.append(timestampGeneration)
        elif startPeriod > endPeriod:
            print ("Invalid Input. Start Period can not be higher that end period")
            sys.exit(1)
        elif (startPeriod.day > datetime.now().day):
            print ("Check the Start Period. Please use the script to get past co2 emission data or today's co2 emission forecast")
            sys.exit(1)
        elif (endPeriod > (datetime.now().replace(hour=0, minute=0) + timedelta(days=1))):
            print ("Please check the End Period. It can't be greater than today")
            sys.exit(1)
        else:
            timestamp = self.startPeriod
            while(timestamp < self.endPeriod):
                self.timestamps.append(datetime.strftime(timestamp, "%Y%m%d%H%M"))
                timestamp = timestamp + timedelta( hours=1 )
            pp.pprint(str(timestamp) + "  " + str(self.endPeriod))
            self.startPeriod = datetime.strftime(self.startPeriod, "%Y%m%d%H%M")
            self.endPeriod = datetime.strftime(self.endPeriod, "%Y%m%d%H%M")


    def getGenerationPerUnit(self, psrType):
        """Query and collect the power generation data of the previous day for
        a generation unit namely coal or gas.

        @return:
        """
        params = {
            'securityToken': self.API_KEY,
            'documentType': self.documentType,
            'processType': self.processType,
            'psrType': psrType,
            'in_Domain': self.in_Domain,
            'periodStart': self.startPeriod,
            'periodEnd': self.endPeriod
        }

        try:
            queryResponse = requests.get(self.API, params)
            if queryResponse.status_code != 200: 
                print("co2 api::Not Successful! Status code: ", queryResponse.status_code)
                # This error is raised, as certain psType is not applicable for Germany
                return
            
            # Received string is in HTML format 
            apiResponse = ET.iterparse(StringIO(queryResponse.text))
            for _, elementTag in apiResponse:
                prefix, has_namespace, postfix = elementTag.tag.partition('}')
                if has_namespace:
                    elementTag.tag = postfix  # strip all namespaces
            root = apiResponse.root
            
            generationData = {}
            for timeSeriesTag in root.iter('TimeSeries'):
                for periodTag in timeSeriesTag.iter('Period'):
                    for index, point in enumerate(periodTag):
                        if (index > 1):
                            positionOfPoint = int(point[0].text) - 1
                            priceOfPoint = int(point[1].text)
                            timestampGeneration = datetime.strptime(self.startPeriod,"%Y%m%d%H%M") + timedelta(minutes=(positionOfPoint * 15),days=1)
                            generationData[str(timestampGeneration)] = priceOfPoint
                return generationData
        
        except requests.RequestException as e:
            print("request exception")
            print(e)

    # Example: Group 'biomass' includes B01(biomass) and B17(waste)
    # Calculate Power Generation of every generation group for the previous day
    def getPowerGenData(self):
        for psrType in ENTSOE_GENERATION_TYPE_CODES:
            self.genDataDict[psrType] = self.getGenerationPerUnit(psrType)

    # CIPK Unit : gCO2eq/kWh
    def calculateCarbonIntensity(self):
        for timestamp in self.timestamps:
            totalPowerProduced = 0
            totalCarbonProduced = 0
            i = 0
            while(i < 4):
                for psrType in self.genDataDict:
                    if self.genDataDict[psrType] != None:
                        # Data has to be converted from MW to kWh
                        # Factor 0.25 : To convert from MW to MWh
                        # Factor 1000 : To convert from MWh to kWh
                        powerPerPsrType = self.genDataDict[psrType][str(timestamp)] * 1000 * 0.25    # Unit : kWh
                        totalPowerProduced = totalPowerProduced + ( powerPerPsrType )
                        totalCarbonProduced = totalCarbonProduced + ( powerPerPsrType * CIPK_VALUES_FOR_PSR_TYPES[psrType])
                timestamp = timestamp + timedelta(minutes=15)
                i = i + 1
            CIPK =  totalCarbonProduced / totalPowerProduced
            timestamp = timestamp - timedelta(hours=1)
            print(timestamp, totalPowerProduced , totalCarbonProduced )
            self.CIPKvalues[timestamp] = CIPK
        return self.CIPKvalues
                    

# datetime(year, month, day, hour, minute)
# Example: datetime(2017, 11, 28, 23, 55)
if __name__ == "__main__":  
    carbonIntensity = CarbonIntensityAPI()
    carbonIntensity.getPowerGenData()
    pp.pprint(carbonIntensity.calculateCarbonIntensity())
