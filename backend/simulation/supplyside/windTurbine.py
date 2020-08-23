import math
import pytemperature

from simulation.location_entity import LocationEntity
from database.models import WindTurbine

class WindTurbineSim(LocationEntity):
    def __init__(self, name, lat, long, powerCoefficient, radius):
        """ 
        inits the wind turbine with a radius and a power coefficient
        @param radius: radius in m
        @param powerCoefficient: power coefficient in % (should be between 0.35 and 0.45 in practice)
        """
        LocationEntity.__init__(self, name, lat, long)
        self.powerCoefficient = powerCoefficient
        self.radius = radius

        # constants
        self.IDEAL_GAS = 8.314
        self.MODULAR_MASS_DRY = 0.029
        self.MODULAR_MASS_WATER_VAPOR = 0.018
        # wobus constants
        self.ES0 = 6.1078
        self.C = [None] * 10
        self.C[0] = 0.99999683 * 10**0
        self.C[1] = -0.90826951 * 10**-2
        self.C[2] = 0.78736169 * 10**-4
        self.C[3] = -0.61117958 * 10**-6
        self.C[4] = 0.43884187 * 10**-8
        self.C[5] = -0.29883885 * 10**-10
        self.C[6] = 0.21874425 * 10**-12
        self.C[7] = -0.17892321 * 10**-14
        self.C[8] = 0.11112018 * 10**-16
        self.C[9] = -0.30994571 * 10**-19

    @classmethod
    def createFromModel(cls, windTurbine):
        return cls(windTurbine.name, windTurbine.lat, windTurbine.long, windTurbine.powerCoefficient, windTurbine.radius)

    def computePower(self, temp, partialPressureDryPascal, windSpeed, relativeHumidity):
        """ 
        computes the amount of power the turbine generates at a specific timepoint 
        @param int: temp in °celsius
        @param windSpeed: wind speed in m/s
        @param partialPressureDryPascal: partialPressureDryPascal in pascal
        @param relativeHumidity: relative humidity in %
        """
        airDensity = self.computeAirDensity(temp, partialPressureDryPascal, relativeHumidity)
        sweptArea = self.radius * self.radius * math.pi
        power = 1/2 * airDensity * sweptArea * math.pow(windSpeed, 3) * self.powerCoefficient
        return power

    def computeAirDensity(self, temp, partialPressureDryPascal, relativeHumidity):
        """ computes the current air density """
        # auxiliary variables
        RT = self.IDEAL_GAS * pytemperature.c2k(temp)
        partialPressureWaterVapor = self.computePartialPressureWaterVapor(temp, relativeHumidity)
        partialDensityDry = partialPressureDryPascal * self.MODULAR_MASS_DRY / RT
        partialDensityWaterVapor = partialPressureWaterVapor * self.MODULAR_MASS_WATER_VAPOR / RT
        airDensity = partialDensityDry + partialDensityWaterVapor
        return airDensity
    
    def convertHPaToPa(self, pascal):
        """ converts parameter from hPa to Pa """
        return pascal * 100

    def computePartialPressureWaterVapor(self, temp, relativeHumidity):
        """ 
        computes the partial pressure of water vapor with a given temperature 
        @param temp: temperature in °Celsius
        
        """        
        saturatedVaporPressure = self.computeWobus(temp, relativeHumidity)
        # saturated vapor pressure needs to be converted to Pascal
        saturatedVaporPressure = self.convertHPaToPa(saturatedVaporPressure)
        partialPressureWaterVapor = relativeHumidity * saturatedVaporPressure
        return partialPressureWaterVapor

    def computeWobus(self, temp, relativeHumidity):
        """ 
        computes the saturated Vapor pressure with the Wobus algorithm
        @param temp: temperature in °Celsius
        @return: saturated vapor pressure in hPa
        """     
        # compute value from Wobus Polynomial
        wobus = self.C[9]
        for i in range(8, -1, -1):
            wobus = temp * wobus
            wobus = wobus + self.C[i]

        saturatedVaporPressure = self.ES0 / (math.pow(wobus, 8))
        return saturatedVaporPressure

if __name__ == "__main__":
    turbine = WindTurbineSim("test", 5, 5, 1, 10)

    power = turbine.computePower(15, 1000, 5, 10)
    print(power)
    # print(power)