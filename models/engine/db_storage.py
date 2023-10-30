#!/usr/bin/python3
""" MySQL database storage"""


import models
from models.user import User
from models.locationreminder import LocationReminder
from models.todo import Todo
from models.location import Location
from models.basemodel import BaseModel, Base
from os import getenv
import sqlalchemy
from contextlib import contextmanager
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
classes = {"User": User, "Location": Location, "Todo": Todo,
        "LocationReminder": LocationReminder}


class DBStorage:
    """ Interacts with the MySQL database"""
    __engine = None
    __session = None

    def __init__(self):
        """ Instantiate the database storage"""
        '''
        USER = getenv('USER')
        PWD = getenv('PWD')
        HOST = getenv('HOST')
        DB = getenv('DB')
        if HOST is not None:
            self.__engine = create_engine('mysql+mysqldb://{}:{}@{}/{}'.format(
                USER, PWD, HOST, DB))
        else:
            # uncommemt to male use of mySQL
            # self.__engine = create_engine('mysql+mysqldb://admin:GeoAlertAdmin@localhost/GeoAlert')
        '''
        self.__engine = create_engine('sqlite:///:GEOALERT.db', echo=True)
        Base.metadata.create_all(self.__engine)
        Session = sessionmaker(bind=self.__engine)
        self.__session = Session()

    @contextmanager
    def session_scope(self):
        """Provides a transactional scope around a series of operations"""
        session = self.__session()
        try:
            yield session  # send d session for work
            session.commit()  # commit everything to database
        except Exception as e:
            session.rollback()  # Return to the last transaction<F11>
            logger.exception("An error occurred during the transaction.")
            raise e
        finally:
            session.close()
            session.exit()

    def all(self, cls=None):
        """ Query the database for all instamces of the cls
        if provided or if not, it'll bring all the data on the database
        """
        new_dict = {}
        for clss in classes:
            if cls is None or cls is classes[clss] or cls is clss:
                objs = self.__session.query(classes[clss]).all()

                for obj in objs:
                    if obj.__class__.__name__ == 'User':
                        key = obj.__class__.__name__ + '.' + obj.username
                    else:
                        key = obj.__class__.__name__ + '.' + obj.id
                    new_dict[key] = obj
        return (new_dict)

    def new(self, obj):
        """Adds new object to the current database session"""
        self.__session.add(obj)

    def save(self):
        """Commit all changes to the database"""
        self.__session.commit()

    def delete(self, obj=None):
        """Deletes an obj instance from the database if obj is not None"""
        if obj is not None:
            self.__session.delete(obj)

    def clear(self, obj):
        '''Deletes all entries in database
        should only be ysed on tasks'''
        objs = self.__session.query(Tasks).all()
        for i in objs:
            self.__session.delete(i)
        self.__session.commit()

    @staticmethod
    def get(cls, unit=None):
        """Returs the object based on it's id.
        will later need to change the id to something that can be easy to implement"""
        try:
            if cls not in classes.values():
                return None
            all_cls = models.storage.all(cls)
            if unit is None:
                return all_cls #[cls]
            else:
                if cls == eval('User'):
                    for value in all_cls.values():
                        if (value.username == unit):
                            return value
                for value in all_cls.values():
                    if (value.id == unit):
                        return value
        except Exception as e:
            raise ValueError
                      

    def count(self, cls=None):
        """Count the number of objects in the storage"""
        all_classes  = classes.values()
        count = 0

        if not cls:
 
            for clss in all_classes:
                count += len(models.storage.all(clss).values())
        else:
            count += len(models.storage.all(cls).values())
        return count

    def close(self):
        """Closes the current database session"""
        if self.__session is not None:
            self.__session.close()
    def reload(self):
        '''Reloads the database'''
        pass

   