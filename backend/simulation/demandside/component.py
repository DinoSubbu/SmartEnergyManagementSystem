from enum import Enum

from database.models import Component

class ComponentState(Enum):
    NOTSTARTED = 1
    RUNNING = 2
    FINISHED = 3

class ComponentSim():
    '''This class simulates a component for a building'''
    
    def __init__(self, name, est, let, e, lot):
        self.name = name
        # earliest starting time
        self.est = est
        # latest end time
        self.let = let 
        # power
        self.e = e
        # length of operation time
        self.lot = lot
        # hour of the day at which the component was started 
        self.startHour = -1
        self.state = ComponentState.NOTSTARTED


    def start(self, hour):
        '''Starts the componennt'''
        if hour < 0 or hour > 23:
            raise ValueError()
        if hour >= self.est and hour <= self.let:
            self.state = ComponentState.RUNNING
            self.startHour = hour

    def update(self, hour):
        '''Updates the component state.'''
        if hour < 0 or hour > 23:
            raise ValueError()
        if hour == 0:
            # new day --> reset component
            self.state = ComponentState.NOTSTARTED;

        if self.state == ComponentState.RUNNING:
            # check if the component is finished
            if self.startHour + self.lot <= hour:
                self.state = ComponentState.FINISHED
        elif self.state == ComponentState.NOTSTARTED:
            # check if the component has to be stated because it did not run today and now it is the latest start time 
            if hour >= self.let - self.lot:
                self.start(self.let - self.lot)

    def currentDemand(self):
        '''Returns the current demand of the component'''
        if self.state == ComponentState.RUNNING:
            return self.e
        else:
            return 0
    

