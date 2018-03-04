#! /usr/bin/env python3
"""Test suite for testing the schema constraints"""

import unittest, traceback
from admin import dropSchema, declareSchema
from session import SessionManager
from query import getUser
from sqlalchemy.exc import IntegrityError, DataError
import sqlalchemy
from schema import User, File

class SchemaTest(unittest.TestCase):
    """base setup for all schema related tests"""

    def setUp(self):
        dropSchema()
        declareSchema()
        self.mgr = SessionManager("postgres","password","localhost", debug=True)




class TestSchemaUser(SchemaTest):
    """Tests the user entity"""

    def test_create(self):
        """Test object creation."""
        
        #test certificate attribute

        with self.mgr.session_scope() as session:
            u = User(certificate="107125912631866552739", name="Bilbo Baggins")

        with self.assertRaises(IntegrityError), self.mgr.session_scope() as session:
            u = User(certificate="107125912631866552739", name="Bilbo Baggins")
            session.add(u)

        with self.assertRaises(IntegrityError), self.mgr.session_scope() as session:
            u = User(certificate="10712591263186655273", name="Bilbo Baggins")
            session.add(u)

        with self.assertRaises(DataError), self.mgr.session_scope() as session:
            u = User(certificate="1071259126318665527399", name="Bilbo Baggins")
            session.add(u)

        #test the name attribute
        with self.assertRaises(DataError), self.mgr.session_scope() as session:
            u = User(certificate="107125912331866552739", name="my name is verrrrrrrrrrrrryyyyyyyyyyyyy long")
            session.add(u)

        with self.assertRaises(IntegrityError), self.mgr.session_scope() as session:
            u = User(certificate="107125912331866552739", name="") 
            session.add(u)
        

class TestSchemaFile(SchemaTest):
    """Test the file entity"""
    def test_create(self):
        """Test object creation."""

        print("hello")

        uid = "107125912631866552739"

        with self.mgr.session_scope() as session:
            user = User(certificate= uid, name="Bilbo Baggins")

        with self.assertRaises(IntegrityError), self.mgr.session_scope() as session:
            user = getUser(session, uid)
            if user:
                user.uploads.append(File(url="", name="ame"))

        with self.assertRaises(IntegrityError):
            user = getUser(session, uid)
            if user:
                user.uploads.append(File(url="ul", name=""))

        with self.mgr.session_scope() as session:
            user = getUser(session, uid)
            if user:
                user.uploads.append(File(url="url1", name="name1"))

        with self.mgr.session_scope() as session:
            user = getUser(session, uid)
            if user:
                user.uploads.append(File(url="url2", name="name2"))

        with self.mgr.session_scope() as session:
            user = getUser(session, uid)
            if user:
                user.uploads.append(File(url="url3", name="name3"))



if __name__ == "__main__":
    unittest.main()


