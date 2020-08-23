from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Text, Integer, Float, ForeignKey, DateTime, UniqueConstraint, String

Base = declarative_base()

class SpaceHeating(Base):
    __tablename__ = 'spaceHeating'

    timestamp = Column(DateTime, primary_key=True)
    buildingName = Column(String(30), primary_key=True)
    latitude = Column(Float, primary_key=True)
    longitude = Column(Float, primary_key=True)
    temperatureIndoor = Column(Float)
    temperatureOutdoor = Column(Float)
    powerSH = Column(Float)


    def __init__(self, timestamp, buildingName, latitude, longitude, temperatureIndoor, temperatureOutdoor, powerSH):
        self.timestamp = timestamp
        self.buildingName = buildingName
        self.latitude = latitude
        self.longitude = longitude
        self.temperatureIndoor = temperatureIndoor
        self.temperatureOutdoor = temperatureOutdoor
        self.powerSH = powerSH

    def toDict(self):
            return {
                    "timestamp": self.timestamp,
                    "buildingName": self.buildingName,
                    "latitude": self.latitude,
                    "longitude": self.longitude,
                    "temperatureIndoor": self.temperatureIndoor,
                    "temperatureOutdoor": self.temperatureOutdoor,
                    "powerSH": self.powerSH
                    }
                    
    def toJson(self):
        return f'''{{
                "timestamp": {self.timestamp},
                "buildingName": {self.buildingName},
                "latitude": {self.latitude},
                "longitude": {self.longitude},
                "temperatureIndoor": {self.temperatureIndoor},
		        "temperatureOutdoor": {self.temperatureOutdoor},
		        "powerSH": {self.powerSH}
                }}'''

