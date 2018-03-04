#! /usr/bin/env python3
"""Test suite for testing the schema constraints"""

from schema import User, File
from session import SessionManager
from sqlalchemy.exc import IntegrityError, DataError
from admin import dropSchema, declareSchema
import unittest

class SchemaTest(unittest.TestCase):
    """base setup for all schema related tests"""
    def setUp(self):
        dropSchema()
        declareSchema()
        self.session = SessionManager("postgres","password","localhost", debug=False)

class TestSchemaUser(SchemaTest):
    """Tests the user entity"""

    def test_create(self):
        """Test object creation."""
        
        #test certificate attribute
        self.session.create(User(certificate="107125912631866552739", name="Bilbo Baggins"))
        with self.assertRaises(IntegrityError):
            self.session.create(User(certificate="107125912631866552739", name="Bilbo Baggins"))
        with self.assertRaises(IntegrityError):
            self.session.create(User(certificate="10712591263186655273", name="Bilbo Baggins"))
        with self.assertRaises(DataError):
            self.session.create(User(certificate="1071259126318665527399", name="Bilbo Baggins"))

        #test the name attribute
        with self.assertRaises(IntegrityError):
            self.session.create(User(certificate="107125912331866552739"))
        with self.assertRaises(DataError):
            self.session.create(User(certificate="107125912331866552739", name="my name is verrrrrrrrrrrrryyyyyyyyyyyyy long")) 
        with self.assertRaises(IntegrityError):
            self.session.create(User(certificate="107125912331866552739", name=""))

class TestSchemaFile(SchemaTest):
    """Test the file entity"""

    def test_create(self):
        """Test object creation."""
        with self.assertRaises(IntegrityError):
            self.session.create(File(url="www"))
        with self.assertRaises(IntegrityError):
            self.session.create(File(name = "name"))
        with self.assertRaises(IntegrityError):
            self.session.create(File())
        with self.assertRaises(IntegrityError):
            self.session.create(File(url="", name="name"))
        with self.assertRaises(IntegrityError):
            self.session.create(File(url="url", name=""))

if __name__ == "__main__":
    unittest.main()


