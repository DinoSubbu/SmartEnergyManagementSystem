from flask import Flask
from flask import request
from flask_cors import CORS
import database.models as entityModels
import database.pricesModel as pricesModels
import database.co2Model as co2Model
import database.gasBoilerModel as gasBoilerModel
import database.optimizerModel as optimizerModel
from database.databasehandler import MariaDB_handler
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
import json
from util.json_encoder import Encoder
from datetime import datetime, timedelta
import config
import requests
import threading

#FLASK_APP=simulation/building_service.py flask run

app = Flask(__name__)
CORS(app)

entityDBConfig = {"user":"myusr", "password":"myusrpass", "host":"localhost", "port":"3306", "database":"mydb"}
entityDB = MariaDB_handler(**entityDBConfig)
entityDB.createTables(entityModels.Base)

priceDBConfig = {"user":"myusr", "password":"myusrpass", "host":"localhost", "port":"3306", "database":"mydb"}
priceDB = MariaDB_handler(**priceDBConfig)
priceDB.createTables(pricesModels.Base)

co2DBConfig = {"user":"myusr", "password":"myusrpass", "host":"localhost", "port":"3306", "database":"mydb"}
co2DB = MariaDB_handler(**co2DBConfig)
co2DB.createTables(co2Model.Base)

gasBoilerDBConfig = {"user":"myusr", "password":"myusrpass", "host":"localhost", "port":"3306", "database":"mydb"}
gasBoilerDB = MariaDB_handler(**co2DBConfig)
gasBoilerDB.createTables(co2Model.Base)

simDBConfig = {"user":"myusr", "password":"myusrpass", "host":"localhost", "port":"3306", "database":"mydb"}
simDB = MariaDB_handler(**simDBConfig)
simDB.createTables(entityModels.Base)

optimizerDBConfig = {"user":"myusr", "password":"myusrpass", "host":"localhost", "port":"3306", "database":"mydb"}
optimizerDB = MariaDB_handler(**optimizerDBConfig)
optimizerDB.createTables(optimizerModel.Base)

@app.route('/')
def index():
    return 'Element Service'
    
###################################
# functions for creating entities #
###################################

@app.route('/windturbine/create', methods=['POST'])
def create_windturbine():
    '''
    Creates the windturbine specified in the request.
    '''
    if request.method == 'POST':
        if request.is_json:
            # check if a simulation is running
            if get_number_of_running_simulations() == 0:
                try:
                    session = entityDB.create_session()
                    req_data = request.get_json()
                    windturbine = entityModels.WindTurbine(req_data['name'], req_data['lat'], req_data['long'], req_data['powerCoefficient'], req_data['radius'])
                    entityDB.addElementToDatabase(session, windturbine)
                except KeyError:
                    return 'json does not match the format', 415
                except IntegrityError:
                    return 'duplicate', 409
                finally:
                    entityDB.close_session(session)
                return windturbine.toJson(), 201
            else:
                return "Simulation is running", 423
    return "HTTP-Method not supported", 404

@app.route('/solarpanel/create', methods=['POST'])
def create_solarpanel():
    '''
    Creates the solarpanel specified in the request.
    '''
    if request.method == 'POST':   
        if request.is_json:
            # check if a simulation is running
            if get_number_of_running_simulations() == 0:
                try:
                    session = entityDB.create_session()
                    req_data = request.get_json()
                    solarpanal = entityModels.SolarPanel(req_data['name'], req_data['lat'], req_data['long'], req_data['powerCoefficient'], req_data['area'], req_data['angleOfModule'])
                    entityDB.addElementToDatabase(session, solarpanal)
                except KeyError:
                    return 'json does not match the format', 415
                except IntegrityError:
                    return 'duplicate', 409
                finally:
                    entityDB.close_session(session)
                return solarpanal.toJson(), 201
            else:
                return "Simulation is running", 423
    return "HTTP-Method not supported", 404

