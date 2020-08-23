from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Text, Integer, Float, ForeignKey, DateTime, UniqueConstraint, String

Base = declarative_base()

class HotWater(Base):
    __tablename__ = 'hotWater'

    timestamp = Column(DateTime, primary_key=True)
    buildingName = Column(String(30),primary_key=True)
    latitude = Column(Float, primary_key=True)
    longitude = Column(Float, primary_key=True)
    powerDHW = Column(Float)


    def __init__(self, timestamp, buildingName, latitude, longitude, powerDHW):
        self.timestamp = timestamp
        self.buildingName = buildingName
        self.latitude = latitude
        self.longitude = longitude
        self.powerDHW = powerDHW

    def toDict(self):
        return {
                "timestamp": self.timestamp,
                "buildingName": self.buildingName,
                "latitude": self.latitude,
                "longitude": self.longitude,
		        "powerDHW": self.powerDHW
                }

    def toJson(self):
        return f'''{{
                "timestamp": {self.timestamp},
                "buildingName": {self.buildingName},
                "latitude": {self.latitude},
                "longitude": {self.longitude},
		        "powerDHW": {self.powerDHW}
                }}'''

