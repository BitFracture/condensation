#! /usr/bin/env python3
"""Administrtative code for the data layer.

Running this module will regenerate the database.

static methods:
    declareSchema - declare the schema
    dropSchema - drops the schema
    populate - populates the database with data
"""
from session import SessionManager
from schema import Base, User, File



def declareSchema():
    """Declares the schema."""
    session = SessionManager("postgres","password","localhost", debug=True)
    Base.metadata.create_all(session.engine)
    
def dropSchema():
    """Drops the schema."""
    session = SessionManager("postgres","password","localhost", debug=True)
    Base.metadata.drop_all(session.engine)

def populate():
    """Populates the database with data."""
    session = SessionManager("postgres","password","localhost", debug=True)
    certificates = ["12341234123412341234", "12341234123412341235", "12341234123412341236", "12341234123412341237"]
    names = ["Bilbo Baggins", "Gandalf Greyhame", "Merry Took", "Pippin Took"]
    fnames = ["there and back again", "fantastic spells and where to find them", "longbottom leaf, the dank growers guide", "hobbiton sports illustrated, swimsuit edition"]
    furls = ["www.example.com/1", "www.example.com/2", "www.example.com/3", "www.example.com/4"]

    for cert, name, fname, furl, in zip(certificates,  names, fnames, furls):
        user = User(certificate = cert, name = name)
        uFile = File(name = fname, url=furl)
        session.create(user)
        session.create(uFile)


if __name__ == "__main__":
    dropSchema()
    declareSchema()
    populate()