@app.route('/battery/create', methods=['POST'])
def create_battery():
    '''
    Creates the battery specified in the request.
    '''
    if request.method == 'POST':
        if request.is_json:
            # check if a simulation is running
            if get_number_of_running_simulations() == 0:
                try:
                    session = entityDB.create_session()
                    req_data = request.get_json()
                    battery = entityModels.Battery(req_data['name'], req_data['lat'], req_data['long'], req_data['batteryEfficiency'], req_data['chargeUpperBound'], req_data['dischargeUpperBound'], req_data['energyUpperBound'], req_data['selfDischargingRate'])
                    entityDB.addElementToDatabase(session, battery)
                except KeyError:
                    return 'json does not match the format', 415
                except IntegrityError:
                    return 'duplicate', 409
                finally:
                    entityDB.close_session(session)
                return battery.toJson(), 201
            else:
                return "Simulation is running", 423
    return "HTTP-Method not supported", 404

@app.route('/building/create', methods=['POST'])
def create_building():
    '''
    Creates the builiding specified in the request.
    '''
    if request.method == 'POST':
        if request.is_json:
            # check if a simulation is running
            if get_number_of_running_simulations() == 0:
                try:
                    session = entityDB.create_session()
                    req_data = request.get_json()
                    building = entityModels.Building(req_data['name'], req_data['lat'], req_data['long'], req_data['mathematicalModel'], req_data['historicalData'])
                    for comp_data in req_data['components']:
                        # create components of the building
                        building.components.append(entityModels.Component(comp_data['name'], comp_data['est'], comp_data['let'], comp_data['e'], comp_data['lot']))
                    entityDB.addElementToDatabase(session, building)
                except KeyError:
                    return 'json does not match the format', 415
                except IntegrityError:
                    return 'duplicate', 409
                finally:
                    entityDB.close_session(session)
                return building.toJson(), 201
            else:
                return "Simulation is running", 423
    return "HTTP-Method not supported", 404

#################################################
# functions for deleting entities, not finished #
#################################################

def delete_entity(model, name):
    '''
    Deletes the entity specified entity.
    '''
    if request.method == 'DELETE':
        if get_number_of_running_simulations() == 0:
            try:
                session = entityDB.create_session()
                entity = session.query(model).filter_by(name=name).first()
                if entity:
                    entityDB.deleteElementFromDatabase(session, entity)
                else:
                    return "Entity not found", 404
            finally:
                entityDB.close_session(session)
            return entity.toJson(), 200
        else:
            return "Simulation is running", 423
    return "HTTP-Method not supported", 404


#################################
# getter-functions for entities #
#################################

@app.route('/solarpanel/getAll', methods=['GET'])
def getAll_solarpanels():
    return getAllJson(entityDB, entityModels.SolarPanel)

@app.route('/solarpanel/get/<string:name>', methods=['GET'])
def get_solarpanel(name):
    return getByNameJson(entityModels.SolarPanel, name)

@app.route('/windturbine/getAll', methods=['GET'])
def getAll_windturbines():
    return getAllJson(entityDB, entityModels.WindTurbine)

@app.route('/windturbine/get/<string:name>', methods=['GET'])
def get_windturbine(name):
    return getByNameJson(entityModels.WindTurbine, name)

@app.route('/battery/getAll', methods=['GET'])
def getAll_batteries():
    return getAllJson(entityDB, entityModels.Battery)

@app.route('/battery/get/<string:name>', methods=['GET'])
def get_battery(name):
    return getByNameJson(entityModels.Battery, name)

@app.route('/building/getAll', methods=['GET'])
def getAll_buildings():
    return getAllJson(entityDB, entityModels.Building)

@app.route('/building/get/<string:name>', methods=['GET'])
def get_building(name):
    return getByNameJson(entityModels.Building, name)
    
    
###############################
# getter-functions for prices #
###############################

@app.route('/price/getAll', methods=['GET'])
def getAll_prices():
    """
    Returns all prices.
    """
    return getAllJson(priceDB, pricesModels.PriceForecast)

@app.route('/price/getRange/<string:start>/<string:end>', methods=['GET'])
def getPriceByRange(start, end):
    """
    Returns all prices which in the given time range.
    """
    if request.method == 'GET':
        try:
            session = priceDB.create_session()
            start_date = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
            end_date = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")
            prices = session.query(pricesModels.PriceForecast).filter(pricesModels.PriceForecast.timestamp>=start_date, pricesModels.PriceForecast.timestamp<=end_date).all()
            priceDict = [price.toDict() for price in prices]
            return json.dumps(priceDict, cls=Encoder), 200
        except Exception as e:
            return str(e), 500
        finally:
            priceDB.close_session(session)
    return "HTTP-Method not supported", 404

