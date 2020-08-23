import math
from simulation.location_entity import LocationEntity
from database.models import SolarPanel

class SolarPanelSim(LocationEntity):
    """ computes the power of a solar panel """
    def __init__(self, name, lat, long, powerCoefficient, area, angleOfModule):
        """ inits the solarPanel with a latitude, surface area, a power coefficient and a temperature coefficient"""
        LocationEntity.__init__(self, name, lat, long)
        self.powerCoefficient = powerCoefficient
        self.area = area
        self.angleOfModule = angleOfModule

        # constants
        self.CONSTANT_LOSS = 0.14
        self.TEMPERATURE_COEFFICIENT = 0.005
    
    @classmethod
    def createFromModel(cls, solarPanel):
        return cls(solarPanel.name, solarPanel.lat, solarPanel.long, solarPanel.powerCoefficient, solarPanel.area, solarPanel.angleOfModule)

    def computePower(self, dayOfTheYear, temp, S_horizontal):
        """ computes the amount of power the solar panel generates at a specific timepoint """
        power = self.area * self.powerCoefficient * self.computePerformanceRatio(temp) * self.computeSolarIrradiance(dayOfTheYear, self.angleOfModule, S_horizontal)
        return power

    def computePerformanceRatio(self, temp):       
        tempDiff = temp - 25
        tempDiff = abs(tempDiff)
        temperatureLoss = tempDiff * self.TEMPERATURE_COEFFICIENT

        
        loss = temperatureLoss + self.CONSTANT_LOSS
        performanceRatio = 1 - loss
        return performanceRatio

    def computeSolarIrradiance(self, dayOfTheYear, beta, S_horizontal):
        """ computes the solar irradiance
            from https://www.pveducation.org/pvcdrom/properties-of-sunlight/solar-radiation-on-a-tilted-surface
            @return: solar irradiance in W/m^2
        """
        phi = float(self.lat)
        # sinus function takes radians
        delta = 23.45 * math.sin(math.radians((360/365) * (284 + dayOfTheYear)))
        alpha = 90 - phi + delta
        S_module = S_horizontal * math.sin(math.radians(alpha + beta)) / math.sin(math.radians(alpha))
        irradiance = S_module
        return irradiance

if __name__ == "__main__":
    
    solarPanel = SolarPanelSim("test", 10, 40, 5, 30, 0.5)        

    # solarPanel.computeSolarIrradiance(30, 45, 30)
    solarPanel.computePower(30, 20, 20)

