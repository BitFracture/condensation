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
        self.values = {}
        self.values["name1"] = "Bilbo Baggins"
        self.values["name2"] = "Frodo Baggins"
        self.values["name3"] = "Gollum"
        self.values["uid1"] = "107225912631866552739"
        self.values["uid2"] = "107225922631866552739"
        self.values["uid3"] = "107226212631866552739"
        self.values["fname1"] = "There and back again"
        self.values["fname2"] = "The lusty argonian maid"
        self.values["fname3"] = "Pugilism Illustrated"
        self.values["url1"] = "www.joes-crematorium.com"
        self.values["url2"] = "www.parrot-muzzles-r-us.com"
        self.values["url3"] = "www.tire-photos.com"


class TestSchemaUser(SchemaTest):
    """Tests the user entity"""

    def test_create(self):
        """Test object creation."""
        
        #test certificate attribute

        with sessionMgr.session_scope() as session:
            session.add(User(certificate=self.values["uid1"], name=self.values["name1"]))

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            session.add(User(certificate=self.values["uid1"], name=self.values["name1"]))

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            session.add(User(certificate="10712591263186655273", name=self.values["name1"]))

        with self.assertRaises(DataError), sessionMgr.session_scope() as session:
            session.add(User(certificate="1071259126318665527399", name=self.values["name1"]))

        #test the name attribute
        with self.assertRaises(DataError), sessionMgr.session_scope() as session:
            session.add(User(certificate=self.values["uid2"], name="my name is verrrrrrrrrrrrryyyyyyyyyyyyy long"))

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            session.add(User(certificate=self.values["uid2"], name=""))

    def test_delete(self):
        """test deletion operations"""
        with self.assertRaises(InvalidRequestError),sessionMgr.session_scope() as session:
            user = User(certificate=self.values["uid1"], name=self.values["name1"])
            session.delete(user)

        with sessionMgr.session_scope() as session:
            user = User(certificate=self.values["uid1"], name=self.values["name1"])
            user.uploads.append(File(url=self.values["url1"], name=self.values["fname1"]))
            user.uploads.append(File(url=self.values["url2"], name=self.values["fname2"]))
            session.add(user)

        with sessionMgr.session_scope() as session:
            user = getUser(session, self.values["uid1"])
            session.delete(user)

        with sessionMgr.session_scope() as session:
            self.assertIsNone(getUser(session, self.values["uid1"]))

        with sessionMgr.session_scope() as session:
            self.assertIsNone(getFile(session, self.values["uid1"], self.values["fname1"]))
            self.assertIsNone(getFile(session, self.values["uid1"], self.values["fname2"]))

    def test_update(self):
        """test update operations"""

        with sessionMgr.session_scope() as session:
            user1 = User(certificate=self.values["uid1"], name=self.values["name1"])
            user2 = User(certificate=self.values["uid2"], name=self.values["name2"])
            user1.uploads.append(File(url=self.values["url1"], name=self.values["fname1"]))
            user2.uploads.append(File(url=self.values["url2"], name=self.values["fname2"]))
            session.add(user1)
            session.add(user2)

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            user2 = getUser(session, self.values["uid2"])
            user2.certificate = self.values["uid1"]
        with sessionMgr.session_scope() as session:
            user1 = getUser(session, self.values["uid1"])
            user1.name = self.values["name3"]
        with sessionMgr.session_scope() as session:
            f1 = getFile(session, self.values["uid1"], self.values["fname1"])
            self.assertTrue(f1.user.name == self.values["name3"])


