import datetime
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




class User(_Base):

    __tablename__ = "users"
    
    certificate = Column(
            String(21), 
            CheckConstraint("length(certificate) = 21"), 
            primary_key=True)

    name = Column(
            String(25), 
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


class File(_Base):
    
    __tablename__ = "files"
    
    id = Column(
            Integer, 
            primary_key=True,)

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
            default=datetime.datetime.utcnow(), 
            nullable=False)

    attached_threads = relationship(
            "Thread",
            secondary=attachments_thread,
            back_populates="attachments")

    attached_comments = relationship(
            "Comment",
            secondary=attachments_comment,
            back_populates="attachments")

class Thread(_Base):
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
            String(10000),
            CheckConstraint("length(body) > 1"), 
            nullable=False)

    time_created = Column(
            DateTime, 
            default=datetime.datetime.utcnow(), 
            nullable=False)

    time_modified = Column(
            DateTime, 
            default=datetime.datetime.utcnow(), 
            onupdate=datetime.datetime.utcnow(), 
            nullable=False)

    last_reply = Column(DateTime)
    
    attachments = relationship(
            "File",
            secondary=attachments_thread,
            back_populates="attached_threads")

    replies = relationship(
            "Comment", 
            cascade="all, delete-orphan", 
            back_populates="thread")

    @hybrid_property
    def reply_count(self):
        if replies:
            return len(replies)
        return 0
 
@event.listens_for(Thread.replies, 'append')
def receive_append(thread, comment, initiator):
    """updates the last comment time, when a comment is added"""
    print("****************************************************************************************************************")
    thread.last_reply = datetime.datetime.utcnow()
    #returns original value as specified by decorator
    return comment
 
class Comment(_Base):
    __tablename__ = "comments"
    
    id = Column(
            Integer, 
            primary_key=True)


    user_certificate = Column(
            String(21), 
            ForeignKey(User.certificate), 
            nullable=False)

    user = relationship(
            "User", 
            foreign_keys="Comment.user_certificate",
            back_populates="comments")


    thread_id =  Column(
            Integer,
            ForeignKey(Thread.id), 
            nullable=False)

    thread = relationship(
            "Thread", 
            foreign_keys="Comment.thread_id",
            back_populates="replies")

    #Comment has a composite foreign key and needs to have it's constraints expressed like this
    
    body = Column(
            String(10000),
            CheckConstraint("length(body) > 1"), 
            nullable=False)

    time_created = Column(
            DateTime, 
            default=datetime.datetime.utcnow(), 
            nullable=False)
 
    time_modified = Column(
            DateTime, 
            default=datetime.datetime.utcnow(), 
            onupdate=datetime.datetime.utcnow(), 
            nullable=False)
    
    attachments = relationship(
            "File",
            secondary=attachments_comment,
            back_populates="attached_comments")

