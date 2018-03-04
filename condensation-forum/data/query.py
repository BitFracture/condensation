"""A collection of queries to enteract with the database"""
from schema import User

def getUser(session, certificate):
    """gets a user by id"""
    user = session.query(User).filter(User.certificate == certificate)
    if user:
        return user.one()
    return None