@app.route('/price/getRange/<string:start>', methods=['GET'])
def getPriceByRangeStart(start):
    """
    Returns all prices which are after the given start date.
    """
    if request.method == 'GET':
        try:
            session = priceDB.create_session()
            start_date = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
            prices = session.query(pricesModels.PriceForecast).filter(pricesModels.PriceForecast.timestamp>=start_date).all()
            priceDict = [price.toDict() for price in prices]
            return json.dumps(priceDict, cls=Encoder), 200
        except Exception as e:
            return str(e), 500
        finally:
            priceDB.close_session(session)
    return "HTTP-Method not supported", 404

@app.route('/price/get/<string:date>', methods=['GET'])
def get_price(date):
    """
    Returns the prices for given timestamp day.
    """
    if request.method == 'GET':
        try:
            session = priceDB.create_session()
            date_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
            price = session.query(pricesModels.PriceForecast).filter_by(timestamp=date_date).first()
            return price.toJson(), 200
        except Exception as e:
            return str(e), 500
        finally:
            priceDB.close_session(session)
    return "HTTP-Method not supported", 404

@app.route('/price/getlatest', methods=['GET'])
def get_price_latest():
    """
    Returns the prices for the most recent day.
    """
    if request.method == 'GET':
        try:
            session = priceDB.create_session()
            date = session.query(func.max(pricesModels.PriceForecast.timestamp)).first()
            if date == None:
                return "No data", 404
            prices = session.query(pricesModels.PriceForecast).filter(pricesModels.PriceForecast.timestamp>(date[0] - timedelta(days=1))).all()
            if prices:
                priceDict = [price.toDict() for price in prices]
                return json.dumps(priceDict, cls=Encoder), 200
            else:
                return 'No prices', 404
        except Exception as e:
            return str(e), 500
        finally:
            priceDB.close_session(session)
    return "HTTP-Method not supported", 404


##############################################
# getter-functions for co2 emission forecast #
##############################################

@app.route('/co2/getAll', methods=['GET'])
def getAll_co2Values():
    """
    Returns all co2 emission values.
    """
    return getAllJson(co2DB, co2Model.Co2ForecastProxy)

@app.route('/co2/getRange/<string:start>/<string:end>', methods=['GET'])
def getCo2ByRange(start, end):
    """
    Returns all Co2 emission values which are in the given time range.
    """
    if request.method == 'GET':
        try:
            session = co2DB.create_session()
            start_date = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
            end_date = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")
            co2Values = session.query(co2Model.Co2ForecastProxy).filter(co2Model.Co2ForecastProxy.timestamp>=start_date, co2Model.Co2ForecastProxy.timestamp<=end_date).all()
            co2Dict = [co2Value.toDict() for co2Value in co2Values]
            return json.dumps(co2Dict, cls=Encoder), 200
        except Exception as e:
            return str(e), 500
        finally:
            co2DB.close_session(session)
    return "HTTP-Method not supported", 404

@app.route('/co2/getRange/<string:start>', methods=['GET'])
def getCo2ByRangeStart(start):
    """
    Returns all Co2 emission values which are after the given start date.
    """
    if request.method == 'GET':
        try:
            session = co2DB.create_session()
            start_date = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
            co2Values = session.query(co2Model.Co2ForecastProxy).filter(co2Model.Co2ForecastProxy.timestamp>=start_date).all()
            co2Dict = [co2Value.toDict() for co2Value in co2Values]
            return json.dumps(co2Dict, cls=Encoder), 200
        except Exception as e:
            return str(e), 500
        finally:
            co2DB.close_session(session)
    return "HTTP-Method not supported", 404

@app.route('/co2/get/<string:date>', methods=['GET'])
def get_co2(date):
    """
    Returns the Co2 emission values for given timestamp day.
    """
    if request.method == 'GET':
        try:
            session = co2DB.create_session()
            date_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
            co2Value = session.query(co2Model.Co2ForecastProxy).filter_by(timestamp=date_date).first()
            return co2Value.toJson(), 200
        except Exception as e:
            return str(e), 500
        finally:
            co2DB.close_session(session)
    return "HTTP-Method not supported", 404

