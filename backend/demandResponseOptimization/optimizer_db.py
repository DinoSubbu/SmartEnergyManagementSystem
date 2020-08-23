from demandResponseOptimization.optimizer import Optimizer
from database.databasehandler import MariaDB_handler
import database.optimizerModel as optimizerModel
import database.models as entitymodel
import database.pricesModel as pricesModel
from datetime import datetime, timedelta
import json

class NotEnoughDataException(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

class Optimzer_DB():

    def __init__(self, schduleDBConfig, entityDBConfig, priceDBConfig, number_of_time_steps=24, time_limit=None, gap_factor=10):
        self.scheduleDB = MariaDB_handler(**schduleDBConfig)
        self.scheduleDB.createTables(optimizerModel.Base)
        self.entityDB = MariaDB_handler(**entityDBConfig)
        self.entityDB.createTables(entitymodel.Base)
        self.priceDB = MariaDB_handler(**priceDBConfig)
        self.priceDB.createTables(pricesModel.Base)
        self.number_of_time_steps = number_of_time_steps
        self.time_limit = time_limit
        self.gap_factor = gap_factor

    def writeScheduleToDB(self, obj_function, use_this=False):
        '''
        Loads all data, generates a schedule and writes it to the database.
        '''
        self.__loadGrid()
        date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        self.__loadForecast(date)
        self.__loadBatteryEnergy(date)
        try:
            self.__loadPrices(date)
        except NotEnoughDataException:
            print('No current prices. Use the prices from yesterday.')
            self.__loadPrices(date - timedelta(days=1))
        obj_value, schedule = self.__optimize(obj_function, self.time_limit, self.gap_factor)
        try:
            session_scheduleDB = self.scheduleDB.create_session()
            schedule_DB_data = session_scheduleDB.query(optimizerModel.Schedule) \
                .filter(
                    optimizerModel.Schedule.date == date,
                    optimizerModel.Schedule.obj_function == obj_function
                    ).first()
            if schedule_DB_data:
                schedule_DB_data.obj_value = obj_value
                schedule_DB_data.schedule = schedule
                self.scheduleDB.commitOrRollback(session_scheduleDB)
            else:
                schedule_DB_data = optimizerModel.Schedule(date, obj_function, obj_value,schedule)
                self.scheduleDB.addElementToDatabase(session_scheduleDB, schedule_DB_data)
        finally:
            self.scheduleDB.close_session(session_scheduleDB)
        return schedule_DB_data

    def setObjectiveInDB(self, obj_function):
        '''
        Sets the objective of the next day.
        '''
        date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        try:
            session_scheduleDB = self.scheduleDB.create_session()
            objective_DB_data = session_scheduleDB.query(optimizerModel.Objective) \
                .filter(
                    optimizerModel.Objective.date == date
                    ).first()
            if objective_DB_data:
                objective_DB_data.obj_function = obj_function
                self.scheduleDB.commitOrRollback(session_scheduleDB)
            else:
                objective_DB_data = optimizerModel.Objective(date, obj_function)
                self.scheduleDB.addElementToDatabase(session_scheduleDB, objective_DB_data)
        finally:
            self.scheduleDB.close_session(session_scheduleDB)
        return objective_DB_data

    def setSameObjectiveAsLastDay(self):
        '''
        Sets the objective of the next day with the value of the objective of this day, if there is no objective for tomorrow.
        '''
        date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        try:
            session_scheduleDB = self.scheduleDB.create_session()
            objective_DB_data = session_scheduleDB.query(optimizerModel.Objective) \
                .filter(
                    optimizerModel.Objective.date == date
                    ).first()
            if objective_DB_data:
                objective = objective_DB_data.obj_function
            else:
                objective = 'cost'
            new_date = date + timedelta(days=1)
            new_objective_DB_data = session_scheduleDB.query(optimizerModel.Objective) \
                .filter(
                    optimizerModel.Objective.date == new_date
                    ).first()
            if not  new_objective_DB_data:
                new_objective_DB_data = optimizerModel.Objective(new_date, objective)
                self.scheduleDB.addElementToDatabase(session_scheduleDB, new_objective_DB_data)
        finally:
            self.scheduleDB.close_session(session_scheduleDB)
        return new_objective_DB_data



    def __loadGrid(self):
        ''' 
        Loads the micro grid from the database.
        '''
        self.windTurbines = []
        self.solarPanels = []
        self.batteries = []
        self.buildings = []
        try:
            session_entityDB = self.entityDB.create_session()
            for windturbine in self.entityDB.getAll(session_entityDB,entitymodel.WindTurbine):
                self.windTurbines.append(windturbine)

            for solarpanel in self.entityDB.getAll(session_entityDB, entitymodel.SolarPanel):
                self.solarPanels.append(solarpanel)

            for building in self.entityDB.getAll(session_entityDB, entitymodel.Building):
                self.buildings.append(building)

            for battery in self.entityDB.getAll(session_entityDB, entitymodel.Battery):
                self.batteries.append(battery)
        finally:
            self.entityDB.close_session(session_entityDB)

    def __loadForecast(self, date):
        '''
        Loads the simulation forecast data from the database.
        '''
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        self.gen_forecasts = {}
        try:
            session_entityDB = self.entityDB.create_session() 
            for solarpanel in self.solarPanels:
                forcast = session_entityDB \
                    .query(entitymodel.SimulationForecastSolarPanel) \
                    .filter(
                        entitymodel.SimulationForecastSolarPanel.solarpanel_name == solarpanel.name,
                        entitymodel.SimulationForecastSolarPanel.timestamp >= date_start, 
                        entitymodel.SimulationForecastSolarPanel.timestamp < date_end
                        ).all()
                if len(forcast) != self.number_of_time_steps:
                    raise NotEnoughDataException(f'Not enough forcast data for {solarpanel.name}.')
                self.gen_forecasts[solarpanel.name] = [item.supply for item in forcast]

            for windturbine in self.windTurbines:
                forcast = session_entityDB \
                    .query(entitymodel.SimulationForecastWindTurbine) \
                    .filter(
                        entitymodel.SimulationForecastWindTurbine.windturbine_name == windturbine.name,
                        entitymodel.SimulationForecastWindTurbine.timestamp >= date_start, 
                        entitymodel.SimulationForecastWindTurbine.timestamp < date_end
                        ).all()
                if len(forcast) != self.number_of_time_steps:
                    raise NotEnoughDataException(f'Not enough forcast data for {windturbine.name}.')
                self.gen_forecasts[windturbine.name] = [item.supply for item in forcast]
        finally:
            self.entityDB.close_session(session_entityDB)

    def __loadPrices(self, date):
        '''
        Loads the prices from the database.
        '''
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        try:
            session_priceDB = self.priceDB.create_session()
            price_data = session_priceDB \
                .query(pricesModel.PriceForecast) \
                    .filter(
                        pricesModel.PriceForecast.timestamp >= date_start,
                        pricesModel.PriceForecast.timestamp < date_end
                    ).all()
            if len(price_data) != self.number_of_time_steps:
                    raise NotEnoughDataException(f'Not enough price data.')
            self.prices_buy = [price.price for price in price_data]
            # sell prices are are 10 percent less than buy prices due to taxes
            self.prices_sell = [price.price*0.9 for price in price_data]
        finally:
            self.priceDB.close_session(session_priceDB)

    def __loadBatteryEnergy(self, date):
        '''
        Loads the battery energy from the last schedue, so that energy can be transfered to the next day.
        If there is no last schedule, initialize all batteries with energy 0.
        '''
        self.batteries_startEnergy = {}
        date = date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        try:
            session_scheduleDB = self.scheduleDB.create_session()
            objective_DB_data = session_scheduleDB.query(optimizerModel.Objective) \
                .filter(
                    optimizerModel.Objective.date == date
                    ).first()
            if objective_DB_data:
                objective = objective_DB_data.obj_function
            else:
                objective = 'cost'
            last_schedule = session_scheduleDB \
                .query(optimizerModel.Schedule) \
                .filter(
                    optimizerModel.Schedule.date==date,
                    optimizerModel.Schedule.obj_function==objective
                    ).first()
            if last_schedule:
                battery_schedule = last_schedule['batteries']
                for battery in self.batteries:
                    self.batteries_startEnergy[battery.name] = battery_schedule[battery.name]['energy'][24]
            else:
                for battery in self.batteries:
                    self.batteries_startEnergy[battery.name] = 0
        finally:
            self.scheduleDB.close_session(session_scheduleDB)



    def __optimize(self, obj_function, time_limit=None, gap_factor=10):
        '''
        Initialize the optimizer and run the optimization.
        '''
        opt = Optimizer(self.number_of_time_steps)
        for building in self.buildings:
            opt.addBuilding(building)
        for battery in self.batteries:
            opt.addBattery(battery, self.batteries_startEnergy[battery.name])
        for name, forecast in self.gen_forecasts.items():
            opt.addGenerator(name, forecast)
        opt.addPriceBuy(self.prices_buy)
        opt.addPriceSell(self.prices_sell)
        if time_limit:
            opt.set_time_limit(time_limit)
        # Try the optimization until is works with the specified time limit and mip gap
        # After each time out triple the mip gap and try it again
        while(True):
            try:
                opt.optimize(obj_function)
                break
            except TimeoutError:
                opt.multiply_mip_gap(gap_factor)
        return opt.getObjFuncValue(), opt.getSchedule()

if __name__ == "__main__":
    configDB = {'user':'myusr', 'password':'myusrpass', 'host':'localhost', 'port':'3306', 'database':'mydb'}
    opt_db = Optimzer_DB(configDB, configDB, configDB)
    opt_db.writeScheduleToDB('cost')