"""A collection of queries to enteract with the database"""
from .schema import User, File, Thread, Comment

def extractOutput(queryResults):
    """convenience function to extract results from active query object"""
    return [x.toDict() if x else None for x in queryResults]

def getThreadsByCommentTime(dbSession):
    """get all threads ordered by the time they were last commented"""
    threads = dbSession.query(Thread).order_by(Thread.time_last_reply)
    if threads:
        return threads.all()
    return None

def getUser(dbSession, certificate):
    """gets a user by id"""
    user = dbSession.query(User).filter(User.certificate == certificate)
    if user:
        return user.one_or_none()
    return None

def getUserDeep(dbSession, certificate):
    """gets a user by id"""
    user = dbSession.query(User).filter(User.certificate == certificate).enable_eagerloads(True)
    if user:
        return user.one_or_none()
    return None



def getFileById(dbSession, fid):
    """gets a file by user and id"""
    f = dbSession.query(File).filter(File.id == fid)
    if f:
        return f.one_or_none()
    return None

def getFileByName(dbSession, user_certificate, name):
    """gets a file by user and id"""
    f = dbSession.query(File).filter(File.user_certificate == user_certificate).filter(File.name == name)
    if f:
        return f.one_or_none()
    return None

def getFilesByUser(dbSession, user_certificate):
    """gets a file by user and id"""
    f = dbSession.query(File).filter(File.user_certificate == user_certificate)
    if f:
        return f.all()
    return None



def getThreadsByUser(dbSession, user_certificate):
    """gets all threads associated with a user"""
    threads = dbSession.query(Thread).filter(Thread.user_certificate == user_certificate)
    if threads:
        return threads.all_or_none()
    return None

def getThreadById(dbSession, tid):
    """gets all threads associated with a user"""
    thread = dbSession.query(Thread).filter(Thread.id == tid)
    if thread:
        return thread.one_or_none()
    return None

def getCommentById(dbSession, cid):
    """gets all threads associated with a user"""
    comment = dbSession.query(Comment).filter(Comment.id == cid)
    if comment:
        return comment.one_or_none()
    return None

