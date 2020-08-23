from gurobipy import *


class Optimizer:
    def __init__(self, grid_p_min, grid_p_max):
        """ inits the optimizer class """

        # general variables
        self.grid = {'p_min': grid_p_min, 'p_max': grid_p_max}
        self.time_steps = range(0, 24)

        # plants variables
        self.plants = []
        self.plants_char = {}
        self.price = {}

        # user variables
        self.users = []
        self.tarifs = {}
        self.UD = {}

        # device variables
        self.devices = []
        self.CED = {}

        # model variables
        self.model = Model('Optimal Scheduling')
        self.status = []
        self.st_start = []
        self.st_end = []

    def addPlant(self, name, p_min, p_max, price):
        """
        adds a generator with the given name, p_min, p_max and price
        @param p_max is an array for 24 timeslots

        """
        self.plants.append(name)
        self.plants_char[name] = {'p_min': p_min, 'p_max': p_max}
        self.price[name] = price

    def addUser(self, name, tarif, uncontrollableLoad):
        """
        adds a user with the given name, tarif and uncontrollableLoad
        @param tarif is an array for 24 timeslots

        """
        self.users.append(name)
        self.tarifs[name] = tarif
        self.UD[name] = uncontrollableLoad

    def addDevice(self, name, EST, LET, E, LOT):
        """
        adds a device with the given name and schedule profile

        """
        self.devices.append(name)
        self.CED[name] = {'EST': EST, 'LET': LET, 'E': E, 'LOT': LOT}

    def __addVariablesToModel(self):
        '''add variables'''
        self.p_gen = self.model.addVars(self.plants, self.time_steps, lb=0, vtype=GRB.CONTINUOUS, name="pow_gen")  # generated power from plants       
        self.p_grid = self.model.addVars(self.time_steps, lb = -GRB.INFINITY, vtype=GRB.CONTINUOUS, name="exch_pow") # power exchanged with the main grid >0 if import <0 if export

        self.tot_d = self.model.addVars(self.users, self.time_steps, lb = 0, vtype=GRB.CONTINUOUS, name="total_demand") # total demand

        self.status = []
        self.st_start = []
        self.st_end = []
        for index, user in enumerate(self.users):
            self.status.append(self.model.addVars(self.devices, self.time_steps, vtype=GRB.BINARY, name="Dev_status_user" + str(index))) # status of devices of each user
            self.st_start.append(self.model.addVars(self.devices, self.time_steps, vtype=GRB.BINARY, name="start_status_user"  + str(index)))
            self.st_end.append(self.model.addVars(self.devices, self.time_steps, vtype=GRB.BINARY, name="end_status_user"  + str(index)))

    
    def __createConstrainsts(self):
        '''add constraints'''
        # balance
        self.model.addConstrs((quicksum(self.p_gen[pp,t] for pp in self.plants) - quicksum(self.tot_d[u,t] for u in self.users) + self.p_grid[t] == 0 for t in self.time_steps),name='balance')

        # generation limit
        for index, plant in enumerate(self.plants):
            self.model.addConstrs((self.p_gen[plant,t] >= self.plants_char[plant]['p_min'][t] for t in self.time_steps), name='P1limitmin_plant' + str(index))
            # TODO check if this is okay; in the example the plant2 has to fit exactly the p_max value of the timestep for some reason, see next line
            #  model.addConstrs((p_gen['Plant2',t] == plants_char['Plant2']['p_max'][t] for t in time_steps), name='P2output')
            #  could also make sense if p_min is not a list and not equal to p_max in the example of solar panel
            self.model.addConstrs((self.p_gen[plant,t] <= self.plants_char[plant]['p_max'][t] for t in self.time_steps), name='P1limitmax_plant' + str(index))

        # grid exchange
        self.model.addConstrs((self.p_grid[t] >= self.grid['p_min'] for t in self.time_steps), name='gridmin')
        self.model.addConstrs((self.p_grid[t] <= self.grid['p_max'] for t in self.time_steps), name='gridmax')
        
        # demand side for each user
        for index, user in enumerate(self.users):
            # total demand
            self.model.addConstrs((self.tot_d[user,t] == self.UD[user][t] + quicksum(self.CED[d]['E']*self.status[index][d,t] for d in self.devices) for t in self.time_steps), name='U' + str(index) + 'totd')

            # device start and end
            self.model.addConstrs((quicksum(self.st_start[index][d,t] for t in self.time_steps if t >= self.CED[d]['EST'] or t <= self.CED[d]['LET']-self.CED[d]['LOT']) == 1 for d in self.devices), name='U' + str(index) + 'singlestart')
            self.model.addConstrs((quicksum(self.st_end[index][d,t] for t in self.time_steps if t <= self.CED[d]['LET'] or t >= self.CED[d]['EST']+self.CED[d]['LOT']) == 1 for d in self.devices), name='U' + str(index) + 'singleend')
            self.model.addConstrs((self.st_start[index][d,t] ==0 for d in self.devices for t in self.time_steps if t < self.CED[d]['EST'] or t > self.CED[d]['LET'] - self.CED[d]['LOT']), name='U' + str(index) + 'startzero')
            self.model.addConstrs((self.st_end[index][d,t] ==0 for d in self.devices for t in self.time_steps if t < self.CED[d]['EST'] + self.CED[d]['LOT'] or t > self.CED[d]['LET']), name='U' + str(index) + 'endzero')
            self.model.addConstrs((self.st_end[index][d,t] == self.st_start[index][d,t-self.CED[d]['LOT']] for d in self.devices for t in self.time_steps if t>= self.CED[d]['LOT']), name='U' + str(index) + 'startend')

            # device status
            self.model.addConstrs((quicksum(self.status[index][d,t] for t in self.time_steps if t >= self.CED[d]['EST'] or t <= self.CED[d]['LET']) == self.CED[d]['LOT'] for d in self.devices), name='U' + str(index) + 'duration')
            self.model.addConstrs((self.status[index][d,t] ==0 for d in self.devices for t in self.time_steps if t < self.CED[d]['EST'] or t > self.CED[d]['LET']), name='U' + str(index) + 'statuszero')
            self.model.addConstrs((quicksum(self.status[index][d,tau] for tau in range(t)) >= self.CED[d]['LOT']*self.st_end[index][d,t] for d in self.devices for t in self.time_steps), name='U' + str(index) + 'endafterLOT')
            self.model.addConstrs((quicksum(self.st_start[index][d,tau] for tau in range(t+1)) >= self.status[index][d,t] for d in self.devices for t in self.time_steps), name='U' + str(index) + 'statusafterstart')

    def __optimize(self):
        self.__addVariablesToModel()
        self.__createConstrainsts()

        # objective function
        obj = (quicksum(self.tarifs[u][t]*self.tot_d[u,t]*1/100 for u in self.users for t in self.time_steps) - quicksum(self.price[pp]*self.p_gen[pp,t]*1/100 for pp in self.plants for t in self.time_steps))

        self.model.setObjective(obj, GRB.MAXIMIZE)

        self.model.optimize()

    def getOptimizedResults(self):
        self.__optimize()

        msgdict = {GRB.OPTIMAL : 'Optimal', GRB.INFEASIBLE : 'Infeasible model'}
        msg = msgdict[self.model.status]
        if msg == 'Infeasible model':
            print('The model is infeasible; computing IIS')
            self.model.computeIIS()
            print('\nThe following constraint(s) cannot be satisfied:')
            for c in self.model.getConstrs():
                if c.IISConstr:
                    print('%s' % c.constrName)

        for v in self.model.getVars():
            if v.X != 0:
                print("%s %f" % (v.Varname, v.X))
        print('\n')



