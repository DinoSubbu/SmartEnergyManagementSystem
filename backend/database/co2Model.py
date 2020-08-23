from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Text, Integer, Float, ForeignKey, DateTime, UniqueConstraint, String

Base = declarative_base()

class Co2ForecastProxy(Base):
    __tablename__ = 'co2ForecastProxy'

    timestamp = Column(DateTime, primary_key=True)
    carbonIntensity = Column(Float)


    def __init__(self, timestamp, carbonIntensity):
        self.timestamp = timestamp
        self.carbonIntensity = carbonIntensity

    def toDict(self):
            return {
                    "timestamp": self.timestamp,
                    "carbonIntensity": self.carbonIntensity
                    }

    def toJson(self):
        return f'''{{
                "timestamp": {self.timestamp},
		        "carbonIntensity": {self.carbonIntensity}
                }}'''

