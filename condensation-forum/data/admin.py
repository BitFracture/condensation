#! /usr/bin/env python3
from data.session import SessionManager
from data.schema import Base, User, File



def declareSchema():
    session = SessionManager("postgres","password","localhost", debug=True)
    Base.metadata.create_all(session.engine)
    
def dropSchema():
    session = SessionManager("postgres","password","localhost", debug=True)
    Base.metadata.drop_all(session.engine)

def populate():
    session = SessionManager("postgres","password","localhost", debug=True)
    names = ["Bilbo Baggins", "Gandalf Greyhame", "Merry Took", "Pippin Took"]
    fnames = ["there and back again", "fantastic spells and where to find them", "longbottom leaf, the dank growers guide", "hobbiton sports illustrated, swimsuit edition"]
    furls = ["www.example.com/1", "www.example.com/2", "www.example.com/3", "www.example.com/4"]

    for name, fname, furl, in zip(names, fnames, furls):
        user = User(name=name)
        uFile = File(name = fname, url=furl)
        session.create(user)
        session.create(uFile)
