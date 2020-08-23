#from gurobipy import *
import xpress as xp
from database.models import Building, Component, Battery
import json

class Optimizer():
     
    def __init__(self, number_of_time_steps=24):
        # Create a new model
        self.model = xp.problem()
        # optimization horizon:
        self.time_steps = range(0, number_of_time_steps)
        self.time_steps_with_tomorrow = range(0, number_of_time_steps+1)
        self.buildings = {}
        self.batteries = {}
        self.generators = {}


    def addBuilding(self, building):
        self.buildings[building.name] = building

    def addBattery(self, battery, startEnergy):
        self.batteries[battery.name] = (battery, startEnergy)

    def addGenerator(self, name, forecast):
        self.generators[name] = forecast

    def addPriceBuy(self, prices):
        self.buy_prices = prices

    def addPriceSell(self, prices):
        self.sell_prices = prices


    def __addVariablesToModel(self):
        '''add variables'''
        
        '''total demand of the micro grid'''
        self.total_demand = {t :xp.var(
            vartype=xp.continuous,
            name='total_demand{}'.format(t)
        )for t in self.time_steps}

        '''total supply of the micro grid'''
        self.total_supply = {t: xp.var(
            vartype=xp.continuous,
            name='total_supply{}'.format(t)
        )for t in self.time_steps}

        '''indicates if we sell energy to the main grid'''
        self.sell = {t: xp.var(
            vartype=xp.binary,
            name='sell_to_main_grid{}'.format(t)
        )for t in self.time_steps}

        '''indicates if we buy energy from the main grid'''
        self.buy = {t :xp.var(
            vartype=xp.binary,
            name='buy_from_main_grid{}'.format(t)
        )for t in self.time_steps}

        self.model.addVariable(self.total_demand,self.total_supply, self.sell, self.buy)

        self.status_comp = {}
        self.st_start_comp = {}
        self.st_end_comp = {}

         # variables for each building
        for name, building in self.buildings.items():

            self.status_comp[name] = { (comp.name, t): xp.var(
                vartype=xp.binary, 
                name= "{}_comp_status{}{}".format(name, comp.name, t))
                for comp in building.components for t in self.time_steps}

            self.st_start_comp[name] = {(comp.name, t) : xp.var(
                vartype=xp.binary, 
                name = "{0}_comp_start_status{1}{2}".format(name, comp.name, t))
                for comp in building.components for t in self.time_steps}

            self.st_end_comp[name] = { (comp.name, t): xp.var(
                vartype=xp.binary, 
                name= "{0}_comp_end_status{1}{2}".format(name, comp.name, t))
                for comp in building.components for t in self.time_steps_with_tomorrow}

        self.model.addVariable(self.status_comp,self.st_start_comp, self.st_end_comp)


        '''charging rate of the battery, zero if not charging'''
        self.charging_rate_bat = { (batteryTuple[0].name,t): xp.var(
            ub = xp.infinity, 
            vartype=xp.continuous, 
            name="battery_charging_rate{0}{1}".format(batteryTuple[0].name,t))
            for batteryTuple in self.batteries.values() for t in self.time_steps}

        '''discharging rate of the battery, zero if not discharging'''
        self.discharging_rate_bat = {(batteryTuple[0].name,t) : xp.var(
            ub = xp.infinity, 
            vartype=xp.continuous, 
            name="battery_discharging_rate{0}{1}".format(batteryTuple[0].name,t))
            for batteryTuple in self.batteries.values() for t in self.time_steps}

        '''current energy level'''
        self.current_energy_bat = { (batteryTuple[0].name,t): xp.var(
            vartype=xp.continuous, 
            name="battery_current_energy{0}{1}".format(batteryTuple[0].name,t))
            for batteryTuple in self.batteries.values() for t in self.time_steps_with_tomorrow}

        '''indicates if the battery is ideling'''
        self.batteryIdle = {(batteryTuple[0].name,t) : xp.var(
            vartype=xp.binary, 
            name="battery_state_idle{0}{1}".format(batteryTuple[0].name,t))
            for batteryTuple in self.batteries.values() for t in self.time_steps}

        '''indicates if the battery is charging'''
        self.batteryCharging = {(batteryTuple[0].name,t) : xp.var(
            vartype=xp.binary, 
            name="battery_state_charging{0}{1}".format(batteryTuple[0].name,t))
            for batteryTuple in self.batteries.values() for t in self.time_steps}

        '''indicates if the battery is discharging'''
        self.batteryDischarging = {(batteryTuple[0].name,t) : xp.var(
            vartype=xp.binary, 
            name="battery_state_discharging{0}{1}".format(batteryTuple[0].name,t))
            for batteryTuple in self.batteries.values() for t in self.time_steps}

        '''The battery gets discharged due to self-discharging all the time. This variable stores the current battery level after self-discharging.'''
        self.selfDischargingValue = {(batteryTuple[0].name,t) : xp.var(
            lb = -xp.infinity,
            vartype=xp.continuous, 
            name="battery_selfdischarging{0}{1}".format(batteryTuple[0].name,t))
            for batteryTuple in self.batteries.values() for t in self.time_steps}

        '''Due to the non-existens of negative energy, this variable stores max(0, selfDischargingValue).'''
        self.selfDischargingValueMax = {(batteryTuple[0].name,t) : xp.var(
            vartype=xp.continuous, 
            name="battery_selfdischarging_max{0}{1}".format(batteryTuple[0].name,t))
            for batteryTuple in self.batteries.values() for t in self.time_steps}

        self.model.addVariable(self.charging_rate_bat, self.discharging_rate_bat, self.current_energy_bat, self.batteryIdle,
            self.batteryCharging, self.batteryDischarging, self.selfDischargingValue, self.selfDischargingValueMax)

    def __createContraints(self):

        '''The total demand is the sum of the single demands of the buildings and charging of the batteries.'''
        self.model.addConstraint(
            (self.total_demand[t] ==  (
            xp.Sum(building.historicalData[t] 
            + xp.Sum(self.status_comp[building.name][comp.name, t]*comp.e for comp in building.components) for building in self.buildings.values())
            + (xp.Sum(self.charging_rate_bat[batteryName, t] for batteryName in self.batteries.keys())))
            for t in self.time_steps)
        )

        '''The total supply is the sum of all generated energy by the generators and discharging of the batteries'''
        self.model.addConstraint([self.total_supply[t] == 
            xp.Sum(forcast[t] for forcast in self.generators.values())
            + (xp.Sum(self.discharging_rate_bat[batteryName,t] for batteryName in self.batteries.keys()))
            for t in self.time_steps])

        '''We can either buy or sell from the main grid'''
        self.model.addConstraint( 
            (self.sell[t] + self.buy[t] == 1 for t in self.time_steps))

        '''If we sell, we must have more supply than demand'''
        self.model.addConstraint(
                ( not(self.sell[t] == 1) or  
                (self.total_supply[t] >= self.total_demand[t]) for t in self.time_steps))
        
        '''If we buy, we must have more demand than supply'''
        self.model.addConstraint(
                (not(self.buy[t] == 1) or
                (self.total_demand[t] >= self.total_supply[t]) for t in self.time_steps))
    
        # building
        for name, building in self.buildings.items():
            for comp in building.components:
                # device start and end
                self.model.addConstraint(
                    (xp.Sum(self.st_start_comp[name][comp.name, t] for t in self.time_steps if t >= comp.est or t <= comp.let - comp.lot) == 1))

                self.model.addConstraint(
                    (xp.Sum(self.st_end_comp[name][comp.name, t] for t in self.time_steps_with_tomorrow if t <= comp.let or t >= comp.est + comp.lot) == 1 ))

                self.model.addConstraint(
                    (self.st_start_comp[name][comp.name, t] == 0 for t in self.time_steps if t < comp.est  or t > comp.let - comp.lot))

                self.model.addConstraint(
                    (self.st_end_comp[name][comp.name, t] == 0 for t in self.time_steps_with_tomorrow if t < comp.est  + comp.lot or t > comp.let))

                self.model.addConstraint(
                    (self.st_end_comp[name][comp.name, t] == self.st_start_comp[name][comp.name, t-comp.lot] for t in self.time_steps_with_tomorrow if t>= comp.lot))

                # device status
                self.model.addConstraint(
                    (xp.Sum(self.status_comp[name][comp.name,t] for t in self.time_steps if t >= comp.est  or t <= comp.let) == comp.lot))

                self.model.addConstraint(
                    (self.status_comp[name][comp.name,t] == 0  for t in self.time_steps if t < comp.est  or t > comp.let))

                self.model.addConstraint(
                    (xp.Sum(self.status_comp[name][comp.name,tau] for tau in range(t)) >= comp.lot*self.st_end_comp[name][comp.name,t] for t in self.time_steps_with_tomorrow))

                self.model.addConstraint(
                    (xp.Sum(self.st_start_comp[name][comp.name,tau] for tau in range(t+1)) >= self.status_comp[name][comp.name,t]  for t in self.time_steps))
    
        for name, batteryTuple in self.batteries.items():
            battery = batteryTuple[0]
            startEnergy = batteryTuple[1]

            '''Sets the value of the battery from the previous day.'''
            self.model.addConstraint(
                (self.current_energy_bat[name, 0] == startEnergy))

            '''This constraint ensures that the charging rate is never higher than the upper bound.'''
            self.model.addConstraint(
                ((self.charging_rate_bat[name, t] <= battery.chargeUpperBound) for t in self.time_steps))

            '''This constraint ensures that the discharging rate is never higher than the upper bound.'''
            self.model.addConstraint(
                ((self.discharging_rate_bat[name, t] <= battery.dischargeUpperBound) for t in self.time_steps))

            '''This constraint ensures that the energy of the battery is never higher than the upper bound.'''
            self.model.addConstraint(
                (self.current_energy_bat[name, t+1] <= battery.energyUpperBound for t in self.time_steps))

            '''This constraint ensures that the energy of the battery never gets negative.'''
            self.model.addConstraint(
                (self.current_energy_bat[name, t] >= 0 for t in self.time_steps))

            '''The battery has to be in exactly one state.'''
            self.model.addConstraint(
                (self.batteryIdle[name, t] + self.batteryCharging[name, t] + self.batteryDischarging[name, t] == 1 for t in self.time_steps))
            
            '''This constraint models one time step in the battery. The battery gets either discharged, charged or it is idling. Regardless of the state, the battery is discharged by self-discharge.'''
            self.model.addConstraint(
                (self.current_energy_bat[name, t+1] == self.selfDischargingValueMax[name, t] + battery.batteryEfficiency * self.charging_rate_bat[name, t] - self.discharging_rate_bat[name, t] / battery.batteryEfficiency
                for t in self.time_steps)
            )

            '''Calculate the energy level after self-discharging.'''
            self.model.addConstraint(
                (self.selfDischargingValue[name, t] == (self.current_energy_bat[name, t] - self.batteryIdle[name, t]*battery.selfDischargingRate) for t in self.time_steps)
            )

            '''This constraint allows an empty and idling battery.'''
            self.model.addConstraint(
                (self.selfDischargingValueMax[name, t] == xp.max(self.selfDischargingValue[name, t], 0) for t in self.time_steps)
            )

            '''Specifies a minimum charging rate.'''
            self.model.addConstraint(
                (not(self.batteryCharging[name, t] == 1) or  
                (self.charging_rate_bat[name, t] >=  max(min(battery.selfDischargingRate/battery.batteryEfficiency, battery.chargeUpperBound), 0.001)) for t in self.time_steps))

            '''Charging rate is zero, if the battery is not in state 'charging'.'''
            self.model.addConstraint(
                (not(self.batteryCharging[name, t] == 0) or  
                (self.charging_rate_bat[name, t] == 0) for t in self.time_steps))

            '''Specifies a minimum discharging rate.'''
            self.model.addConstraint(
                (not(self.batteryDischarging[name, t] == 1) or  
                (self.discharging_rate_bat[name, t] >= max(min(battery.selfDischargingRate*battery.batteryEfficiency, battery.dischargeUpperBound), 0.001)) for t in self.time_steps))

            '''Discharging rate is zero, if the battery is not in state 'discharging'.'''
            self.model.addConstraint(
                (not(self.batteryDischarging[name, t] == 0) or  
                (self.discharging_rate_bat[name, t] == 0) for t in self.time_steps))
            


    def set_time_limit(self, time_limit):
        '''
        Set a time limit for the optimization.
        To use no time limit, set it to double xp.infinity.
        If no time limit is set, the optimization time is unbounded
        '''
        self.timelimit = time_limit

    def set_mip_gap(self, gap):
        '''
        Set the mip gap for the optimization.
        The default value is 10^(-4), which are 0.01%.
        '''
        self.model.Params.mipgap = gap

    def multiply_mip_gap(self, factor):
        '''
        Multiply the current mip gap by the given factor.
        '''
        self.model.Params.mipgap *= factor

    def optimize(self, goal='cost'):
        '''
        Optimizes the micro grid with the given objective goal
        Raise a TimoutError, if the time limit is reached
        '''
        self.__addVariablesToModel()
        self.__createContraints() 
        if goal == 'cost':
            self.model.setObjective( 
                (xp.Sum(self.buy[t]*(self.total_demand[t]- self.total_supply[t])  for t in self.time_steps)),
                #(xp.Sum(
                #((self.total_supply[t] - self.total_demand[t])*self.sell[t]*self.sell_prices[t])
                # + ((self.total_supply[t]- self.total_demand[t])*self.buy[t]*self.buy_prices[t])
                 #for t in self.time_steps))/10**6 , 

                 sense=xp.maximize)
        elif goal == 'independent':
            obj_independent = (xp.Sum(self.buy[t]*(1- self.total_demand[t]- self.total_supply[t]) + self.sell[t]*(self.total_supply[t] - self.total_demand[t])  for t in self.time_steps))
            self.model.setObjective(obj_independent, sense=xp.minimize)
        elif goal == 'xp.minbuy':
            obj_independent = (xp.Sum(self.buy[t]*(self.total_demand[t]- self.total_supply[t])  for t in self.time_steps))
            self.model.setObjective(obj_independent, sense=xp.minimize)
        else:
            raise ValueError('Unkown objective goal')
        self.model.solve()
        print("Status: ", self.model.getProbStatusString())
        print("Solution: ", self.model.getSolution())
        if self.model.getProbStatus() == GRB.TIME_LIMIT:
            raise TimeoutError()

    def getSchedule(self, precision = 5):
        '''
        Returns the schedule as a dict.
        Round all values to given precision.
        '''
        if self.model.status == GRB.OPTIMAL:
            exchange_with_main_grid = ["error" for t in self.time_steps]
            for t in self.time_steps:
                exchange_with_main_grid[t] = round(self.total_demand[t].X - self.total_supply[t].X, precision)
            schedule = {'buildings':{}, 'batteries':{}, 'exchange_with_main_grid':exchange_with_main_grid}
            for name, building in self.buildings.items():
                schedule['buildings'][name] = {}
                for comp in building.components:
                    schedule['buildings'][name][comp.name] = {}
                    for t in self.time_steps:
                        if self.st_start_comp[name][comp.name, t].X >= 0.5:
                            schedule['buildings'][name][comp.name]['start'] = t
                    for t in self.time_steps_with_tomorrow:
                        if self.st_end_comp[name][comp.name, t].X >= 0.5:
                            schedule['buildings'][name][comp.name]['end'] = t
            for batteryName in self.batteries.keys():
                state = ["error" for t in self.time_steps]
                rate = ["error" for t in self.time_steps]
                energy = ["error" for t in self.time_steps_with_tomorrow]
                for t in self.time_steps_with_tomorrow:
                    energy[t] = max(0, round(self.current_energy_bat[batteryName, t].X, precision))
                for t in self.time_steps:
                    if self.batteryIdle[batteryName, t].X >= 0.5:
                        state[t] = 'idle'
                        rate[t] = 0
                    if self.batteryCharging[batteryName, t].X >= 0.5:
                        state[t] = 'charging'
                        rate[t] = round(self.charging_rate_bat[batteryName, t].X, precision)
                    if self.batteryDischarging[batteryName, t].X >= 0.5:
                        state[t] = 'discharging'
                        rate[t] = round(-self.discharging_rate_bat[batteryName, t].X, precision)
                schedule['batteries'][batteryName] = {'state':state, 'rate':rate, 'energy':energy}
            return schedule
        else:
            print("not optimal")

    def getObjFuncValue(self):
        if self.model.status == GRB.OPTIMAL:
            return self.model.objVal
        else:
            print("not optimal")


    
