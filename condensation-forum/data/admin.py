#! /usr/bin/env python3
from data.session import Session
from data.schema import Base 


def declareSchema():
    session = Session("postgres","password","localhost", debug=True)
    Base.metadata.create_all(session.engine)
    
def dropSchema():
    session = Session("postgres","password","localhost", debug=True)
    Base.metadata.drop_all(session.engine)

