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

    @classmethod
    def createFromModel(cls, battery, hour=0, currentEnergy=0):
        return cls(battery.name, battery.lat, battery.long, battery.batteryEfficiency, battery.chargeUpperBound, battery.dischargeUpperBound, battery.energyUpperBound, battery.selfDischargingRate, hour, currentEnergy)

    def calc(self, rate, hour):
        if rate > 0 :
            self.charge(self, rate, hour)
        elif rate < 0:
            self.discharge(self, rate, hour)
        else:
            self.idle(hour)

    def charge(self, rate, hour):
        if hour < 0 and hour > 23:
            raise ValueError()
        if currentHour < hour or (currentHour == 23 and hour == 0):
            if 0 <= rate <= self.chargeUpperBound:
                self.currentHour = hour
                self.currentState = BatteryState.CHARGING
                self.currentEnergy += self.batteryEfficiency*rate
                self.currentChargeRate = rate
                self.checkCurrentEnergy()
            else:
                raise ChargingException("The charging rate does not fulfill the constraints. {} <= {} <= {}".format(0, rate, self.chargeUpperBound))

    def discharge(self, rate, hour):
        if hour < 0 and hour > 23:
            raise ValueError()
        if currentHour < hour or (currentHour == 23 and hour == 0):
            if 0 <= rate <= self.dischargeUpperBound:
                self.currentHour = hour
                self.currentState = BatteryState.DISCHARGING
                self.currentEnergy += - rate/self.batteryEfficiency
                self.currentDischargeRate = rate
                self.checkCurrentEnergy()
            else:
                raise ChargingException("The discharging rate does not fulfill the constraints. {} <= {} <= {}".format(0, rate, self.dischargeUpperBound))

    def idle(self, hour):
        if hour < 0 and hour > 23:
            raise ValueError()
        if currentHour < hour or (currentHour == 23 and hour == 0):
            self.currentHour = hour
            self.currentState = BatteryState.IDLE
            self.currentEnergy -= selfDischargingRate
            self.checkCurrentEnergy()

    def checkCurrentEnergy(self):
        if self.currentEnergy < 0:
            self.currentEnergy = 0
            self.currentDischargeRate = 0
        elif self.currentEnergy > self.energyUpperBound:
            self.currentEnergy = self.energyUpperBound
            self.currentChargeRate = 0