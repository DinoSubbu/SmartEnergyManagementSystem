from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Text, String, Integer, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator
import json

Base = declarative_base()

class Float_List(TypeDecorator):

    impl = Text()

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

class Component_Dict(TypeDecorator):

    impl = Text()

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

class Battery(Base):
    __tablename__ = 'batteries'

    name = Column(String(100), primary_key=True)
    lat = Column(Text, nullable=False)
    long = Column(Text, nullable=False)
    batteryEfficiency = Column(Float, nullable=False)
    chargeUpperBound = Column(Float, nullable=False)
    dischargeUpperBound = Column(Float, nullable=False)
    energyUpperBound = Column(Float, nullable=False)
    selfDischargingRate = Column(Float, nullable=False)

    def __init__(self, name, lat, long, batteryEfficiency, chargeUpperBound, dischargeUpperBound, energyUpperBound, selfDischargingRate):
        self.name = name
        self.lat = lat
        self.long = long
        self.batteryEfficiency = batteryEfficiency
        self.chargeUpperBound = chargeUpperBound
        self.dischargeUpperBound = dischargeUpperBound
        self.energyUpperBound = energyUpperBound
        self.selfDischargingRate = selfDischargingRate

    def toDict(self):
        return {"name": self.name,
                "lat": self.lat,
                "long": self.long,
                "batteryEfficiency": self.batteryEfficiency,
                "chargeUpperBound": self.chargeUpperBound,
                "dischargeUpperBound": self.dischargeUpperBound,
                "energyUpperBound": self.energyUpperBound,
                "selfDischargingRate": self.selfDischargingRate}

    def toJson(self):
        return json.dumps(self.toDict())


class Building(Base):
    __tablename__= 'buildings'

    name = Column(String(100), primary_key=True)
    lat = Column(Text, nullable=False)
    long = Column(Text, nullable=False)
    thermalResistance = Column(Float, nullable=False)
    heatCapacityAirIndoor = Column(Float, nullable=False)
    historicalData = Column(Float_List(), nullable=False)
    components = relationship("Component", lazy="joined")

    def __init__(self, name, lat, long, mathematicalModel, historicalData):
        self.name = name
        self.lat = lat
        self.long = long
        self.thermalResistance = mathematicalModel['thermalResistance']
        self.heatCapacityAirIndoor = mathematicalModel['heatCapacityAirIndoor']
        self.historicalData = historicalData

    def toDict(self):
        return {"name": self.name,
                "lat": self.lat,
                "long": self.long,
                "thermalResistance" : self.thermalResistance,
                "heatCapacityAirIndoor" : self.heatCapacityAirIndoor,
                "historicalData": self.historicalData,
                "components": [comp.toDict() for comp in self.components]}

    def toJson(self):
        return json.dumps(self.toDict())




class Component(Base):
    __tablename__ = 'componets'

    name = Column(String(100), primary_key=True)
    building_name = Column(String(100), ForeignKey('buildings.name'), primary_key=True)
    est = Column(Integer, nullable=False)
    let = Column(Integer, nullable=False)
    e = Column(Float, nullable=False)
    lot = Column(Integer, nullable=False)

    def __init__(self, name, est, let, e, lot):
        self.name = name
        self.est = est
        self.let = let
        self.e = e
        self.lot = lot

    def toDict(self):
        return {"name": self.name,
                "est": self.est,
                "let": self.let,
                "e": self.e,
                "lot": self.lot}

    def toJson(self):
        return json.dumps(self.toDict())

class SolarPanel(Base):
    __tablename__ = 'solarpanels'

    name = Column(String(100), primary_key=True)
    lat = Column(Text, nullable=False)
    long = Column(Text, nullable=False)
    powerCoefficient = Column(Float, nullable=False)
    area = Column(Float, nullable=False)
    angleOfModule = Column(Float, nullable=False)

    def __init__(self, name, lat, long, powerCoefficient, area, angleOfModule):
        self.name = name
        self.lat = lat
        self.long = long
        self.powerCoefficient = powerCoefficient
        self.area = area
        self.angleOfModule = angleOfModule

    def toDict(self):
        return {"name": self.name,
                "lat": self.lat,
                "long": self.long,
                "powerCoefficient": self.powerCoefficient,
                "area": self.area,
                "angleOfModule": self.angleOfModule}

    def toJson(self):
        return json.dumps(self.toDict())

class WindTurbine(Base):
    __tablename__ = 'windturbines'

    name = Column(String(100), primary_key=True)
    lat = Column(Text, nullable=False)
    long = Column(Text, nullable=False)
    powerCoefficient = Column(Float, nullable=False)
    radius = Column(Float, nullable=False)

    def __init__(self, name, lat, long, powerCoefficient, radius):
        self.name = name
        self.lat = lat
        self.long = long
        self.powerCoefficient = powerCoefficient
        self.radius = radius

    def toDict(self):
        return {"name": self.name,
                "lat": self.lat,
                "long": self.long,
                "powerCoefficient": self.powerCoefficient,
                "radius": self.radius}

    def toJson(self):
        return json.dumps(self.toDict())