if __name__ == "__main__":
    # values from the example adjusted to the optimizer class
    optimizer = Optimizer(-70, 70)
    # devices
    optimizer.addDevice("WM", 9, 17, 2, 2)
    optimizer.addDevice("DW", 9, 17, 2, 2)
    # plants
    optimizer.addPlant("Plant0", [10 for _ in range(24)], [70 for _ in range(24)], 10)
    pv_out = [0,0,0,0,2,4,8,10,13,14,16,12,12,13,11,9,6,8,8,0,0,0,0,0]
    optimizer.addPlant("Plant1", pv_out, pv_out, 0)
    # users
    tarif_user0 = [20,20,20,20,20,20,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,20,20]
    uncontrollableLoad_user0 = [0.2,0.2,0.2,0.2,0.2,0.6,0.6,0.6,1,1,1,0.5,0.5,0.5,0.4,0.4,0.4,0.8,0.8,0.6,0.6,0.4,0.2,0.2]
    optimizer.addUser("User0", tarif_user0, uncontrollableLoad_user0)
    tarif_user1 = [18,18,18,18,18,18,35,35,35,35,25,25,25,25,25,25,25,25,35,35,35,35,18,18]
    uncontrollableLoad_user1 = [0.2,0.2,0.2,0.2,0.2,1,1,1,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.6,0.6,0.6,0.6,0.4,0.2,0.2]
    optimizer.addUser("User1", tarif_user1, uncontrollableLoad_user1)

    optimizer.getOptimizedResults()