@app.route('/co2/getlatest', methods=['GET'])
def get_co2_latest():
    """
    Returns the co2 values for the most recent day.
    """
    if request.method == 'GET':
        try:
            session = co2DB.create_session()
            date = datetime.now().replace(hour=0, minute=0)
            if date == None:
                return "No data", 404
            co2Values = session.query(co2Model.Co2ForecastProxy).filter(co2Model.Co2ForecastProxy.timestamp >= date).all()
            if co2Values:
                co2Dict = [co2Value.toDict() for co2Value in co2Values]
                return json.dumps(co2Dict, cls=Encoder), 200
            else:
                return 'No Co2 values', 404
        except Exception as e:
            return str(e), 500
        finally:
            co2DB.close_session(session)
    return "HTTP-Method not supported", 404


##############################################
# getter-functions for gas boiler data #
##############################################

@app.route('/gasBoiler/getAll/<string:buildingName>', methods=['GET'])
def getAll_gasBoilerData(buildingName):
    """
    Returns all gas boiler data available in database for a given building name.
    """
    return getAllJson(gasBoilerDB, gasBoilerModel.GasBoiler)

@app.route('/gasBoiler/getRange/<string:buildingName>/<string:start>/<string:end>', methods=['GET'])
def getGasBoilerDataByRange(buildingName, start, end):
    """
    Returns all gas boiler data which are in the given time range for a given building name.
    """
    if request.method == 'GET':
        try:
            session = gasBoilerDB.create_session()
            start_date = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
            end_date = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")
            gasBoilerValues = session.query(gasBoilerModel.GasBoiler).filter(gasBoilerModel.GasBoiler.timestamp>=start_date, \
                gasBoilerModel.GasBoiler.timestamp<=end_date, gasBoilerModel.GasBoiler.buildingName==buildingName).all()
            gasBoilerDict = [gasBoilerValue.toDict() for gasBoilerValue in gasBoilerValues]
            return json.dumps(gasBoilerDict, cls=Encoder), 200
        except Exception as e:
            return str(e), 500
        finally:
            gasBoilerDB.close_session(session)
    return "HTTP-Method not supported", 404

@app.route('/gasBoiler/getRange/<string:buildingName>/<string:start>', methods=['GET'])
def getGasBoilerDataByRangeStart(buildingName, start):
    """
    Returns all gas boiler data which are after the given start date for a given building name.
    """
    if request.method == 'GET':
        try:
            session = gasBoilerDB.create_session()
            start_date = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
            gasBoilerValues = session.query(gasBoilerModel.GasBoiler).filter(gasBoilerModel.GasBoiler.timestamp>=start_date,\
                gasBoilerModel.GasBoiler.buildingName==buildingName).all()
            gasBoilerDict = [gasBoilerValue.toDict() for gasBoilerValue in gasBoilerValues]
            return json.dumps(gasBoilerDict, cls=Encoder), 200
        except Exception as e:
            return str(e), 500
        finally:
            gasBoilerDB.close_session(session)
    return "HTTP-Method not supported", 404

@app.route('/gasBoiler/get/<string:buildingName>/<string:date>', methods=['GET'])
def get_gasBoilerData(buildingName, date):
    """
    Returns the gas boiler data for given timestamp day.
    """
    if request.method == 'GET':
        try:
            session = gasBoilerDB.create_session()
            date_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
            gasBoilerValue = session.query(gasBoilerModel.GasBoiler).filter(gasBoilerModel.GasBoiler.timestamp==date_date,\
                gasBoilerModel.GasBoiler.buildingName==buildingName).first()
            return gasBoilerValue.toJson(), 200
        except Exception as e:
            return str(e), 500
        finally:
            gasBoilerDB.close_session(session)
    return "HTTP-Method not supported", 404

