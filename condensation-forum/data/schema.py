"""The schema for the condensation application data layer.

There are several attributes and several miscelaneous constraints.

There is a brief synopsis for each entity in the documentation, however
for up to date a specific details about constraints read the code """
    
from datetime import datetime
from dateutil import tz
from sqlalchemy import (
        Table, 
        Column, 
        Integer, 
        String, 
        DateTime, 
        Text, 
        ForeignKey, 
        ForeignKeyConstraint, 
        CheckConstraint, 
        UniqueConstraint, 
        event)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property



#this is a collection of the sql alchemy metadata for the schema
_Base = declarative_base()

#m to n tables 
attachments_thread = Table ( "attachments_thread",
        _Base.metadata,
        Column("file_id", ForeignKey("files.id"), primary_key=True),
        Column("thread_id", ForeignKey("threads.id"), primary_key=True))

attachments_comment = Table ( "attachments_comment",
        _Base.metadata,
        Column("file_id", ForeignKey("files.id"), primary_key=True),
        Column("comment_id", ForeignKey("comments.id"), primary_key=True))

def _localize(time):
    """private method for relocalizing
    
    This is a bit of a hack and only works for things in our local time zone"""
    aware =  time.replace(tzinfo = tz.tzutc())
    return aware.astimezone(tz.tzlocal())
    



class User(_Base):
    """ A user on the site.

    Attributes:
        - certificate (pk): the google authentication id for the user
        - name: the display name for the user
        - uploads: file uploads
        - threads: the threads a user has created
        - comments: the comments the user has posted"""

    __tablename__ = "users"
    
    certificate = Column(
            String(21), 
            CheckConstraint("length(certificate) = 21"), 
            primary_key=True)

    name = Column(
            String(60), 
            CheckConstraint("length(name) > 0"), 
            nullable=False)

    uploads = relationship(
            "File", 
            cascade="all, delete-orphan", 
            back_populates="user")

    threads = relationship(
            "Thread", 
            cascade="all, delete-orphan", 
            back_populates="user")

    comments = relationship(
            "Comment", 
            cascade="all, delete-orphan", 
            back_populates="user")

    def toDict(self):
        """returns dict of primary attributes"""
        out = {}
        out["certificate"] = self.certificate
        out["name"] = self.name
        return out


class File(_Base):
    """A file upload from a user.

    filenames must be unique to each user
    
    Attributes:
        - id (pk): the generated id for the file
        - user: the user that generated the file
        - user_certificate (fk): their google id
        - name: the symbolic file name
        - url: the blob location of the file
        - time_created: the time the file was created
        - time_modified: the last time the file was modified
        - attached_threads: the threads the file is attached to
        - attached_comments: the comments the file is attached to
        """
    
    __tablename__ = "files"
    
    id = Column(
            Integer, 
            primary_key=True)

    user_certificate = Column(
            String(21), 
            ForeignKey(User.certificate), 
            nullable=False)

    user = relationship(
            "User", 
            foreign_keys="File.user_certificate",
            back_populates="uploads")

    name = Column(
            String(50), 
            CheckConstraint("length(name) > 0"), 
            nullable=False)

    #no duplicate file names for user
    __table_args__ = (UniqueConstraint("user_certificate", "name", name="_uc_user_name"),)

    url = Column(
            String(101), 
            CheckConstraint("length(url) > 1"), 
            nullable=False,
            unique=True)

    time_created = Column(
            DateTime, 
            default=datetime.utcnow(), 
            nullable=False)

    time_modified = Column(
            DateTime, 
            default=datetime.utcnow(), 
            onupdate=datetime.utcnow(), 
            nullable=False)

    attached_threads = relationship(
            "Thread",
            secondary=attachments_thread,
            back_populates="attachments")

    attached_comments = relationship(
            "Comment",
            secondary=attachments_comment,
            back_populates="attachments")

    def toDict(self):
        """returns dict of primary attributes"""
        out = {}
        out["id"] = self.id
        out["user_certificate"] = self.user_certificate
        out["name"] = self.name
        out["url"] = self.url
        out["time_created"] = _localize(self.time_created)
        out["time_modified"] = _localize(self.time_modified)
        return out

