from gurobipy import *


'''SETS'''
'''Plant1 is an oil generator and Plant2 is a small solar field'''
plants = ['Plant1', 'Plant2']

'''two users'''
users = ['User1', 'User2']

'''two devices'''
devices = ['WM', 'DW']

'''optimization horizon: 24 hours, 1 hour resolution'''
time_steps = range(0,24)

'''PARAMETERS'''
'''the output of the solar field is known, assuming a perfect forecast kW'''
pv_out = [0,0,0,0,2,4,8,10,13,14,16,12,12,13,11,9,6,8,8,0,0,0,0,0]

'''technical characteristics and limits of power plants kW'''
plants_char = { 'Plant1': {'p_min': 10, 'p_max': 70},
                'Plant2': {'p_min': 0, 'p_max': pv_out}}

'''generation prce of power plants ct/kWh'''
price = {'Plant1': 10, 'Plant2': 4}

'''minimum and maximum exchangable power with the main grid. + means we import power from the main, - means we export power to the main grid'''
grid = { 'p_min': -70, 'p_max': 70}


'''user 1 electricity tariff: 6-22 30ct/kWh; 22-6 20ct/kWh'''
'''user 2 electricity tariff: 6-10 35 ct/kWh; 10-18 25 ct/kWh; 18-22 35 ct/kWh; 22-6 18 ct/kWh'''
tariff = {'User1': [20,20,20,20,20,20,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,20,20],
          'User2': [18,18,18,18,18,18,35,35,35,35,25,25,25,25,25,25,25,25,35,35,35,35,18,18]}

'''users uncontrollable load profiles kW'''
UD = {'User1': [0.2,0.2,0.2,0.2,0.2,0.6,0.6,0.6,1,1,1,0.5,0.5,0.5,0.4,0.4,0.4,0.8,0.8,0.6,0.6,0.4,0.2,0.2],
      'User2': [0.2,0.2,0.2,0.2,0.2,1,1,1,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.6,0.6,0.6,0.6,0.4,0.2,0.2]}

'''Each user has two loads to schedule: Wasching machine WM, dish washer DW'''
CED = {'WM': {'EST': 9, 'LET': 17, 'E': 2, 'LOT': 2},
       'DW': {'EST': 9, 'LET': 12, 'E': 1.8, 'LOT': 2}}


'''MODEL'''
model = Model('Optimal Scheduling')

'''add variables'''
p_gen = model.addVars(plants, time_steps, lb = 0, vtype=GRB.CONTINUOUS, name="pow_gen") # generated power from plants
p_grid = model.addVars(time_steps, lb = -GRB.INFINITY, vtype=GRB.CONTINUOUS, name="exch_pow") # power exchanged with the main grid >0 if import <0 if export

tot_d = model.addVars(users, time_steps, lb = 0, vtype=GRB.CONTINUOUS, name="total_demand") # total demand

status1 = model.addVars(devices, time_steps, vtype=GRB.BINARY, name="Dev_status_user1") # status of devices of user1
st_start1 = model.addVars(devices, time_steps, vtype=GRB.BINARY, name="start_status_user1")
st_end1 = model.addVars(devices, time_steps, vtype=GRB.BINARY, name="end_status_user1")

status2 = model.addVars(devices, time_steps, vtype=GRB.BINARY, name="Dev_status_user2") # status of devices of user1
st_start2 = model.addVars(devices, time_steps, vtype=GRB.BINARY, name="start_status_user2")
st_end2 = model.addVars(devices, time_steps, vtype=GRB.BINARY, name="end_status_user2")

'''add constraints'''
'''balance'''
model.addConstrs((quicksum(p_gen[pp,t] for pp in plants) - quicksum(tot_d[u,t] for u in users) + p_grid[t] == 0 for t in time_steps),name='balance')

