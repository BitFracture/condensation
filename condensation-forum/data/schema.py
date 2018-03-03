from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer


#this is a collection of the sql alchemy metadata for the schema
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)



