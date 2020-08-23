from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Text, Integer, Float, ForeignKey, DateTime, UniqueConstraint, String

Base = declarative_base()

class WeatherCurrent(Base):
    __tablename__ = 'weatherCurrent'

    lat = Column(String(30), primary_key=True)
    long = Column(String(30), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    temp = Column(Float)
    windSpeed = Column(Float)
    pressure = Column(Float)
    relativeHumidity = Column(Float)
    s_horizontal = Column(Float)


    def __init__(self, lat, long, timestamp, temp, windSpeed, pressure, relativeHumidity, s_horizontal):
        self.lat = lat
        self.long = long
        self.timestamp = timestamp
        self.temp = temp
        self.windSpeed = windSpeed
        self.pressure = pressure
        self.relativeHumidity = relativeHumidity
        self.s_horizontal = s_horizontal

    def toJson(self):
        return f'''{{
                "lat": "{self.lat}",
                "long": "{self.long}",
                "timestamp": {self.timestamp},
                "temp": {self.temp},
                "windSpeed": {self.windSpeed},
                "pressure": {self.pressure},
                "relativeHumidity": {self.relativeHumidity},
                "s_horizontal": {self.s_horizontal}
                }}'''

class WeatherForecast(Base):
    __tablename__ = 'weatherForecast'
    
    lat = Column(String(30), primary_key=True)
    long = Column(String(30), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    temp = Column(Float)
    windSpeed = Column(Float)
    pressure = Column(Float)
    relativeHumidity = Column(Float)
    s_horizontal = Column(Float)


    def __init__(self, lat, long, timestamp, temp, windSpeed, pressure, relativeHumidity, s_horizontal):
        self.lat = lat
        self.long = long
        self.timestamp = timestamp
        self.temp = temp
        self.windSpeed = windSpeed
        self.pressure = pressure
        self.relativeHumidity = relativeHumidity
        self.s_horizontal = s_horizontal

    def toJson(self):
        return f'''{{
                "lat": "{self.lat}",
                "long": "{self.long}",
                "timestamp": {self.timestamp},
                "temp": {self.temp},
                "windSpeed": {self.windSpeed},
                "pressure": {self.pressure},
                "relativeHumidity": {self.relativeHumidity},
                "s_horizontal": {self.s_horizontal}
                }}'''