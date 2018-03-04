import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

#this is a collection of the sql alchemy metadata for the schema
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False)

    def __repr__(self):
        return '<User(id=%d, name"%s")>' % (self.id, self.name)


class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)
    url = Column(String(150), nullable=False)
    time_created = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)

    def __repr__(self):
        return '<File(id=%d, name"%s", url="%s", time_created="%s")>' % (self.id, self.name, self.time_created)
