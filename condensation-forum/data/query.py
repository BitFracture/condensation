"""A collection of queries to enteract with the database"""
import sys
from .schema import User, File, Thread, Comment

def extractOutput(queryResults):
    """convenience function to extract results from active query object"""
    if not queryResults:
        return None
    try:
        return [x.toDict() if x else None for x in queryResults]
    except TypeError:
        return queryResults.toDict()
    return None

def getThreadsByCommentTime(dbSession):
    """get all threads ordered by the time they were last commented"""
    threads = dbSession.query(Thread).order_by(Thread.time_last_reply.desc())
    if threads:
        return threads.all()
    return None

def getUser(dbSession, uid):
    """gets a user by id"""
    user = dbSession.query(User).filter(User.id == uid)
    if user:
        return user.one_or_none()
    return None

def getUserDeep(dbSession, uid):
    """gets a user by id"""
    user = dbSession.query(User).filter(User.id == uid).enable_eagerloads(True)
    if user:
        return user.one_or_none()
    return None



def getFileById(dbSession, fid):
    """gets a file by user and id"""
    f = dbSession.query(File).filter(File.id == fid)
    if f:
        return f.one_or_none()
    return None

def getFileByName(dbSession, user_id, name):
    """gets a file by user and id"""
    f = dbSession.query(File).filter(File.user_id == user_id).filter(File.name == name)
    if f:
        return f.one_or_none()
    return None

def getFilesByUser(dbSession, user_id):
    """gets a file by user and id"""
    f = dbSession.query(File).filter(File.user_id == user_id)
    if f:
        return f.all()
    return None


def getThreadsByUser(dbSession, user_id):
    """gets all threads associated with a user"""
    threads = dbSession.query(Thread).filter(Thread.user_id == user_id)
    if threads:
        return threads.all_or_none()
    return None

def getThreadById(dbSession, tid):
    """gets all threads associated with a user"""
    thread = dbSession.query(Thread).filter(Thread.id == tid)
    if thread:
        return thread.one_or_none()
    return None

def getCommentsByThread(dbSession, tid):
    """gets all comments associated with a thread, ordered by time"""
    comments = dbSession.query(Comment).filter(Comment.thread_id == tid).order_by(Comment.time_created.desc())
    if comments:
        return comments.all()
    return None

def getCommentById(dbSession, cid):
    """gets a specific comment"""
    comment = dbSession.query(Comment).filter(Comment.id == cid)
    if comment:
        return comment.one_or_none()
    return None

