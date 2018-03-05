import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

#this is a collection of the sql alchemy metadata for the schema
_Base = declarative_base()


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


    def __repr__(self):
        return '<User(certificate=%s, name"%s")>' % (self.certificate, self.name)

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

class Thread(_Base):
    __tablename__ = "threads"
    
    id = Column(
            Integer, 
            primary_key=True,)

    user_certificate = Column(
            String(21), 
            ForeignKey(User.certificate), 
            nullable=False)

    user = relationship(
            "User", 
            foreign_keys="Thread.user_certificate",
            back_populates="threads")

    heading = Column(
            String(80),
            CheckConstraint("length(heading) > 1"), 
            nullable=False)

    body = Column(
            Text(10000),
            CheckConstraint("length(body) > 1"), 
            nullable=False)

    time_created = Column(
            DateTime, 
            default=datetime.datetime.utcnow(), 
            nullable=False)

#    @hybrid_property
#    def reply_count(self):
#        if replies:
#            return len(replies)
#        return 0
    

    def __repr__(self):
        return '<File(id=%d, name"%s", url="%s", time_created="%s")>' % (self.id, self.name, self.time_created)
