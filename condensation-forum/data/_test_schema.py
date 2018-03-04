#! /usr/bin/env python3
"""Test suite for testing the schema constraints"""

import unittest, traceback
from admin import dropSchema, declareSchema
from session import SessionManager, sessionMgr
from query import getUser, getFile
from sqlalchemy.exc import IntegrityError, DataError, InvalidRequestError
import sqlalchemy
from schema import User, File

class SchemaTest(unittest.TestCase):
    """base setup for all schema related tests"""

    def setUp(self):
        dropSchema()
        declareSchema()




class TestSchemaUser(SchemaTest):
    """Tests the user entity"""

    def test_create(self):
        """Test object creation."""
        
        #test certificate attribute

        with sessionMgr.session_scope() as session:
            u = User(certificate="107125912631866552739", name="Bilbo Baggins")
            session.add(u)

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            u = User(certificate="107125912631866552739", name="Bilbo Baggins")
            session.add(u)

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            u = User(certificate="10712591263186655273", name="Bilbo Baggins")
            session.add(u)

        with self.assertRaises(DataError), sessionMgr.session_scope() as session:
            u = User(certificate="1071259126318665527399", name="Bilbo Baggins")
            session.add(u)

        #test the name attribute
        with self.assertRaises(DataError), sessionMgr.session_scope() as session:
            u = User(certificate="107125912331866552739", name="my name is verrrrrrrrrrrrryyyyyyyyyyyyy long")
            session.add(u)

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            u = User(certificate="107125912331866552739", name="") 
            session.add(u)

    def test_delete(self):
        """test deletion operations"""
        uid = "107125912631866552739"
        n1 = "1"
        n2 = "2"
        with self.assertRaises(InvalidRequestError),sessionMgr.session_scope() as session:
            user = User(certificate=uid, name="Bilbo Baggins")
            session.delete(user)


        with sessionMgr.session_scope() as session:
            user = User(certificate=uid, name="Bilbo Baggins")
            user.uploads.append(File(url="url2", name=n1))
            user.uploads.append(File(url="url3", name=n2))
            session.add(user)

        name = ""
        with sessionMgr.session_scope() as session:
            user = getUser(session, uid)
            f = user.uploads[0]
            name = f.name
            session.delete(user)

        with sessionMgr.session_scope() as session:
            self.assertIsNone(getUser(session, uid))

        with sessionMgr.session_scope() as session:
            self.assertIsNone(getFile(session, uid, name))





class TestSchemaFile(SchemaTest):
    """Test the file entity"""
    def test_create(self):
        """Test object creation."""
        uid = "107125912631866552739"

        with sessionMgr.session_scope() as session:
            user = User(certificate= uid, name="Bilbo Baggins")
            print(user.__repr__())
            session.add(user)

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            user = getUser(session, uid)
            if user:
                user.uploads.append(File(url="", name="ame"))

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            user = getUser(session, uid)
            if user:
                user.uploads.append(File(url="ul", name=""))

        with sessionMgr.session_scope() as session:
            user = getUser(session, uid)
            print(user.__repr__())
            if user:
                user.uploads.append(File(url="url1", name="name1"))

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            user = getUser(session, uid)
            print(user.__repr__())
            if user:
                user.uploads.append(File(url="url2", name="name1"))


        with sessionMgr.session_scope() as session:
            user = getUser(session, uid)
            if user:
                user.uploads.append(File(url="url2", name="name2"))

        with sessionMgr.session_scope() as session:
            user = getUser(session, uid)
            if user:
                user.uploads.append(File(url="url3", name="name3"))

    def test_delete(self):
        """test deletion operations"""
        uid = "107125912631866552739"
        uid2 = "107225912631866552739"
        n1 = "1"
        n2 = "2"
        with self.assertRaises(InvalidRequestError),sessionMgr.session_scope() as session:
            f = File(user_certificate=uid, name=n1, url ="a")
            session.delete(f)


        with sessionMgr.session_scope() as session:
            user = User(certificate=uid, name="Bilbo Baggins")
            user2 = User(certificate=uid2, name="frodo Baggins")
            user.uploads.append(File(url="url2", name=n1))
            user.uploads.append(File(url="url3", name=n2))
            session.add(user)
            session.add(user2)

        name = ""
        with sessionMgr.session_scope() as session:
            user = getUser(session, uid)
            f = user.uploads[0]
            name = f.name
            session.delete(f)


        with sessionMgr.session_scope() as session:
            print("$$$$$$$$$$$$$$$$")
            for user in session.query(User).all():
                print("$$$$$$$$$$$", user.__repr__())
            user = getUser(session, uid)
            self.assertIsNotNone(user.uploads)
            for f in user.uploads:
                session.delete(f)

        with sessionMgr.session_scope() as session:
            user = getUser(session, uid)
            self.assertTrue(len(user.uploads) == 0)
            user2 = getUser(session, uid2)
            self.assertTrue(len(user2.uploads) == 0)

    

        with sessionMgr.session_scope() as session:
            self.assertIsNone(getFile(session, uid, name))


if __name__ == "__main__":
    unittest.main()


