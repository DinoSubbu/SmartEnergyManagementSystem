from gurobipy import *
import docplex.mp.model as cpx
import pulp as plp
import cplex
from database.models import Building, Component, Battery
import json

# https://medium.com/opex-analytics/optimization-modeling-in-python-pulp-gurobi-and-cplex-83a62129807a
# http://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html

class Optimizer():
     
    def __init__(self, number_of_time_steps=24):
        # Create a new model
        self.model = plp.LpProblem("model")
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
        self.total_demand = {time_step : plp.LpVariable(
            cat=plp.LpContinuous,
            #self.time_steps,
            lowBound=0,
            name="total_demand_{0}".format(time_step)
        )for time_step in self.time_steps}

        '''total supply of the micro grid'''
        self.total_supply = {time_step: plp.LpVariable(
            #self.time_steps,
            cat=plp.LpContinuous,
            lowBound=0,
            name="total_supply_{0}".format(time_step)
        )for time_step in self.time_steps}

        '''indicates if we sell energy to the main grid'''
        self.sell = {time_step: plp.LpVariable(
            #self.time_steps,
            cat=plp.LpBinary,
            lowBound=0,
            name="sell_to_main_grid_{0}".format(time_step)
        )for time_step in self.time_steps}

        '''indicates if we buy energy from the main grid'''
        self.buy = {time_step: plp.LpVariable(
            #self.time_steps,
            cat=plp.LpBinary,
            lowBound=0,
            name="buy_from_main_grid_{0}".format(time_step)
        )for time_step in self.time_steps}

        self.status_comp = {}
        self.st_start_comp = {}
        self.st_end_comp = {}

         # variables for each building
        for name, building in self.buildings.items():

            self.status_comp[name] = {(comp.name,time_step) : plp.LpVariable(
                #[comp.name for comp in building.components], 
                #self.time_steps,
                cat=plp.LpBinary,
                lowBound=0,
                name= "{0}_comp_status_{1}_{2}".format(name,comp.name,time_step))
                for comp in building.components for time_step in self.time_steps}

            self.st_start_comp[name] = {(comp.name,time_step) : plp.LpVariable(
                #[comp.name for comp in building.components], 
                #self.time_steps, 
                cat=plp.LpBinary,
                lowBound=0,
                name= "{0}_comp_start_status_{1}_{2}".format(name,comp.name, time_step))
                for comp in building.components for time_step in self.time_steps}

            self.st_end_comp[name] = {(comp.name,time_step) : plp.LpVariable(
                #[comp.name for comp in building.components], 
                #self.time_steps_with_tomorrow, 
                cat=plp.LpBinary,
                lowBound=0,
                name= "{0}_comp_end_status_{1}_{2}".format(name,comp.name, time_step))
                for comp in building.components for time_step in self.time_steps_with_tomorrow}

        '''charging rate of the battery, zero if not charging'''
        self.charging_rate_bat = {(batteryTuple[0].name,time_step): plp.LpVariable(
            #[batteryTuple[0].name for batteryTuple in self.batteries.values()], 
            #self.time_steps, 
            cat=plp.LpContinuous,
            lowBound=0,
            name="battery_charging_rate_{0}_{1}".format(batteryTuple[0].name, time_step))
            for batteryTuple in self.batteries.values() for time_step in self.time_steps}

        '''discharging rate of the battery, zero if not discharging'''
        self.discharging_rate_bat = {(batteryTuple[0].name,time_step) : plp.LpVariable(
            #[batteryTuple[0].name for batteryTuple in self.batteries.values()], 
            #self.time_steps, 
            cat=plp.LpContinuous,
            lowBound=0,
            name="battery_discharging_rate_{0}_{1}".format(batteryTuple[0].name, time_step))
            for batteryTuple in self.batteries.values() for time_step in self.time_steps}

        '''current energy level'''
        self.current_energy_bat = {(batteryTuple[0].name,time_step) : plp.LpVariable(
            #[batteryTuple[0].name for batteryTuple in self.batteries.values()], 
            #self.time_steps_with_tomorrow, 
            cat=plp.LpContinuous,
            lowBound=0,
            name="battery_current_energy_{0}_{1}".format(batteryTuple[0].name,time_step))
            for batteryTuple in self.batteries.values() for time_step in self.time_steps_with_tomorrow}

        '''indicates if the battery is ideling'''
        self.batteryIdle = {(batteryTuple[0].name,time_step) : plp.LpVariable(
            #[batteryTuple[0].name for batteryTuple in self.batteries.values()], 
            #self.time_steps, 
            cat=plp.LpBinary,
            lowBound=0,
            name="battery_state_idle_{0}_{1}".format(batteryTuple[0].name,time_step))
            for batteryTuple in self.batteries.values() for time_step in self.time_steps}

        '''indicates if the battery is charging'''
        self.batteryCharging = {(batteryTuple[0].name,time_step) : plp.LpVariable(
            #[batteryTuple[0].name for batteryTuple in self.batteries.values()], 
            #self.time_steps, 
            cat=plp.LpBinary,
            lowBound=0,
            name="battery_state_charging_{0}_{1}".format(batteryTuple[0].name,time_step))
            for batteryTuple in self.batteries.values() for time_step in self.time_steps}

        '''indicates if the battery is discharging'''
        self.batteryDischarging = {(batteryTuple[0].name,time_step) : plp.LpVariable(
            #[batteryTuple[0].name for batteryTuple in self.batteries.values()], 
            #self.time_steps, 
            cat=plp.LpBinary,
            lowBound=0,
            name="battery_state_discharging_{0}_{1}".format(batteryTuple[0].name, time_step))
            for batteryTuple in self.batteries.values() for time_step in self.time_steps}

        '''The battery gets discharged due to self-discharging all the time. This variable stores the current battery level after self-discharging.'''
        self.selfDischargingValue = {(batteryTuple[0].name,time_step) : plp.LpVariable(
            #[batteryTuple[0].name for batteryTuple in self.batteries.values()], 
            #self.time_steps, 
            cat=plp.LpContinuous,
            #lowBound = -cplex.infinity,
            name="battery_selfdischarging_{0}_{1}".format(batteryTuple[0].name, time_step))
            for batteryTuple in self.batteries.values() for time_step in self.time_steps}

        '''Due to the non-existens of negative energy, this variable stores max(0, selfDischargingValue).'''
        self.selfDischargingValueMax = {(batteryTuple[0].name,time_step) : plp.LpVariable(
            #[batteryTuple[0].name for batteryTuple in self.batteries.values()], 
            #self.time_steps, 
            lowBound=0,
            cat=plp.LpContinuous,
            name="battery_selfdischarging_max_{0}_{1}".format(batteryTuple[0].name, time_step))
            for batteryTuple in self.batteries.values() for time_step in self.time_steps}


    def __createContraints(self):

        '''The total demand is the sum of the single demands of the buildings and charging of the batteries.'''
        {t : self.model.addConstraint(
            plp.LpConstraint (
                rhs = self.total_demand[t],
                e = plp.lpSum(building.historicalData[t]  + plp.lpSum(self.status_comp[building.name][comp.name, t]*comp.e for comp in building.components) for building in self.buildings.values())
                      + (plp.lpSum(self.charging_rate_bat[batteryName, t] for batteryName in self.batteries.keys())),
                sense = plp.LpConstraintEQ,
                name = 'total_demand_{0}'.format(t)
            ))for t in self.time_steps}

        '''The total supply is the sum of all generated energy by the generators and discharging of the batteries'''
        {t : self.model.addConstraint(
            plp.LpConstraint (
                rhs = self.total_supply[t],
                e = plp.lpSum(forcast[t] for forcast in self.generators.values())
                + (plp.lpSum(self.discharging_rate_bat[batteryName, t] for batteryName in self.batteries.keys())),
                sense = plp.LpConstraintEQ,
                name = 'total_supply_{0}'.format(t)
            ))for t in self.time_steps}

        '''We can either buy or sell from the main grid'''
        {t : self.model.addConstraint(
            plp.LpConstraint (
                e = self.sell[t] + self.buy[t],
                rhs = 1,
                sense = plp.LpConstraintEQ,
                name ='exactlyOneState_{0}'.format(t)
                ))
            for t in self.time_steps}

        # p => q is the same as not(p) or q
        '''If we sell, we must have more supply than demand'''
        {t : self.model.addConstraint(
                plp.LpConstraint (
                    e = ( not(self.sell[t] == 1) or  
                (self.total_supply[t] >= self.total_demand[t]) ),
                name = 'sellIfSurplus_{0}'.format(t)
                ))
                for t in self.time_steps}
        
        '''If we buy, we must have more demand than supply'''
        {t : self.model.addConstraint(
                plp.LpConstraint (  not(self.buy[t] == 1) or
                (self.total_demand[t] >= self.total_supply[t]) ),
                name='buyIfdemand_{0}'.format(t))
                for t in self.time_steps}


        # building
        for name, building in self.buildings.items():
            for comp in building.components:
                # device start and end
                self.model.addConstraint(
                    plp.LpConstraint (
                        e= (plp.lpSum(self.st_start_comp[name][comp.name, t] for t in self.time_steps if t >= comp.est or t <= comp.let - comp.lot)),
                        rhs = 1, 
                        sense = plp.LpConstraintEQ,
                        name='singlestart_{0}_{1}'.format(name,comp.name)))


                self.model.addConstraint(
                    plp.LpConstraint (plp.lpSum(self.st_end_comp[name][comp.name, t] for t in self.time_steps_with_tomorrow if t <= comp.let or t >= comp.est + comp.lot) == 1 , 
                    name='singleend_{0}_{1}'.format(name,comp.name)))


                {t :self.model.addConstraint(
                    plp.LpConstraint (
                        e = self.st_start_comp[name][comp.name, t],
                        rhs = 0,
                        sense = plp.LpConstraintEQ,
                        name ="startzero_{0}_{1}_{2}".format(name,comp.name,t)
                        ))
                    for t in self.time_steps 
                    if t < comp.est  or t > (comp.let - comp.lot)
                    }

                {t :self.model.addConstraint(
                    plp.LpConstraint (self.st_end_comp[name][comp.name, t] == 0,
                    name="endzero_{0}_{1}_{2}".format(name,comp.name,t)))
                    for t in self.time_steps_with_tomorrow if ((t < comp.est  + comp.lot) or (t > comp.let)) }

                {t :self.model.addConstraint(
                    plp.LpConstraint (self.st_end_comp[name][comp.name, t] == self.st_start_comp[name][comp.name, t-comp.lot],
                    name="startend_{0}_{1}_{2}".format(name,comp.name,t)))
                    for t in self.time_steps_with_tomorrow if t>= comp.lot}

                # device status
                self.model.addConstraint(
                    plp.LpConstraint (plp.lpSum(self.status_comp[name][comp.name,t] 
                        for t in self.time_steps if t >= comp.est  or t <= comp.let) == comp.lot,
                    name="duration{0}_{1}".format(name,comp.name)))

                {t :self.model.addConstraint(
                    plp.LpConstraint (self.status_comp[name][comp.name,t] == 0,
                    name="statuszero_{0}_{1}_{2}".format(name,comp.name,t)))
                    for t in self.time_steps if t < comp.est  or t > comp.let}

                {(t,tau) : self.model.addConstraint(
                    plp.LpConstraint (plp.lpSum(self.status_comp[name][comp.name,tau]) >= comp.lot*self.st_end_comp[name][comp.name,t] ),
                    name='endafterLOT_{0}_{1}_{2}_{3}'.format(name,comp.name,t,tau))
                    for t in self.time_steps_with_tomorrow for tau in range(t)}

                {(t,tau) : self.model.addConstraint(
                    plp.LpConstraint (plp.lpSum(self.st_start_comp[name][comp.name,tau]) >= self.status_comp[name][comp.name,t]),
                    name='statusafterstart_{0}_{1}_{2}_{3}'.format(name,comp.name,t,tau))
                    for t in self.time_steps for tau in range(t+1)}

        for name, batteryTuple in self.batteries.items():
            battery = batteryTuple[0]
            startEnergy = batteryTuple[1]

            '''Sets the value of the battery from the previous day.'''
            self.model.addConstraint(
                plp.LpConstraint (self.current_energy_bat[name, 0] == startEnergy,
                name='startEnergy_{0}'.format(name)))

            '''This constraint ensures that the charging rate is never higher than the upper bound.'''
            {t : self.model.addConstraint(
                plp.LpConstraint ((self.charging_rate_bat[name, t] <= battery.chargeUpperBound),
                name='chargingUpperBound_{0}_{1}'.format(name,t)))
                for t in self.time_steps}

            '''This constraint ensures that the discharging rate is never higher than the upper bound.'''
            {t : self.model.addConstraint(
                plp.LpConstraint ((self.discharging_rate_bat[name, t] <= battery.dischargeUpperBound),
                name='dischargingUpperBound_{0}_{1}'.format(name,t)))
                for t in self.time_steps}

            '''This constraint ensures that the energy of the battery is never higher than the upper bound.'''
            {t : self.model.addConstraint(
                plp.LpConstraint (self.current_energy_bat[name, t+1] <= battery.energyUpperBound,
                name='energyUpperBound_{0}_{1}'.format(name,t)))
                for t in self.time_steps}

            '''This constraint ensures that the energy of the battery never gets negative.'''
            {t : self.model.addConstraint(
                plp.LpConstraint (self.current_energy_bat[name, t] >= 0,
                name='noNegativeEnergy_{0}_{1}'.format(name,t)))
                for t in self.time_steps}

            '''The battery has to be in exactly one state.'''
            {t : self.model.addConstraint(
                plp.LpConstraint (self.batteryIdle[name, t] + self.batteryCharging[name, t] + self.batteryDischarging[name, t] == 1,
                name='exactlyOneState_{0}_{1}'.format(name,t)))
                for t in self.time_steps}
            
            '''This constraint models one time step in the battery. The battery gets either discharged, charged or it is idling. Regardless of the state, the battery is discharged by self-discharge.'''
            batteryEfficiencyInverse = 1 / battery.batteryEfficiency
            {t : self.model.addConstraint(
                plp.LpConstraint (self.current_energy_bat[name, t+1] == self.selfDischargingValueMax[name, t] + battery.batteryEfficiency * self.charging_rate_bat[name, t] - (self.discharging_rate_bat[name, t] * batteryEfficiencyInverse)
                ,
                name='chargingTransition_{0}_{1}'.format(name,t))
            ) for t in self.time_steps}

            '''Calculate the energy level after self-discharging.'''
            {t : self.model.addConstraint(
                plp.LpConstraint (self.selfDischargingValue[name, t] == (self.current_energy_bat[name, t] - self.batteryIdle[name, t]*battery.selfDischargingRate),
                name='selfdischargingValue_{0}_{1}'.format(name,t))
            )  for t in self.time_steps}

            '''This constraint allows an empty and idling battery.'''
            {t : self.model.addConstraint(
                plp.LpConstraint (self.selfDischargingValueMax[name, t] == self.selfDischargingValue[name, t] and self.selfDischargingValueMax[name, t] >= 0,
                name='selfdischargingValueMax_{0}_{1}'.format(name,t))
            ) for t in self.time_steps}

            minValueChargeBound = min (battery.selfDischargingRate * batteryEfficiencyInverse , battery.chargeUpperBound)
            '''Specifies a minimum charging rate.'''
            {t : self.model.addConstraint(
                plp.LpConstraint ( not(self.batteryCharging[name, t] == 1) or
                (self.charging_rate_bat[name, t] >= minValueChargeBound
                    and self.charging_rate_bat[name, t] >= 0.001),
                #self.model.max(self.model.min(battery.selfDischargingRate/battery.batteryEfficiency, battery.chargeUpperBound), 0.001)),
                name='chargingNotEqualsZero_{0}_{1}'.format(name,t)))
                for t in self.time_steps}

            '''Charging rate is zero, if the battery is not in state 'charging'.'''
            {t : self.model.addConstraint(
                plp.LpConstraint ( not(self.batteryCharging[name, t] == 0) or
                (self.charging_rate_bat[name, t] == 0) ,
                name='chargingEqualsZero_{0}_{1}'.format(name,t)))
                for t in self.time_steps}

            minValueDischargeBound = min (battery.selfDischargingRate * battery.batteryEfficiency , battery.dischargeUpperBound)
            '''Specifies a minimum discharging rate.'''
            {t : self.model.addConstraint(
                plp.LpConstraint ( not(self.batteryDischarging[name, t] == 1) or 
                (self.discharging_rate_bat[name, t] >= minValueDischargeBound and  self.discharging_rate_bat[name, t] >= 0.001 ), 
                #(self.discharging_rate_bat[name, t] >= self.model.max(self.model.min(battery.selfDischargingRate*battery.batteryEfficiency, battery.dischargeUpperBound), 0.001)),
                name='dischargingNotEqualsZero_{0}_{1}'.format(name,t)))
                for t in self.time_steps }

            '''Discharging rate is zero, if the battery is not in state 'discharging'.'''
            {t : self.model.addConstraint(
                plp.LpConstraint ( not(self.batteryDischarging[name, t] == 0) or 
                (self.discharging_rate_bat[name, t] == 0),
                name='dischargingEqualsZero_{0}_{1}'.format(name,t)))
                for t in self.time_steps } 
            


    def set_time_limit(self, time_limit):
        '''
        Set a time limit for the optimization.
        To use no time limit, set it to double infinity.
        If no time limit is set, the optimization time is unbounded
        '''
        #self.model.parameters.timelimit = time_limit
        self.time_limit = time_limit

    def set_mip_gap(self, gap):
        '''
        Set the mip gap for the optimization.
        The default value is 10^(-4), which are 0.01%.
        '''
        self.model.parameters.mip.tolerances.mipgap = gap

    def multiply_mip_gap(self, factor):
        '''
        Multiply the current mip gap by the given factor.
        '''
        self.model.parameters.mip.tolerances.mipgap *= factor

    def optimize(self, goal='cost'):
        '''
        Optimizes the micro grid with the given objective goal
        Raise a TimoutError, if the time limit is reached
        '''
        self.__addVariablesToModel()
        self.__createContraints() 
        if goal == 'cost':
            obj_cost = (plp.lpSum(-self.buy[t]*self.buy_prices[t]*(self.total_demand[t]- self.total_supply[t]) + self.sell[t]*self.sell_prices[t]*(self.total_supply[t] - self.total_demand[t])  for t in self.time_steps))/10**6
            self.model.sense = plp.LpMaximize
            self.model.setObjective(obj_cost)
        elif goal == 'independent':
            obj_independent = (plp.lpSum(self.buy[t]*(self.total_demand[t]- self.total_supply[t]) + self.sell[t]*(self.total_supply[t] - self.total_demand[t])  for t in self.time_steps))
            self.model.sense = plp.LpMinimize
            self.model.setObjective(obj_independent)
        elif goal == 'min_buy':
            obj_independent = (plp.lpSum(self.buy[t]*(self.total_demand[t]- self.total_supply[t])  for t in self.time_steps))
            self.model.sense = plp.LpMinimize
            self.model.setObjective(obj_independent)
        else:
            raise ValueError('Unkown objective goal')
        self.model.solve(maxSeconds=self.time_limit)
        if plp.LpStatus[self.model.status] == 'Undefined':
            raise TimeoutError()

    def getSchedule(self, precision = 5):
        '''
        Returns the schedule as a dict.
        Round all values to given precision.
        '''
        if plp.LpStatus[self.model.status] == 'Optimal':
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
        if plp.LpStatus[self.model.status] == 'Optimal':
            return self.model.objective.value()
            #return self.model.objVal
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
            opt.optimize('min_buy')
            break
        except TimeoutError:
            opt.multiply_mip_gap(3)

    #msgdiplp.LpConstraint {GRB.OPTIMAL : 'Optimal', GRB.INFEASIBLE : 'Infeasible model'}
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


   
