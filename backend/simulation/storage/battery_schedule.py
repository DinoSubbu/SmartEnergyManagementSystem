from enum import Enum
from simulation.location_entity import LocationEntity
from database.models import Battery

class BatteryState(Enum):
    CHARGING = 1
    DISCHARGING = 2
    IDLE = 3

class ChargingException(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

class BatterySim(LocationEntity):

    def __init__(self, name, lat, long, batteryEfficiency, chargeUpperBound, dischargeUpperBound, energyUpperBound, selfDischargingRate, hour, currentEnergy = 0):
        LocationEntity.__init__(self, name, lat, long)
        self.currentState = BatteryState.IDLE
        self.batteryEfficiency = batteryEfficiency
        self.chargeUpperBound = chargeUpperBound
        self.currentChargeRate = 0
        self.dischargeUpperBound = dischargeUpperBound
        self.currentDischargeRate = 0
        self.selfDischargingRate = selfDischargingRate
        self.energyUpperBound = energyUpperBound
        self.currentEnergy = currentEnergy
        self.currentHour =  hour
        self.schedule = None

    @classmethod
    def createFromModel(cls, battery, hour=0, currentEnergy=0):
        return cls(battery.name, battery.lat, battery.long, battery.batteryEfficiency, battery.chargeUpperBound, battery.dischargeUpperBound, battery.energyUpperBound, battery.selfDischargingRate, hour, currentEnergy)

    def getEnergy(self, hour):
        if self.schedule != None:
            return self.schedule['energy'][hour]
        else:
            return 0

    def getRate(self, hour):
        if self.schedule != None:
            return self.schedule['rate'][hour]
        else:
            return 0

    def getState(self, hour):
        if self.schedule != None:
            stateString = self.schedule['state'][hour]
            if stateString == 'charging':
                return BatteryState.CHARGING
            elif stateString == 'discharging':
                return BatteryState.DISCHARGING
            else:
                return BatteryState.IDLE
        else:
            return BatteryState.IDLE

    def setSchedule(self, schedule):
        self.schedule = schedule