class Thread(_Base):
    """A user created thread.
    
    Attributes:
        - id (pk): the generated id of the thread
        - user: the original poster
        - user_certificate(fk): the id of original poster (also number of op's mom?)
        - heading: the display heading of the post
        - body: the body of the post
        - time_created: time created
        - time_modified: the last time the thread entity was modified
        - time_last_reply: the time of the last comment
        - reply_count: the  number of replies
        - attachments: uploaded files attached to thread body
        - replies: the comments on the thread
        """

    __tablename__ = "threads"
    
    id = Column(
            Integer, 
            primary_key=True)

    user_certificate = Column(
            String(21), 
            ForeignKey(User.certificate), 
            nullable=False)

    user = relationship(
            "User", 
            foreign_keys="Thread.user_certificate",
            back_populates="threads")

    heading = Column(
            String(160),
            CheckConstraint("length(heading) > 1"), 
            nullable=False)

    body = Column(
            String(20000),
            CheckConstraint("length(body) > 1"), 
            nullable=False)

    time_created = Column(
            DateTime, 
            default=datetime.utcnow(), 
            nullable=False)

    time_modified = Column(
            DateTime, 
            default=datetime.utcnow(), 
            onupdate=datetime.utcnow(), 
            nullable=False)

    time_last_reply = Column(DateTime)
    
    @hybrid_property
    def reply_count(self):
        if self.replies:
            return len(self.replies) 
        return 0

    attachments = relationship(
            "File",
            secondary=attachments_thread,
            back_populates="attached_threads")

    replies = relationship(
            "Comment", 
            cascade="all, delete-orphan", 
            back_populates="thread")

    def toDict(self):
        out = {}
        out["id"] = self.id
        out["user_certificate"] = self.user_certificate
        out["heading"] = self.heading
        out["body"] = self.body 
        out["time_created"] = _localize(self.time_created)
        out["time_modified"] = _localize(self.time_modified)
        out["time_last_reply"] = _localize(self.time_last_reply)
        out["reply_count"] = self.reply_count
        return out
        


@event.listens_for(Thread.replies, 'append')
def comment(thread, comment, initiator):
    """updates the last comment time, when a comment is added"""
    thread.time_last_reply = datetime.utcnow()
 
class Comment(_Base):
    """A user created comment on the thread.
    
    Attributes:
        - id(pk): the generated id of the comment
        - user: the user that posted the comment
        - user_certificate(fk): the id of the user
        - thread: the thread the comment is responding to
        - thread_id(fk): the generated id of the thread
        - body: the body of the post 
        - time_created: the time of the comment
        - time_modified: the time the comment was modified
        - attachments: the list of file attachments"""
    __tablename__ = "comments"
    
    id = Column(
            Integer, 
            primary_key=True)

    user = relationship(
            "User", 
            foreign_keys="Comment.user_certificate",
            back_populates="comments")

    user_certificate = Column(
            String(21), 
            ForeignKey(User.certificate), 
            nullable=False)

    thread = relationship(
            "Thread", 
            foreign_keys="Comment.thread_id",
            back_populates="replies")

    thread_id =  Column(
            Integer,
            ForeignKey(Thread.id), 
            nullable=False)

    body = Column(
            String(20000),
            CheckConstraint("length(body) > 1"), 
            nullable=False)

    time_created = Column(
            DateTime, 
            default=datetime.utcnow(), 
            nullable=False)
 
    time_modified = Column(
            DateTime, 
            default=datetime.utcnow(), 
            onupdate=datetime.utcnow(), 
            nullable=False)
    
    attachments = relationship(
            "File",
            secondary=attachments_comment,
            back_populates="attached_comments")

    def toDict(self):
        """populates a dictionary with our primary attributes"""
        out = {}
        out["id"] = self.id
        out["user_certificate"] = self.user_certificate
        out["thread_id"] = self.thread_id
        out["body"] = self.body
        out["time_created"] = _localize(self.time_created)
        out["time_modified"] = _localize(self.time_modified)
        out["user_certificate"] = self.user_certificate
        return out

