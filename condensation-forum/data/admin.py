#! /usr/bin/env python3
"""Administrtative code for the data layer.

Running this module will regenerate the database.

static methods:
    declareSchema - declare the schema
    dropSchema - drops the schema
    populate - populates the database with data
"""
from schema import _Base, User, File
from sqlalchemy import *
from sqlalchemy.engine import reflection
from sqlalchemy.schema import Table, DropTable, DropConstraint



def declareSchema(engine):
    """Declares the schema."""
    _Base.metadata.create_all(bind=engine)

    
def dropSchema(engine):
    """Drops the schema."""

    # From http://www.sqlalchemy.org/trac/wiki/UsageRecipes/DropEverything
    inspector = reflection.Inspector.from_engine(engine)
    metadata = MetaData()
    
    tbs = []
    all_fks = []
    
    for table_name in inspector.get_table_names():
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            if not fk['name']:
                continue
            fks.append( ForeignKeyConstraint((),(),name=fk['name']))
        t = Table(table_name,metadata,*fks)
        tbs.append(t)
        all_fks.extend(fks)
    
    for fkc in all_fks:
        engine.execute(DropConstraint(fkc))
    
    for table in tbs:
        engine.execute(DropTable(table))


def populate(session):
    """Populates the database with data."""
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
    sessionMgr = SessionManager("postgres","password","localhost", debug=True)
    with sessionMgr.session_scope() as session:
        dropSchema(sessionMgr.engine)
        declareSchema(sessionMgr.engine)
        populate(session)

