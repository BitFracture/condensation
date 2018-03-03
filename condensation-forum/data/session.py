from sqlalchemy import create_engine
"""Abstracts the data layer of the condensation forum.

Classes:
    Session -- Opens up a lazily evaluating connection to a provided datavase.
"""

class Session:
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

    def _buildConnectionString(self, user, password, endpoint):
        """Builds a connection string"""
        return "postgresql://%s:%s@%s:5432/postgres" % (user, password, endpoint)

        


