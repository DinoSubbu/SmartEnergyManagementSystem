from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InvalidRequestError, IntegrityError
import database.models as dbmodels
from database.models import Battery, Building, Component, SolarPanel, WindTurbine


class SessionException(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

class MariaDB_handler():

    def __init__(self, user, password, host, port, database):
        connect_string = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
        self.engine = create_engine(connect_string, pool_pre_ping=True)


    def create_session(self):
        # expire_on_commit: database objects can be used after the session is closed
        Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        return Session()

    def close_session(self, session):
        if session != None:
            session.close()


    def commitOrRollback(self, session):
        if session != None:
            if session.dirty:
                try:
                    session.commit()
                except Exception as e:
                    print(e)
                    session.rollback()
                
    def addElementToDatabase(self, session, element):
        if session != None:
            session.add(element)
            try:
                session.commit()
            except InvalidRequestError:
                session.rollback()
            except IntegrityError as dup:
                session.rollback()
                raise dup
        else:
            raise SessionException("You have to create a session before you add elements to the database.")

    def deleteElementFromDatabase(self, session, element):
        if session != None:
            session.delete(element)
            try:
                session.commit()
            except InvalidRequestError:
                session.rollback()
        else:
            raise SessionException("You have to create a session before you add elements to the database.")
        
    def addListOfElementsToDatabase(self, session, listOfElements):
        if session != None:
            for element in listOfElements:
                session.add(element)
            try:
                session.commit()
            except InvalidRequestError:
                session.rollback()
        else:
            raise SessionException("You have to create a session before you add elements to the database.")

    def getAll(self, session, model):
        return session.query(model).all()

    def createTables(self, base):
        '''Creates the tables for the given model base, if they do not exist already '''
        base.metadata.create_all(self.engine)


if __name__ == "__main__":
    USER = 'myusr'
    PASSWORD = 'myusrpass'
    HOST = 'localhost'
    PORT = '3306'
    DATABASE = 'mydb'

    mdb = MariaDB_handler(USER, PASSWORD, HOST, PORT, DATABASE)

    bat = Battery('name', '1', '2', 1.0, 1.0, 1.0, 2.0, 0.5)
    building = Building("building", "1000", "12", "[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]")
    comp = Component("comp", 2, 8, 1.8, 2)
    solar = SolarPanel("solar1", "1000", "2000", 0.9, 5, 1.4)
    wind = WindTurbine("wind1", "1234", "4523", 0.4, 3)
    multiple_elements = [solar, wind]
    building.components.append(comp)

    mdb.createTables(dbmodels.Base)

    mdb.create_session()

    mdb.addElementToDatabase(bat)
    mdb.addElementToDatabase(building)

    mdb.addListOfElementsToDatabase(multiple_elements)

    mdb.close_session()