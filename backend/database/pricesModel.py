from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Float, DateTime
import json
from util.json_encoder import Encoder
import datetime

Base = declarative_base()

class PriceForecast(Base):
    __tablename__ = 'priceForecast'

    timestamp = Column(DateTime, primary_key=True)
    retrivalTime = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)


    def __init__(self, timestamp, retrivalTime, price):
        self.timestamp = timestamp
        self.retrivalTime = retrivalTime
        self.price = price

    def toDict(self):
        return {
                "timestamp": self.timestamp,
                "retrivalTime": self.retrivalTime,
                "price": self.price
                }

    def toJson(self):
        return json.dumps(self.toDict(), cls=Encoder)
