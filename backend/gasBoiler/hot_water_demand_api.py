from datetime import datetime
import config
import csv
import os


############################################### Formula Explanation ##############################################
# Formula to calculate Heat Energy required :
    # Heat Energy (Joule) = Density_Water (kg/l) * Specific_Heat_water (J/Kg/degree Celsius) * Water_Demand (l) *
        #  Temp_Desired - Temp_Current (deg Celsius)
# Formula to convert from Heat energy to Power :
    # Power (Watt) = Heat Energy (Joule) / Time (s)
    # Example : 
        # Heat Energy required to achieve hot water demand in a hour = 3600 Joule
        # Power required = No of Joules per second
        # Assuming time frame of 1 hour = 3600 s
        # Power = 3600/3600 = 1 J/s = 1 W 
        # (i.e) 1 Joule of energy has to be supplied per second for a duration of 1 hr to meet the demand
##################################################################################################################

############################# Mathematical Constants ###################################
DENSITY_WATER = 1                   # 1 kg/l 
SPECIFIC_HEAT_CAPACITY_WATER = 4200  # 4.2KJ/Kg/degree Celsius --> 4200 J/Kg/deg Celsius
########################################################################################

class HotWaterAPI:
    """
    API to calculate power required for meeting hot water demand.
    Requires hot water demand profile in the form of csv.

    Attributes
    ----------
    buildingName : string
        name of the building where gas boiler is installed and hot water has to be supplied
    noOfOccupants : int
        number of occupants in a building
    desiredTempWater : float
        desired temperature of hot water. Reads from global config file
    currentTempWater : float
        current temperature of tap water. Reads from global config file
    demandProfile : dictionary
        hourly demand profile for a building
    hotWaterDemand : float
        amount of hot water (in litres) needed at the current hour of the day
    ThermalPowerDHW : float
        power (in Watts) needed to meet the hot water demand at the current hour of the day

    Methods
    -------
    getHotWaterProfile()
        based on the building name and no of occupants, selects the hot water demand profile for the entire day 
    getCurrentHotWaterDemand()
        returns the hot water demand (in litres) for the current hour
    getThermalPowerDHW(buildingName)
        returns power required (in Watt) for hot water demand

    """

    def __init__(self, noOfOccupants = 4):
        self.noOfOccupants = noOfOccupants
        self.desiredTempWater = config.DESIRED_TEMPERATURE_WATER
        self.currentTempWater = config.CURRENT_TEMPERATURE_WATER
        self.hotWaterDemand = 0

    def getHotWaterProfile(self):
        currentDirectory = os.path.abspath(os.path.dirname(__file__))
        pathCsv = os.path.join(currentDirectory, "dhw_demand_profiles/" + self.buildingName + ".csv")
        with open(pathCsv) as hotWaterProfilecsv:
            hotWaterCsvReader = csv.reader(hotWaterProfilecsv)
            demandProfile = [row for idx, row in enumerate(hotWaterCsvReader) if idx==self.noOfOccupants-1]
        demandProfile = demandProfile[0]
        demandProfile = {i:float(demandProfile[i]) for i in range(24)}
        return demandProfile

    def getCurrentHotWaterDemand(self):
        currentHour = datetime.now().hour
        return(self.demandProfile[currentHour])

    def getThermalPowerDHW(self, buildingName):
        self.buildingName = buildingName
        self.demandProfile = self.getHotWaterProfile()
        self.hotWaterDemand = self.getCurrentHotWaterDemand()
        heatEnergy = DENSITY_WATER * SPECIFIC_HEAT_CAPACITY_WATER * self.hotWaterDemand * \
            (self.desiredTempWater - self.currentTempWater)
        self.ThermalPowerDHW = heatEnergy / 3600
        return(self.ThermalPowerDHW)