if __name__ == "__main__":
    washing_machine = Component("washing_machine", 9, 17, 2, 2)
    dish_washer = Component("dish_washer", 9, 12, 1.8, 2)
    spin_dryer = Component("spin_dryer", 13, 18, 2.5, 1)
    electrical_vehicle = Component("electrical_vehicle", 18, 24, 3.5, 3)
    vacuum_cleaner = Component("vacuum_cleaner", 9, 17, 1.2, 1)
    listOfComponets = [washing_machine, dish_washer, spin_dryer, electrical_vehicle, vacuum_cleaner]
    historicalData = [0.2,0.2,0.2,0.2,0.2,0.6,0.6,0.6,1,1,1,0.5,0.5,0.5,0.4,0.4,0.4,0.8,0.8,0.6,0.6,0.4,0.2,0.2]
    building = Building("test_building", "0", "1", historicalData)
    building.components = listOfComponets
    building_2 = Building("test_building_2", "0", "1", historicalData)
    building_2.components = listOfComponets
    battery = Battery("test_battery", "0", "1", 0.95, 3, 2, 5, 0.1)
    battery2 = Battery("test_battery_2", "0", "1", 0.95, 3, 2, 15, 0.1)
    opt = Optimizer()
    opt.addBuilding(building)
    opt.addBuilding(building_2)
    opt.addBattery(battery, 0)
    opt.addBattery(battery2, 0)
    opt.addGenerator('solar_1', [0,0,0,0,2,4,8,10,13,14,16,12,12,13,11,9,6,8,8,0,0,0,0,0])
    opt.addPriceBuy([18,18,18,18,18,18,35,35,35,35,25,25,25,25,25,25,25,25,35,35,35,35,18,18])
    opt.addPriceSell([18,18,18,18,18,18,35,35,35,35,25,25,25,25,25,25,25,25,35,35,35,35,18,18])
    opt.set_time_limit(60)
    while True:
        try:
            opt.optimize('xp.minbuy')
            break
        except TimeoutError:
            opt.multiply_mip_gap(3)

    msgdict = {GRB.OPTIMAL : 'Optimal', GRB.INFEASIBLE : 'Infeasible model'}
    msg = msgdict[opt.model.status]
    if msg == 'Infeasible model':
        print('The model is infeasible; computing IIS')
        opt.model.computeIIS()
        print('\nThe following constraint(s) cannot be satisfied:')
        for c in opt.model.getConstrs():
            if c.IISConstr:
                print('%s' % c.constrName)
    else:
        # for v in opt.model.getVars():
        #     if v.X != 0:    
        #         print("%s %f" % (v.Varname, v.X))
        # print('\n')
        schedule = opt.getSchedule()
        print(json.dumps(schedule))


   
