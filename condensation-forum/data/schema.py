import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

#this is a collection of the sql alchemy metadata for the schema
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    certificate = Column(String(21), CheckConstraint("length(certificate) = 21"), primary_key=True)
    name = Column(String(25), CheckConstraint("length(name) > 1"), nullable=False)
    def __repr__(self):
        return '<User(id=%d, name"%s")>' % (self.id, self.name)


class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), CheckConstraint("length(name) > 1"), nullable=False)
    url = Column(String(101), CheckConstraint("length(url) > 1"), nullable=False)
    time_created = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)

    def __repr__(self):
        return '<File(id=%d, name"%s", url="%s", time_created="%s")>' % (self.id, self.name, self.time_created)
