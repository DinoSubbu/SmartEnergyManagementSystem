from database.databasehandler import MariaDB_handler
import database.spaceHeatingModel as spaceHeatingModel
import requests
import config
from datetime import datetime, timedelta
import math


#################################################################### Formula Explanation ########################################################################################
# Exponent Term:
    # Exponent_Term = exp(-TIME_STEP_HR {hour} / (Thermal_Resistance {deg Celcius/W} * Heat_Capactity_Air_Indoor {Wh/degree Celsius} )
# Formula to calculate thermal power required :
    # Space Heating Power (Watt) = Expression_1 - Expression_2
    # Expression_1 = ( (Desired_Indoor_Temperature {deg Celsius} - (Current_Indoor_Temperature {deg Celsius} * Exponent_Term {No Unit}) ) 
        #  / Thermal_Resistance {deg Celcius/W} * (1 - Exponent_Term {No Unit} ) ) )
    # Expression_2 = Current_Temperature_Outdoor {degree Celsius} / Thermal_Resistance {deg Celcius/W}

# Formula to calculate dynamic indoor temperature:
    # Current_Indoor_Temperature {deg Celsius} = (Indoor_Temperature_Previous_Iteration {deg Celsius} * Exponent_Term) + ( ( \
        # Thermal_Resistance {deg Celcius/W} * Thermal_Power_Previous_Iteration {Watt} ) + Temperature_Outdoor_Previous_Iteration {deg Celcius} ) * (1- Exponent_Term) )
#################################################################################################################################################################################


################ Constants #######################
TIME_STEP_HR = 1                         # 1 hour
TIME_STEP_SEC = 3600                     # 1 hour --> 3600 s
#TEMP_INDOOR_DESIRED = 25                # 25 degree celsius
#THERMAL_RESISTANCE = 0.018              # 18 deg Celsius/KW --> 0.018 deg Celsius/W
#HEAT_CAPACITY_AIR_INDOOR = 525          # 0.525 Kwh/ degree Celsius --> 525 Wh/degree Celsius

# Note: Commented constants are read either from Database or from global config file
####################################################


class SpaceHeatingAPI():
    """
    API to calculate power required for space heating.
    Requires weather data to calculate power required for space heating.

    Attributes
    ----------
    buildingName : string
        name of the building where gas boiler is installed and space heating has to be done

    prevTempIndoor : float
        calculated indoor temperature in previous iteration. Parameter is read from database
    currentTempIndoor : float
        calculated current indoor temperature

    prevTempOutdoor : float
        outdoor temperature provided by weather api in previous iteration. Parameter is read from database
    currentTempOutdoor : float
        current outdoor temperarure. Data is provided by weather api

    prevThermalPowerSH : float
        calculated power (Watt) for space heating in previous iteration. Parameter is read from database
    currentThermalPowerSH : float
        calculated power (Watt) for space heating in current iteration

    tempIndoorDesired : float
        desired indoor temperature. Reads from global config file
    thermalResistance : float
        thermal resistance of the building. Parameter is read from database
    heatCapacityAirIndoor : float
        heat capacity of the indoor air. Parameter is read from database
    

    Methods
    -------
    getBuildingConstants()
        get mathematical model of a building from database 
    calculateCurrentTempIndoor()
        calculate current indoor temperature
    calculateThermalPowerSH(buildingName)
        returns power required (in Watt) for space heating

    """
    def __init__(self, spaceHeatingDBConfig):
        self.spaceHeatingDB = MariaDB_handler(**spaceHeatingDBConfig)
        self.prevTempIndoor = config.TEMP_INDOOR_INITIAL
        self.prevThermalPowerSH = 0
        self.tempIndoorDesired = config.TEMP_INDOOR_DESIRED

    def getBuildingConstants(self, buildingModel):
        self.thermalResistance = buildingModel['thermalResistance']
        self.heatCapacityAirIndoor = buildingModel['heatCapacityAirIndoor']
        self.exponentTerm = math.exp(-TIME_STEP_HR/(self.thermalResistance * self.heatCapacityAirIndoor))

    def calculateCurrentTempIndoor(self):
        try:
            session_SH = self.spaceHeatingDB.create_session()
            prevTimestamp = datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
            prevSpaceHeatingValue = session_SH.query(spaceHeatingModel.SpaceHeating).filter(spaceHeatingModel.SpaceHeating.timestamp>=prevTimestamp, \
                spaceHeatingModel.SpaceHeating.buildingName==self.buildingName).first()
            if prevSpaceHeatingValue:
                spaceHeatingDict = prevSpaceHeatingValue.toDict()
                print (spaceHeatingDict)
                self.prevTempIndoor = spaceHeatingDict['temperatureIndoor']
                self.prevThermalPowerSH = spaceHeatingDict['powerSH']
                self.prevTempOutdoor = spaceHeatingDict['temperatureOutdoor']
            else:
                # Values are not available. Set default values
                self.prevTempOutdoor = self.currentTempOutdoor
            
            self.currentTempIndoor = (self.prevTempIndoor * self.exponentTerm) + ( ( \
                (self.thermalResistance * self.prevThermalPowerSH) + self.prevTempOutdoor) * (1- self.exponentTerm) )
            #self.currentTempIndoor = self.prevTempIndoor + ((TIME_STEP_SEC/self.heatCapacityBuilding) \
                #* ( self.prevThermalPowerSH - (self.heatLossCoefficientBuilding * (self.prevTempIndoor - self.prevTempOutdoor) ) ) )
        except Exception as e:
            print(e)
            return
        finally:
            self.spaceHeatingDB.close_session(session_SH)

    def calculateThermalPowerSH(self, timestamp, buildingName, currentTempOutdoor, buildingModel):
        self.currentTempOutdoor = currentTempOutdoor
        self.buildingName= buildingName
        self.getBuildingConstants(buildingModel)
        self.calculateCurrentTempIndoor()
        
        firstTerm = ( (self.tempIndoorDesired - (self.currentTempIndoor * self.exponentTerm) )  / (self.thermalResistance * (1 - self.exponentTerm) ) )
        secondTerm = currentTempOutdoor / self.thermalResistance
        self.currentThermalPowerSH = firstTerm - secondTerm
        return self.currentTempIndoor, self.currentThermalPowerSH