@app.route('/gasBoiler/getlatest/<string:buildingName>', methods=['GET'])
def get_gasBoilerData_latest(buildingName):
    """
    Returns the gas boiler data for the most recent day.
    """
    if request.method == 'GET':
        try:
            session = gasBoilerDB.create_session()
            date = datetime.now().replace(hour=0, minute=0)
            if date == None:
                return "No data", 404
            gasBoilerValues= session.query(gasBoilerModel.GasBoiler).filter(gasBoilerModel.GasBoiler.timestamp >= date\
                , gasBoilerModel.GasBoiler.buildingName==buildingName).all()
            if gasBoilerValues:
                gasBoilerDict = [gasBoilerValue.toDict() for gasBoilerValue in gasBoilerValues]
                return json.dumps(gasBoilerDict, cls=Encoder), 200
            else:
                return 'No gas boiler data', 404
        except Exception as e:
            return str(e), 500
        finally:
            gasBoilerDB.close_session(session)
    return "HTTP-Method not supported", 404



#############################################
# getter-functions for simulation forecasts #
#############################################

@app.route('/forecast/wind/get/<string:name>/', methods=['GET'])
def get_wind_sim_forecast(name):
    date = datetime.now()
    return get_wind_sim_forecast_date(name, date)

@app.route('/forecast/wind/get/<string:name>/<string:start>', methods=['GET'])
def get_wind_sim_forecast_date(name, start):
    return get_sim_forecast_date(entityModels.SimulationForecastWindTurbine, name, start)

@app.route('/forecast/wind/getAll/', methods=['GET'])
def get_wind_sim_forecast_all():
    date = datetime.now()
    return get_wind_sim_forecast_all_date(date)

@app.route('/forecast/wind/getAll/<string:start>', methods=['GET'])
def get_wind_sim_forecast_all_date(start):
    return get_sim_forecast_all_date(entityModels.SimulationForecastWindTurbine, start)

@app.route('/forecast/solar/get/<string:name>/', methods=['GET'])
def get_solar_sim_forecast(name):
    date = datetime.now()
    return get_solar_sim_forecast_date(name, date)

@app.route('/forecast/solar/get/<string:name>/<string:start>', methods=['GET'])
def get_solar_sim_forecast_date(name, start):
    return get_sim_forecast_date(entityModels.SimulationForecastSolarPanel, name, start)

@app.route('/forecast/solar/getAll/', methods=['GET'])
def get_solar_sim_forecast_all():
    date = datetime.now()
    return get_solar_sim_forecast_all_date(date)

@app.route('/forecast/solar/getAll/<string:start>', methods=['GET'])
def get_solar_sim_forecast_all_date(start):
    return get_sim_forecast_all_date(entityModels.SimulationForecastSolarPanel, start)

def get_sim_forecast_date(obj, name, start):
    '''
    Answers a http request for simulation forecast data of a generator specified by the object type and name.
    All simulation forecast data after the specified start date is taken into account.
    '''
    if request.method == 'GET':
        try:
            if isinstance(start, str):
                start_date = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
            else:
                start_date = start
            session = simDB.create_session()
            if obj == entityModels.SimulationForecastWindTurbine:
                sim_data = session.query(obj).filter(
                    obj.windturbine_name == name, 
                    obj.timestamp>=start_date).all()
            elif obj==entityModels.SimulationForecastSolarPanel:
                sim_data = session.query(obj).filter(
                    obj.solarpanel_name == name, 
                    obj.timestamp>=start_date).all()
            sim_data_dict = [data.toDict() for data in sim_data]
            return json.dumps(sim_data_dict, cls=Encoder), 200
        except Exception as e:
            return str(e), 500
        finally:
            simDB.close_session(session)
    return "HTTP-Method not supported", 404

def get_sim_forecast_all_date(obj, start):
    '''
    Answers a http request for simulation forecast data of all generator specified by the object type. 
    All simulation forecast data after the specified start date is taken into account.
    '''
    if request.method == 'GET':
        try:
            if isinstance(start, str):
                start_date = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
            else:
                start_date = start
            session = simDB.create_session()
            sim_data = session.query(obj).filter(
                obj.timestamp>=start_date).all()
            elementsDict = [element.toDict() for element in sim_data]
            return json.dumps(elementsDict, cls=Encoder), 200
            # summed_data ={}
            # for data in sim_data:
            #     if data.timestamp in summed_data:
            #         summed_data[data.timestamp] += data.supply
            #     else:
            #         summed_data[data.timestamp] = data.supply
            # response = []
            # for timestamp, supply in summed_data.items():
            #     response.append({"timestamp":timestamp, "supply":supply})
            # return json.dumps(response, cls=Encoder), 200
        except Exception as e:
            return str(e), 500
        finally:
            simDB.close_session(session)
    return "HTTP-Method not supported", 404

