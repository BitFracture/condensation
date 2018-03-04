"""A collection of queries to enteract with the database"""
from schema import User, File

def getUser(session, certificate):
    """gets a user by id"""
    user = session.query(User).filter(User.certificate == certificate)
    if user:
        return user.one_or_none()

def getFile(session, user_certificate, name):
    """gets a file by user and name"""
    f = session.query(File).filter(File.user_certificate == user_certificate).filter(File.name == name)
    if f:
        return f.one_or_none()