class TestSchemaFile(SchemaTest):
    """Test the file entity"""
    def test_create(self):
        """Test object creation."""

        with sessionMgr.session_scope() as session:
            user = User(certificate= self.values["uid1"], name=self.values["name1"])
            session.add(user)

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            user = getUser(session, self.values["uid1"])
            if user:
                user.uploads.append(File(url="", name=self.values["fname1"]))

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            user = getUser(session, self.values["uid1"])
            if user:
                user.uploads.append(File(url=self.values["url1"], name=""))

        with sessionMgr.session_scope() as session:
            user = getUser(session, self.values["uid1"])
            if user:
                user.uploads.append(File(url=self.values["url1"], name=self.values["fname1"]))

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            user = getUser(session, self.values["uid1"])
            if user:
                user.uploads.append(File(url=self.values["url2"], name=self.values["fname1"]))

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            user = getUser(session, self.values["uid1"])
            if user:
                user.uploads.append(File(url=self.values["url1"], name=self.values["fname2"]))


        with sessionMgr.session_scope() as session:
            user = getUser(session, self.values["uid1"])
            if user:
                user.uploads.append(File(url=self.values["fname2"], name=self.values["url2"]))

        with sessionMgr.session_scope() as session:
            user = getUser(session, self.values["uid3"])
            if user:
                user.uploads.append(File(url=self.values["fname3"], name=self.values["url3"]))

    def test_delete(self):
        """test deletion operations"""
        with self.assertRaises(InvalidRequestError),sessionMgr.session_scope() as session:
            f = File(user_certificate=self.values["uid1"], name=self.values["fname1"], url =self.values["url1"])
            session.delete(f)


        with sessionMgr.session_scope() as session:
            user1 = User(certificate=self.values["uid1"], name=self.values["name1"])
            user2 = User(certificate=self.values["uid2"], name=self.values["name2"])
            user1.uploads.append(File(url=self.values["url1"], name=self.values["fname1"]))
            user1.uploads.append(File(url=self.values["url2"], name=self.values["fname2"]))
            session.add(user1)
            session.add(user2)

        with sessionMgr.session_scope() as session:
            f = getFile(session, self.values["uid1"], self.values["fname1"])
            session.delete(f)


        with sessionMgr.session_scope() as session:
            user = getUser(session, self.values["uid1"])
            self.assertIsNotNone(user)
            self.assertIsNotNone(user.uploads)
            for f in user.uploads:
                session.delete(f)

        with sessionMgr.session_scope() as session:
            user1 = getUser(session, self.values["uid1"])
            self.assertTrue(len(user1.uploads) == 0)
            user2 = getUser(session,self.values["uid1"])
            self.assertTrue(len(user2.uploads) == 0)

    

        with sessionMgr.session_scope() as session:
            self.assertIsNone(getFile(session, self.values["uid1"], self.values["fname1"]))

    def test_update(self):
        """test update operations"""

        with sessionMgr.session_scope() as session:
            user1 = User(certificate=self.values["uid1"], name=self.values["name1"])
            user2 = User(certificate=self.values["uid2"], name=self.values["name2"])
            user1.uploads.append(File(url=self.values["url1"], name=self.values["fname1"]))
            user2.uploads.append(File(url=self.values["url2"], name=self.values["fname2"]))
            session.add(user1)
            session.add(user2)

        with sessionMgr.session_scope() as session:
            user1 = getUser(session, self.values["uid1"])
            user1.name = self.values["name3"]
            f1 = getFile(session, self.values["uid1"], self.values["fname1"])
            self.assertTrue(f1.user.name ==self.values["name3"])

class TestSchemaThread(SchemaTest):
    """Tests the user entity"""

    def test_create(self):
        """Test object creation."""
        with sessionMgr.session_scope() as session:
            session.add(User(certificate=self.values["uid1"], name=self.values["name1"]))

    def test_delete(self):
        """test deletion operations"""
        with self.assertRaises(InvalidRequestError),sessionMgr.session_scope() as session:
            user = User(certificate=self.values["uid1"], name=self.values["name1"])

    def test_update(self):
        """test update operations"""

        with sessionMgr.session_scope() as session:
            user1 = User(certificate=self.values["uid1"], name=self.values["name1"])

if __name__ == "__main__":
    unittest.main()