########################################
# getter-functions for simulation data #
########################################

@app.route('/total/current_sim_latest', methods=['GET'])
def get_total_current_simulation_latest():
    return current_simulation_latest(entityModels.SimulationTotalEnergy)

@app.route('/battery/current_sim_latest', methods=['GET'])
def get_battery_current_simulation_latest():
    return current_simulation_latest(entityModels.SimulationBattery)

@app.route('/windturbine/current_sim_latest', methods=['GET'])
def get_windturbine_current_simulation_latest():
    return current_simulation_latest(entityModels.SimulationWindTurbine)

@app.route('/solarpanel/current_sim_latest', methods=['GET'])
def get_solarpanel_current_simulation_latest():
    return current_simulation_latest(entityModels.SimulationSolarPanel)

@app.route('/building/current_sim_latest', methods=['GET'])
def get_building_current_simulation_latest():
    return current_simulation_latest(entityModels.SimulationBuilding)

def current_simulation_latest(model):
    '''
    Answers a http request for a given model with the latest values.
    '''
    if request.method == 'GET':
        try:
            session = entityDB.create_session()
            date = session.query(func.max(model.timestamp)).first()
            if date == None:
                return "No data", 404
            data_sim = session.query(model).filter_by(timestamp=date[0]).all()
            dataDict = [data.toDict() for data in data_sim]
            return json.dumps(dataDict, cls=Encoder), 200
        finally:
            priceDB.close_session(session)
    return "HTTP-Method not supported", 404

@app.route('/total/current_sim', methods=['GET'])
def get_total_current_simulation():
    return current_simulation(entityModels.SimulationTotalEnergy)

@app.route('/battery/current_sim', methods=['GET'])
def get_battery_current_simulation():
    return current_simulation(entityModels.SimulationBattery)

@app.route('/windturbine/current_sim', methods=['GET'])
def get_windturbine_current_simulation():
    return current_simulation(entityModels.SimulationWindTurbine)

@app.route('/solarpanel/current_sim', methods=['GET'])
def get_solarpanel_current_simulation():
    return current_simulation(entityModels.SimulationSolarPanel)

@app.route('/building/current_sim', methods=['GET'])
def get_building_current_simulation():
    return current_simulation(entityModels.SimulationBuilding)

def current_simulation(model):
    '''
    Answers a http request for a given model with the values of the last 24 hours.
    '''
    if request.method == 'GET':
        try:
            session = entityDB.create_session()
            date = session.query(func.max(model.timestamp)).first()
            if date == None:
                return "No data", 404
            data_sim = session.query(model) \
                .filter(model.timestamp > (date[0]-timedelta(days=1))) \
                .all()
            dataDict = [data.toDict() for data in data_sim]
            return json.dumps(dataDict, cls=Encoder), 200
        finally:
            entityDB.close_session(session)
    return "HTTP-Method not supported", 404

@app.route('/total/sim/<string:date>', methods=['GET'])
def get_total_simulation_by_date(date):
    return get_simulation_by_date(entityModels.SimulationTotalEnergy, date)

@app.route('/battery/sim/<string:date>', methods=['GET'])
def get_battery_simulation_by_date(date):
    return get_simulation_by_date(entityModels.SimulationBattery, date)

@app.route('/windturbine/sim/<string:date>', methods=['GET'])
def get_windturbine_simulation_by_date(date):
    return get_simulation_by_date(entityModels.SimulationWindTurbine, date)

@app.route('/solarpanel/sim/<string:date>', methods=['GET'])
def get_solarpanel_simulation_by_date(date):
    return get_simulation_by_date(entityModels.SimulationSolarPanel, date)

@app.route('/building/sim/<string:date>', methods=['GET'])
def get_building_simulation_by_date(date):
    return get_simulation_by_date(entityModels.SimulationBuilding, date)

