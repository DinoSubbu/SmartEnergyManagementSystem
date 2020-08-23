from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Text, String, Float, DateTime, Boolean
from sqlalchemy.types import TypeDecorator
import json
from util.json_encoder import Encoder


Base = declarative_base()

class Schedule_Dict(TypeDecorator):

    impl = Text()

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

class Schedule(Base):
    __tablename__ = 'schedules'

    date = Column(DateTime, primary_key=True)
    obj_function = Column(String(100), primary_key=True)
    obj_value = Column(Float, nullable=False)
    schedule = Column(Schedule_Dict(), nullable=False)

    def __init__(self, date, obj_function, obj_value, schedule):
        self.date = date
        self.obj_function = obj_function
        self.obj_value = obj_value
        self.schedule = schedule

    def toDict(self):
        return {"date": self.date,
                "obj_function": self.obj_function,
                "obj_value": self.obj_value,
                "schedule": self.schedule}

    def toJson(self):
        return json.dumps(self.toDict(), cls=Encoder)

class Objective(Base):
    __tablename__ = 'objectives'

    date = Column(DateTime, primary_key=True)
    obj_function = Column(Text, nullable=False)

    def __init__(self, date, obj_function):
        self.date = date
        self.obj_function = obj_function

    def toDict(self):
        return {"date": self.date,
                "obj_function": self.obj_function,
                }

    def toJson(self):
        return json.dumps(self.toDict(), cls=Encoder)
