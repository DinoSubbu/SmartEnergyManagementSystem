from datetime import datetime


################################################### Formula Explanation #################################################
# Formula to calculate the power to be produced by boiler :
    # Boiler output power (Watt) = power needed / Efficiency_boiler
        # power needed (Watt) = Power_space_heating + power_hot_water
# Formula to calculate boiler fuel required :
    # amount of gas to be fed (kg) = boiler_output_power (watt) * time (1 hour) / calorific_value_natural_gas (Kwh/kg)
    # Example : amount of gas needed = 2 kg
    # (i.e) in a time frame of 1 hour, a total of 2 kg of fuel have to be fed to meet space heating and hot water demand     
###########################################################################################################################

############################# Mathematical Constants#############################
EFFICIENCY_BOILER = 0.9
CALORIFIC_VALUE_NET_NATURAL_GAS = 10600 # 10.6 Kwh/kg  --> 10600 Wh/kg
# Calorific value source : 
# https://www.forestresearch.gov.uk/tools-and-resources/biomass-energy-resources/reference-biomass/facts-figures/typical-calorific-values-of-fuels/
#################################################################################

class GasBoilerAPI:
    """
    API to calculate amount of fuel (natural gas in kg) to be fed
    Requires space heating power and hot water power for calculation

    Attributes
    ----------
    boilerOutput : float
        power output of the boiler (W)
    boilerInput : float
        amount of fuel to be fed (kg) for a hour

    Methods
    -------
    calculateFuelInput()
        calculate amount of fuel needed by using space heating and hot water power 

    """
    def __init__(self):
        self.boilerOutput = 0
        self.boilerInput = 0

    def calculateFuelInput(self, powerDHW, powerSH):
        print("Calculating Gas Boiler fuel input")
        thermalPowerNeeded = float(powerDHW) + float(powerSH)
        self.boilerOutput = thermalPowerNeeded / EFFICIENCY_BOILER
        boilerInput = self.boilerOutput * 1 / CALORIFIC_VALUE_NET_NATURAL_GAS
        self.boilerInput = boilerInput * 1000 # Conversion from Kg to grams
        return float(powerDHW), float(powerSH), thermalPowerNeeded, self.boilerInput



