import unittest
from simulation.supplyside.windTurbine import WindTurbineSim 
from simulation.supplyside.solarPanel import SolarPanelSim 

import pytemperature

class TestStringMethods(unittest.TestCase):
    # wind turbine 
    radius = 10
    efficiency = 1
    temp = 15
    relativeHumidity = 0.84
    windSpeed = 1.30776
    partialPressureDryPascal = 1020 * 100

    # solar panel
    temperatue_coefficient = 0.005
    angleOfModule = 40

    # def testSolarPanel(self):
    #     solarPanel = SolarPanelSim("test", 5, 5, 260, 1.3, self.temperatue_coefficient, self.angleOfModule)
    #     self.assertAlmostEqual(0.14,1 - solarPanel.computePerformanceRatio(25), 3)
    #     self.assertAlmostEqual(0.145,1 - solarPanel.computePerformanceRatio(26), 3)

    def testPartialPressureWaterVapor(self):
        turbine = WindTurbineSim("test", 5, 5, 1, self.radius)
        self.assertAlmostEqual(31.67, turbine.computePartialPressureWaterVapor(25, 1), 3)
        self.assertAlmostEqual(6.108, turbine.computePartialPressureWaterVapor(0, 1), 3)
        self.assertAlmostEqual(4.215, turbine.computePartialPressureWaterVapor(-5, 1), 3)
        self.assertAlmostEqual(17.044, turbine.computePartialPressureWaterVapor(15, 1), 3)

    def testWindTurbine(self):
        turbine = WindTurbineSim("test", 5, 5, 1, self.radius)
        # self.assertAlmostEqual(1.2334, turbine.computeAirDensity(self.temp, self.partialPressureDryPascal, self.relativeHumidity), 3)
        self.assertAlmostEqual(431.209, turbine.computePower(self.temp, self.partialPressureDryPascal, self.windSpeed, self.relativeHumidity), 2)

if __name__ == '__main__':
    unittest.main()