class SimulationBuilding(Base):
    __tablename__ = 'sim_buildings'

    building_name = Column(String(100), ForeignKey('buildings.name'), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    demand = Column(Float, nullable=False)
    components = Column(Component_Dict(), nullable=False)

    def __init__(self, building_name, timestamp, demand, components):
        self.building_name = building_name
        self.timestamp = timestamp
        self.demand = demand
        self.components = components

    def toDict(self):
        return {"building_name": self.building_name,
                "timestamp": self.timestamp,
                "demand": self.demand,
                "components": self.components}

    def toJson(self):
        return json.dumps(self.toDict())

class SimulationSolarPanel(Base):
    __tablename__ = 'sim_solarpanels'

    solarpanel_name = Column(String(100), ForeignKey('solarpanels.name'), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    supply = Column(Float, nullable=False)

    def __init__(self, solarpanel_name, timestamp, supply):
        self.solarpanel_name = solarpanel_name
        self.timestamp = timestamp
        self.supply = supply

    def toDict(self):
        return {"solarpanel_name": self.solarpanel_name,
                "timestamp": self.timestamp,
                "supply": self.supply}

    def toJson(self):
        return json.dumps(self.toDict())


class SimulationWindTurbine(Base):
    __tablename__ = 'sim_windturbines'

    windturbine_name = Column(String(100), ForeignKey('windturbines.name'), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    supply = Column(Float, nullable=False)

    def __init__(self, windturbine_name, timestamp, supply):
        self.windturbine_name = windturbine_name
        self.timestamp = timestamp
        self.supply = supply

    def toDict(self):
        return {"windturbine_name": self.windturbine_name,
                "timestamp": self.timestamp,
                "supply": self.supply}

    def toJson(self):
        return json.dumps(self.toDict())

class SimulationBattery(Base):
    __tablename__ = 'sim_batteries'

    battery_name = Column(String(100), ForeignKey('batteries.name'), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    currentEnergy = Column(Float, nullable=False)
    currentChargingRate = Column(Float, nullable=False)
    energyUpperBound = Column(Float, nullable=False)

    def __init__(self, battery_name, timestamp, currentEnergy, currentChargingRate, energyUpperBound):
        self.battery_name = battery_name
        self.timestamp = timestamp
        self.currentEnergy = currentEnergy
        self.currentChargingRate = currentChargingRate
        self.energyUpperBound = energyUpperBound

    def toDict(self):
        return {"battery_name": self.battery_name,
                "timestamp": self.timestamp,
                "currentEnergy": self.currentEnergy,
                "currentChargingRate": self.currentChargingRate,
                "energyUpperBound": self.energyUpperBound}

    def toJson(self):
        return json.dumps(self.toDict())

class SimulationTotalEnergy(Base):
    __tablename__ = 'sim_total_energy'

    timestamp = Column(DateTime, primary_key=True)
    energy = Column(Float, nullable=False)

    def __init__(self, timestamp, energy):
        self.timestamp = timestamp
        self.energy = energy

    def toDict(self):
        return {"timestamp": self.timestamp,
                "energy": self.energy}

    def toJson(self):
        return json.dumps(self.toDict())

class SimulationForecastSolarPanel(Base):
    __tablename__ = 'sim_forecast_solarpanels'

    solarpanel_name = Column(String(100), ForeignKey('solarpanels.name'), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    supply = Column(Float, nullable=False)

    def __init__(self, solarpanel_name, timestamp, supply):
        self.solarpanel_name = solarpanel_name
        self.timestamp = timestamp
        self.supply = supply

    def toDict(self):
        return {"solarpanel_name": self.solarpanel_name,
                "timestamp": self.timestamp,
                "supply": self.supply}

    def toJson(self):
        return json.dumps(self.toDict())

class SimulationForecastWindTurbine(Base):
    __tablename__ = 'sim_forecast_windturbines'

    windturbine_name = Column(String(100), ForeignKey('windturbines.name'), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    supply = Column(Float, nullable=False)

    def __init__(self, windturbine_name, timestamp, supply):
        self.windturbine_name = windturbine_name
        self.timestamp = timestamp
        self.supply = supply
    
    def toDict(self):
        return {"windturbine_name": self.windturbine_name,
                "timestamp": self.timestamp,
                "supply": self.supply}

    def toJson(self):
        return json.dumps(self.toDict())

class Simulation(Base):
    __tablename__ = 'simulations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    starting_time = Column(DateTime, nullable=False)
    running = Column(Boolean, nullable=False)

    def __init__(self, starting_time, running):
        self.id
        self.starting_time = starting_time
        self.running = running
    
    def toDict(self):
        return {"id": self.id,
                "starting_time": self.timestamp,
                "running": self.supply}

    def toJson(self):
        return json.dumps(self.toDict())