def get_simulation_by_date(model, date_string):
    '''
    Answers a http request for a given model and date with all values for this day.
    '''
    if request.method == 'GET':
        try:
            session = entityDB.create_session()
            date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
            date = date.replace(hour=0, minute=0, second=0)
            data_sim = session.query(model) \
                .filter(model.timestamp >= date, model.timestamp < (date + timedelta(days=1))) \
                .all()
            if len(data_sim) == 0:
                return "No data for this day", 404
            dataDict = [data.toDict() for data in data_sim]
            return json.dumps(dataDict, cls=Encoder), 200
        finally:
            priceDB.close_session(session)
    return "HTTP-Method not supported", 404

######################################
# functionS for the simulation #
######################################

@app.route('/simulation/isStarted', methods=['GET'])
def is_simulation_started():
    '''
    Answers a http request whether a simulation is running.
    '''
    if request.method == 'GET':
        number_of_running_sims = get_number_of_running_simulations()
        state = (not (0 == number_of_running_sims))
        return json.dumps({"is_started":state}), 200
    return "HTTP-Method not supported", 404


@app.route('/simulation/start', methods=['POST'])
def start_sim():
    if request.method == 'POST':
        if get_number_of_running_simulations() == 0:
            r = requests.post(config.URL_SIMULATION_SERVICE + "/simulation/init")
            print("Simulate init", r)
            if r.status_code != 201:
                return "Simulate init error", r.status_code
            t = threading.Thread(target=start_sim_init_helper)
            t.start()
            return "Simulation started", 201
        else:
            return "Simulation is already running", 423
    return "HTTP-Method not supported", 404

def start_sim_init_helper():
    r = requests.post(config.URL_WEATHER_SERVICE + "/updateWeather")
    print("Update weather data", r)
    r = requests.post(config.URL_PRICE_SERVICE + "/updateprices")
    print("Update price data", r)
    r = requests.post(config.URL_SIMULATION_SERVICE + "/simulation/forecast")
    print("Simulate forecast", r)
    r = requests.post(config.URL_OPTIMIZER_SERVICE + "/optimizer/generateSchedule")
    print("Generate schedule", r)
    r = requests.post(config.URL_SIMULATION_SERVICE + "/simulation/nextHour")
    print("Simulate next hour", r)

####################################
# getter-function for the schedule #
####################################

@app.route('/optimizer/getSchedule/<string:date_string>', methods=['GET'])
def get_schedule(date_string):
    """
    Answers a http request for a schedule for a given day.
    """
    if request.method == 'GET':
        try:
            session = priceDB.create_session()
            date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
            date = date.replace(hour=0, minute=0, second=0)
            schedule = session.query(optimizerModel.Schedule).filter_by(date=date).first()
            return schedule.toJson(), 200
        except Exception as e:
            return str(e), 500
        finally:
            priceDB.close_session(session)
    return "HTTP-Method not supported", 404


####################
# helper-functions #
####################

def getAllJson(db, model):
    """
    This function queries all entities for a given model from the database and
    sends a json http response back to the client.
    """
    if request.method == 'GET':
        try:
            session = db.create_session()
            elements = db.getAll(session, model)
            elementsDict = [element.toDict() for element in elements]
            return json.dumps(elementsDict, cls=Encoder), 200
        except Exception as e:
            return str(e), 500
        finally: 
            db.close_session(session)
    return "HTTP-Method not supported", 404
    
def getByNameJson(model, name):
    """
    This function queries an entity specified by its name and model from the database and
    sends it as json http response back to the client.
    """
    if request.method == 'GET':
        try:
            session = entityDB.create_session()
            element = session.query(model).filter_by(name=name).first()
            if element:
                return element.toJson(), 200
            else:
                return "No such element", 404
        except Exception as e:
            return str(e), 500
        finally:
            entityDB.close_session(session)
    return "HTTP-Method not supported", 404


def get_number_of_running_simulations():
    """
    Returns the number of running simulations.
    If there is no error, it should be either 0 or 1.
    """

    try:
        session_entityDB = entityDB.create_session()
        # stop running simulations
        return session_entityDB.query(entityModels.Simulation).filter_by(running=True).count()
    finally:
        entityDB.close_session(session_entityDB)


if __name__ == '__main__':
    app.run(debug=True, port=5000) #run app in debug mode on port 5000
