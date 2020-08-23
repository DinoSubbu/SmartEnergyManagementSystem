from database.databasehandler import MariaDB_handler
import database.models as entitymodel
import database.weatherModel as weathermodel
import database.optimizerModel as schedulemodel
from simulation.demandside.building_schedule import BuildingSim
from simulation.supplyside.solarPanel import SolarPanelSim
from simulation.supplyside.windTurbine import WindTurbineSim
from simulation.storage.battery_schedule import BatterySim
from datetime import datetime, timedelta




class NoWeatherDataException(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class Simulation():

    def __init__(self, weatherDBConfig, entityDBConfig, scheduleDBConfig):
        # init weater database
        self.weatherDB = MariaDB_handler(**weatherDBConfig)
        self.weatherDB.createTables(weathermodel.Base)
        # init entity database
        self.entityDB = MariaDB_handler(**entityDBConfig)
        self.entityDB.createTables(entitymodel.Base)
        # init schedule database
        self.scheduleDB = MariaDB_handler(**scheduleDBConfig)
        self.scheduleDB.createTables(schedulemodel.Base)
        self.windTurbines = {}
        self.solarPanels = {}
        self.batteries = {}
        self.buildings = {}
        

    def init_sim(self, startingTime):
        self.time = startingTime.replace(minute=0, second=0, microsecond=0)
        self.__loadMicroGridFromDatabase()

        self.simObj = entitymodel.Simulation(self.time, True)
        try:
            session_entityDB = self.entityDB.create_session()
            # stop running simulations
            sims = session_entityDB.query(entitymodel.Simulation).filter_by(running=True).all()
            for sim in sims:
                sim.running = False
            self.entityDB.commitOrRollback(session_entityDB)
            self.entityDB.addElementToDatabase(session_entityDB, self.simObj)
        finally:
            self.entityDB.close_session(session_entityDB)
    
    def close_sim(self):
        try:
            session_entityDB = self.entityDB.create_session()
            self.simObj = session_entityDB.query(entitymodel.Simulation).filter_by(id=self.simObj.id).first()
            self.simObj.running=False
            self.entityDB.commitOrRollback(session_entityDB)
        finally:
            self.entityDB.close_session(session_entityDB)

    def __loadMicroGridFromDatabase(self):
        self.windTurbines = {}
        self.solarPanels = {}
        self.batteries = {}
        self.buildings = {}
        try:
            session_entityDB = self.entityDB.create_session()
            for windturbine in self.entityDB.getAll(session_entityDB, entitymodel.WindTurbine):
                self.windTurbines[windturbine.name] = WindTurbineSim.createFromModel(windturbine)

            for solarpanel in self.entityDB.getAll(session_entityDB, entitymodel.SolarPanel):
                self.solarPanels[solarpanel.name] = SolarPanelSim.createFromModel(solarpanel)

            for building in self.entityDB.getAll(session_entityDB, entitymodel.Building):
                self.buildings[building.name] = BuildingSim.createFromModel(building)

            for battery in self.entityDB.getAll(session_entityDB, entitymodel.Battery):
                self.batteries[battery.name] = BatterySim.createFromModel(battery)
        finally:
            self.entityDB.close_session(session_entityDB)


    def __getCurrentWeatherData(self, lat, long):
        try:
            session_weatherDB = self.weatherDB.create_session()
            currentWeather = session_weatherDB.query(weathermodel.WeatherCurrent).filter_by(lat=lat, long=long, timestamp=self.time).first()
            if currentWeather:
                return currentWeather
            forecastWeather = session_weatherDB.query(weathermodel.WeatherForecast).filter_by(lat=lat, long=long, timestamp=self.time).first()
        finally:
            self.weatherDB.close_session(session_weatherDB)
        if forecastWeather:
            print("return forecast")
            return forecastWeather
        raise NoWeatherDataException(f"No data is available. lat:{lat}, long:{long}, timestamp:{str(self.time)}")

    def __getForecastWeatherDataList(self, lat, long):
        try:
            session_weatherDB = self.weatherDB.create_session()
            forecastWeather = session_weatherDB.query(weathermodel.WeatherForecast) \
                .filter(
                    weathermodel.WeatherForecast.timestamp>=self.time, 
                    weathermodel.WeatherForecast.lat==lat,
                     weathermodel.WeatherForecast.long==long) \
                .all()
        finally:
            self.weatherDB.close_session(session_weatherDB)
        if forecastWeather:
            return forecastWeather
        raise NoWeatherDataException(f"No forecast data is available. lat:{lat}, long:{long}, timestamp:{str(self.time)}")
    
    def simulateNextHour(self):
        self.__loadSchedule()
        day_of_the_year = self.time.timetuple().tm_yday
        hour_of_the_day = self.time.timetuple().tm_hour
        total_energy = 0
        total_energy += self.__simulateWindTurbines()
        total_energy += self.__simulateSolarPanels(day_of_the_year)
        total_energy -= self.__simulateBuildings(hour_of_the_day)
        total_energy -= self.__simulateBatteries(hour_of_the_day)
        try:
            session_entityDB = self.entityDB.create_session()
            total_sim = session_entityDB.query(entitymodel.SimulationTotalEnergy).filter_by(timestamp=self.time).first()
            if total_sim:
                total_sim.energy = total_energy
                self.entityDB.commitOrRollback(session_entityDB)
            else:
                self.entityDB.addElementToDatabase(session_entityDB, entitymodel.SimulationTotalEnergy(self.time, total_energy))
        finally:
            self.entityDB.close_session(session_entityDB)
        self.time = self.time + timedelta(hours = 1)

    def simulateForecast(self):
        try:
            session_entityDB = self.entityDB.create_session()
            for windturbine in self.windTurbines.values():
                try:
                    forecastList = self.__getForecastWeatherDataList(windturbine.lat, windturbine.long)
                except NoWeatherDataException as e:
                    print(e)
                for forecast in forecastList:
                    supply = windturbine.computePower(forecast.temp, forecast.pressure, forecast.windSpeed, forecast.relativeHumidity)
                    forecast_data = session_entityDB.query(entitymodel.SimulationForecastWindTurbine).filter_by(windturbine_name=windturbine.name, timestamp=forecast.timestamp).first()
                    if forecast_data:
                        forecast_data.supply = supply
                        self.entityDB.commitOrRollback(session_entityDB)
                    else: 
                        forecast_data = entitymodel.SimulationForecastWindTurbine(windturbine.name, forecast.timestamp, supply)
                        self.entityDB.addElementToDatabase(session_entityDB, forecast_data)

            for solarpanel in self.solarPanels.values():
                try:
                    forecastList = self.__getForecastWeatherDataList(solarpanel.lat, solarpanel.long)
                except NoWeatherDataException as e:
                    print(e)
                for forecast in forecastList:
                    day_of_the_year = forecast.timestamp.timetuple().tm_yday
                    supply = solarpanel.computePower(day_of_the_year, forecast.temp, forecast.s_horizontal)
                    forecast_data = session_entityDB.query(entitymodel.SimulationForecastSolarPanel).filter_by(solarpanel_name=solarpanel.name, timestamp=forecast.timestamp).first()
                    if forecast_data:
                        forecast_data.supply = supply
                        self.entityDB.commitOrRollback(session_entityDB)
                    else: 
                        forecast_data = entitymodel.SimulationForecastSolarPanel(solarpanel.name, forecast.timestamp, supply)
                        self.entityDB.addElementToDatabase(session_entityDB, forecast_data)
        finally:
            self.entityDB.close_session(session_entityDB)


    def __simulateWindTurbines(self):
        total_suppy = 0
        try:
            session_entityDB = self.entityDB.create_session()
            for windturbine in self.windTurbines.values():
                weather_data = self.__getCurrentWeatherData(windturbine.lat, windturbine.long)
                supply = windturbine.computePower(weather_data.temp, weather_data.pressure, weather_data.windSpeed, weather_data.relativeHumidity)
                total_suppy += supply
                windturbine_sim = session_entityDB.query(entitymodel.SimulationWindTurbine).filter_by(windturbine_name=windturbine.name, timestamp=self.time).first()
                if windturbine_sim:
                    windturbine_sim.supply = supply
                    self.entityDB.commitOrRollback(session_entityDB)
                else:
                    self.entityDB.addElementToDatabase(session_entityDB, entitymodel.SimulationWindTurbine(windturbine.name, self.time, supply))
            return total_suppy
        finally:
            self.entityDB.close_session(session_entityDB)

    def __simulateSolarPanels(self, day_of_the_year):
        total_suppy = 0
        try:
            session_entityDB = self.entityDB.create_session()
            for solarpanel in self.solarPanels.values():
                weather_data = self.__getCurrentWeatherData(solarpanel.lat, solarpanel.long)
                supply = solarpanel.computePower(day_of_the_year, weather_data.temp, weather_data.s_horizontal)
                total_suppy += supply
                solarpanel_sim = session_entityDB.query(entitymodel.SimulationSolarPanel).filter_by(solarpanel_name=solarpanel.name, timestamp=self.time).first()
                if solarpanel_sim:
                    solarpanel_sim.supply = supply
                    self.entityDB.commitOrRollback(session_entityDB)
                else:
                    self.entityDB.addElementToDatabase(session_entityDB, entitymodel.SimulationSolarPanel(solarpanel.name, self.time, supply))
            return total_suppy
        finally:
            self.entityDB.close_session(session_entityDB)
    
    def __simulateBuildings(self, hour):
        total_demand = 0
        try:
            session_entityDB = self.entityDB.create_session()
            for name, building in self.buildings.items():
                building.setSchedule(self.schedule['buildings'][name])
                demand = building.getDemand(hour)
                componentState = building.getComponentState(hour)
                total_demand += demand
                building_sim = session_entityDB.query(entitymodel.SimulationBuilding).filter_by(building_name=name, timestamp=self.time).first()
                if building_sim:
                    building_sim.demand = demand
                    building_sim.componentState = componentState
                    self.entityDB.commitOrRollback(session_entityDB)
                else:
                    self.entityDB.addElementToDatabase(session_entityDB, entitymodel.SimulationBuilding(name, self.time, demand, componentState))
            return total_demand
        finally:
            self.entityDB.close_session(session_entityDB)

    def __simulateBatteries(self, hour):
        total_charging_rate = 0
        try:
            session_entityDB = self.entityDB.create_session()
            for name, battery in self.batteries.items():
                battery.setSchedule(self.schedule['batteries'][name])
                rate = battery.getRate(hour)
                total_charging_rate += rate
                energy = battery.getEnergy(hour)
                battery_sim = session_entityDB.query(entitymodel.SimulationBattery).filter_by(battery_name=name, timestamp=self.time).first()
                if battery_sim:
                    battery_sim.energy = energy
                    battery_sim.rate = rate
                    self.entityDB.commitOrRollback(session_entityDB)
                else:
                    self.entityDB.addElementToDatabase(session_entityDB, entitymodel.SimulationBattery(name, self.time, energy, rate, battery.energyUpperBound))
            return total_charging_rate
        finally:
            self.entityDB.close_session(session_entityDB)

    def __loadSchedule(self):
        schedule_date = self.time.replace(hour=0, minute=0, second=0, microsecond=0)
        schedule_data = None
        try:
            session_scheduleDB = self.scheduleDB.create_session()
            objective_data = session_scheduleDB.query(schedulemodel.Objective).filter_by(date=schedule_date).first()
            if objective_data:
                schedule_data = session_scheduleDB.query(schedulemodel.Schedule) \
                    .filter(
                        schedulemodel.Schedule.date == schedule_date,
                        schedulemodel.Schedule.obj_function == objective_data.obj_function
                        ).first()
        finally:
            self.scheduleDB.close_session(session_scheduleDB)
        if schedule_data:
            self.schedule = schedule_data.schedule
        else:
            self.__generateDefaultSchedule()

    def __generateDefaultSchedule(self):
        schedule = {'buildings':{}, 'batteries':{}}
        zero = [0 for i in range(0, 24)]
        idle = ['idle' for i in range(0, 24)]
        for name, building in self.buildings.items():
            schedule['buildings'][name] = {}
            for comp in building.listOfComponets:
                schedule['buildings'][name][comp.name] = {'start':comp.let-comp.lot, 'end':comp.let}
        for name, battery in self.batteries.items():
            schedule['batteries'][name] = {'state':idle, 'rate':zero, 'energy':zero}
        self.schedule = schedule

if __name__ == "__main__":
    configDB = {'user':'myusr', 'password':'myusrpass', 'host':'localhost', 'port':'3306', 'database':'mydb'}
    sim = Simulation(configDB, configDB, configDB)
    sim.init_sim(datetime.now()+ timedelta(hours = 1))
    sim.simulateForecast()
    sim.simulateNextHour()
    sim.simulateNextHour()
    sim.simulateNextHour()
    sim.simulateNextHour()
    print('fertig')