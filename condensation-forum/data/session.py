from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from schema import User
from contextlib import contextmanager
"""Abstracts the data layer of the condensation forum.

Classes:
    SessionManager -- Opens up a lazily evaluating connection to a provided datavase.
"""

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
            

sessionMgr = SessionManager("postgres","password","localhost", debug=True)
