from simulation.demandside.component import ComponentSim
from simulation.location_entity import LocationEntity
from database.models import Building

class BuildingSim(LocationEntity):

    def __init__(self, name, lat, long, listOfComponents, historicalData):
        LocationEntity.__init__(self, name, lat, long)
        self.listOfComponets = listOfComponents
        self.historicalData = historicalData
        self.schedule = None
    
    @classmethod
    def createFromModel(cls, building):
        listOfComponets = []
        for comp in building.components:
            listOfComponets.append(ComponentSim(comp.name, comp.est, comp.let, comp.e, comp.lot))
        return cls(building.name, building.lat, building.long, listOfComponets, building.historicalData)
    
       
    def getDemand(self, hour):
        '''returns the current demand of this building'''
        demandSum = self.historicalData[hour];
        for component in self.listOfComponets:
            if hour >= self.schedule[component.name]['start'] and hour < self.schedule[component.name]['end']:
                demandSum += component.e
        return demandSum

    def getComponentState(self, hour):
        componentState = {}
        for component in self.listOfComponets:
            if hour < self.schedule[component.name]['start']:
                componentState[component.name] = 'not_started'
            elif hour < self.schedule[component.name]['end']:
                componentState[component.name] = 'running'
            else:
                componentState[component.name] = 'finished'
        return componentState

    def setSchedule(self, schedule):
        self.schedule = schedule


if __name__ == "__main__":
    home = BuildingSim.household("home1", 0, 0)
    for hour in range(0, 25):
        home.update(hour)
        print("----------------------------")
        print("Hour: " + str(hour))
        print("Current Demand: " + str(home.currentDemand(hour)))
        for comp in home.listOfComponets:
            print(comp.state, "\t" + comp.name)
        
    