"""A collection of queries to enteract with the database"""
from schema import User, File, Thread

def getUser(session, certificate):
    """gets a user by id"""
    user = session.query(User).filter(User.certificate == certificate)
    if user:
        return user.one_or_none()
    return None

def getUserDeep(session, certificate):
    """gets a user by id"""
    user = session.query(User).filter(User.certificate == certificate).enable_eagerloads(True)
    if user:
        return user.one_or_none()
    return None



def getFileById(session, fid):
    """gets a file by user and id"""
    f = session.query(File).filter(File.id == fid)
    if f:
        return f.one_or_none()
    return None

def getFileByName(session, user_certificate, name):
    """gets a file by user and id"""
    f = session.query(File).filter(File.user_certificate == user_certificate).filter(File.name == name)
    if f:
        return f.one_or_none()
    return None

def getFilesByUser(session, user_certificate):
    """gets a file by user and id"""
    f = session.query(File).filter(File.user_certificate == user_certificate)
    if f:
        return f.all()
    return None



def getThreadsByUser(session, user_certificate):
    """gets all threads associated with a user"""
    threads = session.query(Thread).filter(Thread.user_certificate == user_certificate)
    if threads:
        return threads.all_or_none()
    return None

def getThreadById(session, tid):
    """gets all threads associated with a user"""
    thread = session.query(Thread).filter(Thread.id == tid)
    if thread:
        return thread.one_or_none()
    return None

