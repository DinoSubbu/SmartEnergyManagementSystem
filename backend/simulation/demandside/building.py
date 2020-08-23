from simulation.demandside.component import ComponentSim
from simulation.location_entity import LocationEntity
from database.models import Building

class BuildingSim(LocationEntity):

    def __init__(self, name, lat, long, listOfComponents, historicalData, hour = 0):
        LocationEntity.__init__(self, name, lat, long)
        self.listOfComponets = listOfComponents
        self.historicalData = historicalData
        self.hour = hour
    
    @classmethod
    def createFromModel(cls, building):
        listOfComponets = []
        for comp in building.components:
            listOfComponets.append(ComponentSim(comp.name, comp.est, comp.let, comp.e, comp.lot))
        return cls(building.name, building.lat, building.long, listOfComponets, building.historicalData)
    
    @classmethod
    def household(cls, name, lat, long):
        washing_machine = ComponentSim("washing_machine", 9, 17, 2, 2)
        dish_washer = ComponentSim("dish_washer", 9, 12, 1.8, 2)
        spin_dryer = ComponentSim("spin_dryer", 13, 18, 2.5, 1)
        electrical_vehicle = ComponentSim("electrical_vehicle", 18, 24, 3.5, 3)
        vacuum_cleaner = ComponentSim("vacuum_cleaner", 9, 17, 1.2, 1)
        listOfComponets = [washing_machine, dish_washer, spin_dryer, electrical_vehicle, vacuum_cleaner]
        historicalData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        return cls(name, lat, long, listOfComponets, historicalData)

    @classmethod
    def office(cls, name, lat, long):
        dish_washer1 = ComponentSim("dish_washer1", 9, 12, 1.8, 2)
        dish_washer2 = ComponentSim("dish_washer2", 9, 12, 1.8, 2)
        dish_washer3 = ComponentSim("dish_washer3",9, 12, 1.8, 2)
        dish_washer4 = ComponentSim("dish_washer4",9, 12, 1.8, 2)
        vacuum_cleaner1 = ComponentSim("vacuum_cleaner1", 7, 10, 1.2, 1)
        vacuum_cleaner2 = ComponentSim("vacuum_cleaner2", 7, 9, 1.2, 1)
        vacuum_cleaner3 = ComponentSim("vacuum_cleaner3", 19, 21, 1.2, 1)
        vacuum_cleaner4 = ComponentSim("vacuum_cleaner4", 19, 23, 1.2, 1)
        electrical_vehicle1 = ComponentSim("electrical_vehicle1", 8, 18, 3.5, 3)
        electrical_vehicle2 = ComponentSim("electrical_vehicle2",18, 24, 3.5, 3)
        listOfComponets = [dish_washer1, dish_washer2, dish_washer3, dish_washer4, vacuum_cleaner1, vacuum_cleaner2, vacuum_cleaner3, vacuum_cleaner4, electrical_vehicle1, electrical_vehicle2]
        historicalData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        return cls(name, lat, long, listOfComponets, historicalData)
       

    def currentDemand(self):
        '''returns the current demand of this building'''
        demandSum = self.historicalData[self.hour];
        for component in self.listOfComponets:
            demandSum += component.currentDemand()
        return demandSum

    def update(self, hour):
        '''updates the state of all components in this building with the current time'''
        self.hour = hour % 24
        for component in self.listOfComponets:
            component.update(hour)


if __name__ == "__main__":
    home = BuildingSim.household("home1", 0, 0)
    for hour in range(0, 25):
        home.update(hour)
        print("----------------------------")
        print("Hour: " + str(hour))
        print("Current Demand: " + str(home.currentDemand(hour)))
        for comp in home.listOfComponets:
            print(comp.state, "\t" + comp.name)
        
    