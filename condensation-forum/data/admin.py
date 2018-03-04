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
from sqlalchemy import *

from sqlalchemy.schema import Table, DropTable


def declareSchema():
    """Declares the schema."""
    sessionMgr = SessionManager("postgres","password","localhost", debug=True)
    with sessionMgr.session_scope():
        Base.metadata.drop_all(bind=sessionMgr.engine)

    
def dropSchema():
    """Drops the schema."""
    sessionMgr = SessionManager("postgres","password","localhost", debug=True)

    with sessionMgr.session_scope():
        Base.metadata.drop_all(bind=sessionMgr.engine)




def populate():
    """Populates the database with data."""
    session = SessionManager("postgres","password","localhost", debug=True)
    certificates = ["109584283992409810224", "109584283922409810234", "109582283992409810234", "209584283992409810234"]
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