'''generation limit'''
model.addConstrs((p_gen['Plant1',t] >= plants_char['Plant1']['p_min'] for t in time_steps), name='P1limitmax')
model.addConstrs((p_gen['Plant1',t] <= plants_char['Plant1']['p_max'] for t in time_steps), name='P1limitmin')

model.addConstrs((p_gen['Plant2',t] == plants_char['Plant2']['p_max'][t] for t in time_steps), name='P2output')

'''grid exchange'''
model.addConstrs((p_grid[t] >= grid['p_min'] for t in time_steps), name='gridmin')
model.addConstrs((p_grid[t] <= grid['p_max'] for t in time_steps), name='gridmax')

'''DEMAND SIDE-User1'''
'''total demand'''
model.addConstrs((tot_d['User1',t] == UD['User1'][t] + quicksum(CED[d]['E']*status1[d,t] for d in devices) for t in time_steps), name='U1totd')

'''device start and end'''
model.addConstrs((quicksum(st_start1[d,t] for t in time_steps if t >= CED[d]['EST'] or t <= CED[d]['LET']-CED[d]['LOT']) == 1 for d in devices), name='U1singlestart')
model.addConstrs((quicksum(st_end1[d,t] for t in time_steps if t <= CED[d]['LET'] or t >= CED[d]['EST']+CED[d]['LOT']) == 1 for d in devices), name='U1singleend')
model.addConstrs((st_start1[d,t] ==0 for d in devices for t in time_steps if t < CED[d]['EST'] or t > CED[d]['LET']-CED[d]['LOT']), name='U1startzero')
model.addConstrs((st_end1[d,t] ==0 for d in devices for t in time_steps if t < CED[d]['EST']+CED[d]['LOT'] or t > CED[d]['LET']), name='U1endzero')
model.addConstrs((st_end1[d,t] == st_start1[d,t-CED[d]['LOT']] for d in devices for t in time_steps if t>= CED[d]['LOT']), name='U1startend')

'''device status'''
model.addConstrs((quicksum(status1[d,t] for t in time_steps if t >= CED[d]['EST'] or t <= CED[d]['LET']) == CED[d]['LOT'] for d in devices), name='U1duration')
model.addConstrs((status1[d,t] ==0 for d in devices for t in time_steps if t < CED[d]['EST'] or t > CED[d]['LET']), name='U1statuszero')
model.addConstrs((quicksum(status1[d,tau] for tau in range(t)) >= CED[d]['LOT']*st_end1[d,t] for d in devices for t in time_steps), name='U1endafterLOT')
model.addConstrs((quicksum(st_start1[d,tau] for tau in range(t+1)) >= status1[d,t] for d in devices for t in time_steps), name='U1statusafterstart')

'''DEMAND SIDE-User2'''
'''total demand'''
model.addConstrs((tot_d['User2',t] == UD['User2'][t] + quicksum(CED[d]['E']*status2[d,t] for d in devices) for t in time_steps), name='U2totd')

'''device start and end'''
model.addConstrs((quicksum(st_start2[d,t] for t in time_steps if t >= CED[d]['EST'] or t <= CED[d]['LET']-CED[d]['LOT']) == 1 for d in devices), name='U2singlestart')
model.addConstrs((quicksum(st_end2[d,t] for t in time_steps if t <= CED[d]['LET'] or t >= CED[d]['EST']+CED[d]['LOT']) == 1 for d in devices), name='U2singleend')
model.addConstrs((st_start2[d,t] ==0 for d in devices for t in time_steps if t < CED[d]['EST'] or t > CED[d]['LET']-CED[d]['LOT']), name='U2startzero')
model.addConstrs((st_end2[d,t] ==0 for d in devices for t in time_steps if t < CED[d]['EST']+CED[d]['LOT'] or t > CED[d]['LET']), name='U2endzero')
model.addConstrs((st_end2[d,t] == st_start2[d,t-CED[d]['LOT']] for d in devices for t in time_steps if t>= CED[d]['LOT']), name='U2startend')

