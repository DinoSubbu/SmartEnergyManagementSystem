from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Text, Integer, Float, ForeignKey, DateTime, UniqueConstraint, String

Base = declarative_base()

class GasBoiler(Base):
    __tablename__ = 'gasBoiler'

    timestamp = Column(DateTime, primary_key=True)
    buildingName = Column(String(30), primary_key=True)
    latitude = Column(Float, primary_key=True)
    longitude = Column(Float, primary_key=True)
    powerDHW = Column(Float)
    powerSH = Column(Float)
    powerOutput = Column(Float)
    fuelInput = Column(Float)


    def __init__(self, timestamp, buildingName, latitude, longitude, powerDHW, powerSH, powerOutput, fuelInput ):
        self.timestamp = timestamp
        self.buildingName = buildingName
        self.latitude = latitude
        self.longitude = longitude
        self.powerDHW = powerDHW
        self.powerSH = powerSH
        self.powerOutput = powerOutput
        self.fuelInput = fuelInput

    def toDict(self):
        return {
                "timestamp": self.timestamp,
                "buildingName": self.buildingName,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "hotWaterPower" : self.powerDHW,
                "spaceHeatingPower" : self.powerSH,
                "powerOutputBoiler": self.powerOutput,
                "fuelInputBoiler": self.fuelInput
                }
                    
    def toJson(self):
        return f'''{{
                "timestamp": {self.timestamp},
                "buildingName": {self.buildingName},
                "latitude": {self.latitude},
                "longitude": {self.longitude},
                "hotWaterPower" : {self.powerDHW},
                "spaceHeatingPower" : {self.powerSH},
		        "powerOutputBoiler": {self.powerOutput},
		        "fuelInputBoiler": {self.fuelInput}
                }}'''

