from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from schema import User
from contextlib import contextmanager
"""Abstracts the data layer of the condensation forum.

Classes:
    SessionManager -- Opens up a lazily evaluating connection to a provided datavase.
    Singleton -- Canned Singleton solution from stack overflow
"""
def singleton(cls):
    """ decorator for a class to make a singleton out of it 
    
    Adopted by Collin from
    http://code.activestate.com/recipes/578103-singleton-parameter-based/
    """
    classInstance = None

    def getInstance(*args, **kwargs):
        """ creating or just return the one and only class instance.
            The singleton depends on the parameters used in __init__ """
        nonlocal classInstance
        if not classInstance:
            classInstance = cls(*args, **kwargs)
            return classInstance
        raise ArgumentError
    return getInstance


@singleton
class SessionManager:
    """Opens up a session with our ORM and executes transactions lazily.

    Assumes we are connecting to a postgresql database named postgres, on the
    standard postgres port 5432.
    """

    def __init__(self, user, password, endpoint, debug = False):
        """ Opens up a handle to a future session with the database.

        Does not establish connection until the first transaction is required
        Parameters:
            user -- the desired username
            password -- the desired password
            endpoint -- the endpoint of the database
            debug -- defaults false, echos the output of all database
                     transactions to stdout
        """
        self.engine = create_engine(self._buildConnectionString(user, password, endpoint), echo = debug)
        self.sessionFactory = sessionmaker(bind=self.engine)


    def _buildConnectionString(self, user, password, endpoint):
        """Builds a connection string"""
        return "postgresql://%s:%s@%s:5432/postgres" % (user, password, endpoint)

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.sessionFactory()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
            