'''device status'''
model.addConstrs((quicksum(status2[d,t] for t in time_steps if t >= CED[d]['EST'] or t <= CED[d]['LET']) == CED[d]['LOT'] for d in devices), name='U2duration')
model.addConstrs((status2[d,t] ==0 for d in devices for t in time_steps if t < CED[d]['EST'] or t > CED[d]['LET']), name='U2statuszero')
model.addConstrs((quicksum(status2[d,tau] for tau in range(t)) >= CED[d]['LOT']*st_end2[d,t] for d in devices for t in time_steps), name='U2endafterLOT')
model.addConstrs((quicksum(st_start2[d,tau] for tau in range(t+1)) >= status2[d,t] for d in devices for t in time_steps), name='U2statusafterstart')


'''OBJECTIVE'''
#obj1 = quicksum(tariff[u][t]*tot_d[u,t]*1/100 for u in users for t in time_steps) #euro
#model.setObjective(obj1, GRB.MINIMIZE)

obj2 = (quicksum(tariff[u][t]*tot_d[u,t]*1/100 for u in users for t in time_steps) - quicksum(price[pp]*p_gen[pp,t]*1/100 for pp in plants for t in time_steps))

model.setObjective(obj2, GRB.MAXIMIZE)

model.optimize()

msgdict = {GRB.OPTIMAL : 'Optimal', GRB.INFEASIBLE : 'Infeasible model'}
msg = msgdict[model.status]
if msg == 'Infeasible model':
    print('The model is infeasible; computing IIS')
    model.computeIIS()
    print('\nThe following constraint(s) cannot be satisfied:')
    for c in model.getConstrs():
        if c.IISConstr:
            print('%s' % c.constrName)

for v in model.getVars():
    if v.X != 0:
        print("%s %f" % (v.Varname, v.X))
print('\n')


'''print some results'''        
bill1 = sum(tariff['User1'][t]*tot_d['User1',t].X*1/100 for t in time_steps)
bill2 = sum(tariff['User2'][t]*tot_d['User2',t].X*1/100 for t in time_steps)
revenue1 = sum(price['Plant1']*p_gen['Plant1',t].X*1/100 for t in time_steps)
revenue2 = sum(price['Plant2']*p_gen['Plant2',t].X*1/100 for t in time_steps)

tst_WM1 = [t for t in time_steps if st_start1['WM',t].X ==1]
tend_WM1 = [t for t in time_steps if st_end1['WM',t].X ==1]
tst_DW1 = [t for t in time_steps if st_start1['DW',t].X ==1]
tend_DW1 = [t for t in time_steps if st_end1['DW',t].X ==1]

tst_WM2 = [t for t in time_steps if st_start2['WM',t].X ==1]
tend_WM2 = [t for t in time_steps if st_end2['WM',t].X ==1]
tst_DW2 = [t for t in time_steps if st_start2['DW',t].X ==1]
tend_DW2 = [t for t in time_steps if st_end2['DW',t].X ==1]

print('The microgrid profit is {} euro \n'.format(model.objval))

print('Bill of user 1 is {} euro \n'.format(bill1))

print('The optimal scheduling for the WM of user 1 would be: turn on at {0} and turn off at {1} \n'.format(tst_WM1, tend_WM1))

print('The optimal scheduling for the DW of user 1 would be: turn on at {0} and turn off at {1} \n'.format(tst_DW1, tend_DW1))

print('Bill of user 2 is {} euro \n'.format(bill2))

print('The optimal scheduling for the WM of user 2 would be: turn on at {0} and turn off at {1} \n'.format(tst_WM2, tend_WM2))

print('The optimal scheduling for the DW of user 2 would be: turn on at {0} and turn off at {1} \n'.format(tst_DW2, tend_DW2))

print('Revenue of plant 1 is {} euro \n'.format(revenue1))

print('Revenue of plant 2 is {} euro \n'.format(revenue2))