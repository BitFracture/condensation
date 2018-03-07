#! /usr/bin/env python3
"""Test suite for testing the schema constraints"""

import unittest, traceback
from data.admin import generate_seeds, dropSchema, declareSchema
from data.session import SessionManager
from data.query import getUser, getFilesByUser,getFileByName, getFileById, getThreadById, getCommentById
from sqlalchemy.exc import IntegrityError, DataError, InvalidRequestError
import sqlalchemy
from data.schema import User, File, Thread, Comment
from configLoader import ConfigLoader


sessionMgr = SessionManager( "postgres", "password", "localhost")

class SchemaTest(unittest.TestCase):
    """base setup for all schema related tests"""


    def setUp(self):
        
        with sessionMgr.session_scope() as session:
            dropSchema(sessionMgr.engine)
            declareSchema(sessionMgr.engine)
        self.values = generate_seeds()
        
class TestSchemaUser(SchemaTest):
    """Tests the user entity"""

    def test_create(self):
        """Test object creation."""
        
        #test id attribute

        with sessionMgr.session_scope() as session:
            session.add(User(id=self.values["uid1"], name=self.values["name1"], profile_picture=self.values["pic1"]))

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            session.add(User(id=self.values["uid1"], name=self.values["name1"], profile_picture=self.values["pic1"]))

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            session.add(User(id=self.values["uid1"], name=self.values["name1"], profile_picture=self.values["pic1"]))

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            session.add(User(id="10712591263186655273", name=self.values["name1"], profile_picture=self.values["pic1"]))

        with self.assertRaises(DataError), sessionMgr.session_scope() as session:
            session.add(User(id="1071259126318665527399", name=self.values["name1"], profile_picture=self.values["pic1"]))

        #test the name attribute
        with self.assertRaises(DataError), sessionMgr.session_scope() as session:
            session.add(User(id=self.values["uid2"], name=3*"my name is verrrrrrrrrrrrryyyyyyyyyyyyy long", profile_picture=self.values["pic1"]))

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            session.add(User(id=self.values["uid2"], name="", profile_picture=self.values["pic1"]))

    def test_delete(self):
        """test deletion operations"""
        with self.assertRaises(InvalidRequestError),sessionMgr.session_scope() as session:
            user = User(id=self.values["uid1"], name=self.values["name1"], profile_picture=self.values["pic1"])
            session.delete(user)

        with sessionMgr.session_scope() as session:
            user = User(id=self.values["uid1"], name=self.values["name1"], profile_picture=self.values["pic1"])
            user.uploads.append(File(url=self.values["url1"], name=self.values["fname1"], cloud_key=self.values["key1"]))
            user.uploads.append(File(url=self.values["url2"], name=self.values["fname2"], cloud_key=self.values["key2"]))
            session.add(user)

        with sessionMgr.session_scope() as session:
            user = getUser(session, self.values["uid1"])
            session.delete(user)

        with sessionMgr.session_scope() as session:
            self.assertIsNone(getUser(session, self.values["uid1"]))

        with sessionMgr.session_scope() as session:
            self.assertTrue(len(getFilesByUser(session, self.values["uid1"])) ==0)

    def test_update(self):
        """test update operations"""

        with sessionMgr.session_scope() as session:
            user1 = User(id=self.values["uid1"], name=self.values["name1"], profile_picture=self.values["pic1"])
            user2 = User(id=self.values["uid2"], name=self.values["name2"], profile_picture=self.values["pic2"])
            user1.uploads.append(File(url=self.values["url1"], name=self.values["fname1"], cloud_key=self.values["key1"]))
            user2.uploads.append(File(url=self.values["url2"], name=self.values["fname2"], cloud_key=self.values["key2"]))
            session.add(user1)
            session.add(user2)

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            user2 = getUser(session, self.values["uid2"])
            user2.id = self.values["uid1"]
        with sessionMgr.session_scope() as session:
            user1 = getUser(session, self.values["uid1"])
            user1.name = self.values["name3"]
        with sessionMgr.session_scope() as session:
            f1 = getFileByName(session, self.values["uid1"], self.values["fname1"])
            self.assertTrue(f1.user.name == self.values["name3"])


class TestSchemaFile(SchemaTest):
    """Test the file entity"""
    def test_create(self):
        """Test object creation."""

        with sessionMgr.session_scope() as session:
            user = User(id= self.values["uid1"], name=self.values["name1"], profile_picture=self.values["pic1"])
            session.add(user)

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            user = getUser(session, self.values["uid1"])
            if user:
                user.uploads.append(File(url="", name=self.values["fname1"], cloud_key=self.values["key1"]))

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            user = getUser(session, self.values["uid1"])
            if user:
                user.uploads.append(File(url=self.values["url1"], name=""))

        with sessionMgr.session_scope() as session:
            user = getUser(session, self.values["uid1"])
            if user:
                user.uploads.append(File(url=self.values["url1"], name=self.values["fname1"], cloud_key=self.values["key1"]))

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            user = getUser(session, self.values["uid1"])
            if user:
                user.uploads.append(File(url=self.values["url2"], name=self.values["fname1"], cloud_key=self.values["key1"]))

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            user = getUser(session, self.values["uid1"])
            if user:
                user.uploads.append(File(url=self.values["url1"], name=self.values["fname2"], cloud_key=self.values["key2"]))


        with sessionMgr.session_scope() as session:
            user = getUser(session, self.values["uid1"])
            if user:
                user.uploads.append(File(url=self.values["fname2"], cloud_key=self.values["key2"], name=self.values["url2"]))

        with sessionMgr.session_scope() as session:
            user = getUser(session, self.values["uid3"])
            if user:
                user.uploads.append(File(url=self.values["fname3"], cloud_key=self.values["key3"], name=self.values["url3"]))

    def test_delete(self):
        """test deletion operations"""
        with self.assertRaises(InvalidRequestError),sessionMgr.session_scope() as session:
            f = File(user_id=self.values["uid1"], name=self.values["fname1"], cloud_key=self.values["key1"], url =self.values["url1"])
            session.delete(f)


        with sessionMgr.session_scope() as session:
            user1 = User(id=self.values["uid1"], name=self.values["name1"], profile_picture=self.values["pic1"])
            user2 = User(id=self.values["uid2"], name=self.values["name2"], profile_picture=self.values["pic2"])
            user1.uploads.append(File(url=self.values["url1"], name=self.values["fname1"], cloud_key=self.values["key1"]))
            user1.uploads.append(File(url=self.values["url2"], name=self.values["fname2"], cloud_key=self.values["key2"]))
            session.add(user1)
            session.add(user2)

        with sessionMgr.session_scope() as session:
            f = getFileByName(session, self.values["uid1"], self.values["fname1"])
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
            self.assertIsNone(getFileByName(session, self.values["uid1"], self.values["fname1"]))

    def test_update(self):
        """test update operations"""

        with sessionMgr.session_scope() as session:
            user1 = User(id=self.values["uid1"], name=self.values["name1"], profile_picture=self.values["pic1"])
            user2 = User(id=self.values["uid2"], name=self.values["name2"], profile_picture=self.values["pic2"])
            user1.uploads.append(File(url=self.values["url1"], name=self.values["fname1"], cloud_key=self.values["key1"]))
            user2.uploads.append(File(url=self.values["url2"], name=self.values["fname2"], cloud_key=self.values["key2"]))
            session.add(user1)
            session.add(user2)

        with sessionMgr.session_scope() as session:
            user1 = getUser(session, self.values["uid1"])
            user1.name = self.values["name3"]
            f1 = getFileByName(session, self.values["uid1"], self.values["fname1"])
            self.assertTrue(f1.user.name ==self.values["name3"])

    def test_attachment_thread(self):

        fid = 0
        tid = 0
        alt_tid = 0
        with sessionMgr.session_scope() as session:
            user1 = User(id=self.values["uid1"], name=self.values["name1"], profile_picture=self.values["pic1"])
            user2 = User(id=self.values["uid2"], name=self.values["name2"], profile_picture=self.values["pic2"])
            user3 = User(id=self.values["uid3"], name=self.values["name2"], profile_picture=self.values["pic2"])
            user1.uploads.append(File(url=self.values["url1"], name=self.values["fname1"], cloud_key=self.values["key1"]))
            user2.threads.append(Thread(heading=self.values["heading1"], body=self.values["body1"]))
            user3.threads.append(Thread(heading=self.values["heading1"], body=self.values["body1"]))
            session.add(user1)
            session.add(user2)
            session.add(user3)

        with sessionMgr.session_scope() as session:
            user1 = getUser(session, self.values["uid1"])
            user2 = getUser(session, self.values["uid2"])
            user3 = getUser(session, self.values["uid3"])
            fid = user1.uploads[0].id
            tid = user2.threads[0].id
            alt_tid = user3.threads[0].id
            

        with sessionMgr.session_scope() as session:
            file1 = getFileById(session, fid)
            thread1 = getThreadById(session, tid)
            thread2 = getThreadById(session, alt_tid)
            thread1.attachments.append(file1)
            thread2.attachments.append(file1)
            
        with sessionMgr.session_scope() as session:
            file1 = getFileById(session, fid)
            thread1 = getThreadById(session, tid)
            self.assertTrue(thread1 in file1.attached_threads)

        with sessionMgr.session_scope() as session:
            session.delete(user2)

        with sessionMgr.session_scope() as session:
            file1 = getFileById(session, fid)
            self.assertTrue(len(file1.attached_threads)==1)

        with sessionMgr.session_scope() as session:
            file1 = getFileById(session, fid)
            thread2 = getThreadById(session, alt_tid)
            thread2.attachments.remove(file1)

        with sessionMgr.session_scope() as session:
            file1 = getFileById(session, fid)
            self.assertTrue(len(file1.attached_threads)==0)

    def test_attachment_comment(self):
        fid = 0
        tid1 = 0
        tid2 = 0
        cid1 = 0
        cid2 = 0
        with sessionMgr.session_scope() as session:
            users = []
            users.append(User(id=self.values["uid1"], name=self.values["name1"], profile_picture=self.values["pic1"]))
            users.append(User(id=self.values["uid2"], name=self.values["name2"], profile_picture=self.values["pic2"]))
            users.append(User(id=self.values["uid3"], name=self.values["name3"], profile_picture=self.values["pic3"]))
            for user in users:
                user.threads.append(Thread(heading=self.values["heading1"], body=self.values["body1"]))
                user.threads.append(Thread(heading=self.values["heading2"], body=self.values["body2"]))
            for user in users:
                for thread in user.threads:
                    thread.replies.append(Comment(user=users[0], body=self.values["body1"]))
                    thread.replies.append(Comment(user=users[1], body=self.values["body2"]))
                    thread.replies.append(Comment(user=users[2], body=self.values["body3"]))
            users[0].uploads.append(File(name=self.values["fname1"], cloud_key=self.values["key1"], url=self.values["url1"]))
            for user in users:
                session.add(user)


        with sessionMgr.session_scope() as session:
            user1 = getUser(session, self.values["uid1"])
            user2 = getUser(session, self.values["uid2"])
            user3 = getUser(session, self.values["uid3"])
            fid = user1.uploads[0].id
            tid1 = user2.threads[0].id
            tid2 = user3.threads[0].id
            cid1 = user2.threads[0].replies[0].id
            cid2 = user3.threads[0].replies[0].id

        with sessionMgr.session_scope() as session:
            file1 = getFileById(session, fid)
            comment1 = getCommentById(session, cid1)
            comment2 = getCommentById(session, cid2)
            comment1.attachments.append(file1)
            comment2.attachments.append(file1)
            
        with sessionMgr.session_scope() as session:
            file1 = getFileById(session, fid)
            comment1 = getCommentById(session, cid1)
            self.assertTrue(comment1 in file1.attached_comments)

        with sessionMgr.session_scope() as session:
            session.delete(user2)

        with sessionMgr.session_scope() as session:
            file1 = getFileById(session, fid)
            self.assertTrue(len(file1.attached_comments)==1)

        with sessionMgr.session_scope() as session:
            file1 = getFileById(session, fid)
            comment2 = getCommentById(session, cid2)
            comment2.attachments.remove(file1)

        with sessionMgr.session_scope() as session:
            file1 = getFileById(session, fid)
            self.assertTrue(len(file1.attached_threads)==0)
            
        with sessionMgr.session_scope() as session:
            file1 = getFileById(session, fid)
            session.delete(file1)

        with sessionMgr.session_scope() as session:
            user1 = getUser(session, self.values["uid1"])
            self.assertTrue(len(user1.uploads)==0)

class TestSchemaThread(SchemaTest):
    """Tests the thread entity"""

    def test_create(self):
        """Test object creation."""
        with sessionMgr.session_scope() as session:
            user1 = User(id=self.values["uid1"], name=self.values["name1"], profile_picture=self.values["pic1"])
            user1.threads.append(Thread(heading=self.values["heading1"], body=self.values["body1"]))
            user1.threads.append(Thread(heading=self.values["heading2"], body=self.values["body2"]))
            user1.threads.append(Thread(heading=self.values["heading3"], body=self.values["body3"]))
            user1.threads.append(Thread(heading=self.values["heading3"], body=self.values["body3"]))
            session.add(user1)

        with self.assertRaises(DataError), sessionMgr.session_scope() as session:
            user1 = getUser(session, self.values["uid1"])
            user1.threads.append(Thread(heading=self.values["heading3"], body=3*self.values["body3"]))

        with self.assertRaises(DataError), sessionMgr.session_scope() as session:
            user1 = getUser(session, self.values["uid1"])
            user1.threads.append(Thread(heading=self.values["body2"], body=3*self.values["body3"]))

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            user1 = getUser(session, self.values["uid1"])
            user1.threads.append(Thread(heading="", body=self.values["body3"]))

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            user1 = getUser(session, self.values["uid1"])
            user1.threads.append(Thread(heading=self.values["heading2"], body=""))

    def test_delete(self):
        """test deletion operations"""
        with sessionMgr.session_scope() as session:
            user1 = User(id=self.values["uid1"], name=self.values["name1"], profile_picture=self.values["pic1"])
            user1.threads.append(Thread(heading=self.values["heading1"], body=self.values["body1"]))
            user1.threads.append(Thread(heading=self.values["heading2"], body=self.values["body2"]))
            user1.threads.append(Thread(heading=self.values["heading3"], body=self.values["body3"]))
            user1.threads.append(Thread(heading=self.values["heading3"], body=self.values["body3"]))
            session.add(user1)

        id = 0
        with sessionMgr.session_scope() as session:
            user1 = getUser(session, self.values["uid1"])
            id = user1.threads[0].id
            session.delete(user1.threads[0])

        with sessionMgr.session_scope() as session:
            self.assertIsNone(getThreadById(session, id))
            user1 = getUser(session, self.values["uid1"])
            self.assertTrue(len(user1.threads) == 3)

    def test_update(self):
        """test update operations"""
        with sessionMgr.session_scope() as session:
            user1 = User(id=self.values["uid1"], name=self.values["name1"], profile_picture=self.values["pic1"])
            user1.threads.append(Thread(heading=self.values["heading1"], body=self.values["body1"]))
            session.add(user1)

        id = 0
        with sessionMgr.session_scope() as session:
            user1 = getUser(session, self.values["uid1"])
            user1.threads[0].heading = self.values["heading2"]
            id = user1.threads[0].id

        with sessionMgr.session_scope() as session:
            t = getThreadById(session, id)
            self.assertTrue(t.heading == self.values["heading2"] )
            
class TestSchemaComment(SchemaTest):
    """Tests the comment entity"""
    def test_create(self):
        """Test object creation."""
        with sessionMgr.session_scope() as session:
            users = []
            users.append(User(id=self.values["uid1"], name=self.values["name1"], profile_picture=self.values["pic1"]))
            users.append(User(id=self.values["uid2"], name=self.values["name2"], profile_picture=self.values["pic2"]))
            users.append(User(id=self.values["uid3"], name=self.values["name3"], profile_picture=self.values["pic3"]))
            for user in users:
                user.threads.append(Thread(heading=self.values["heading1"], body=self.values["body1"]))
                user.threads.append(Thread(heading=self.values["heading2"], body=self.values["body2"]))
            for user in users:
                for thread in user.threads:
                    thread.replies.append(Comment(user=users[0], body=self.values["body1"]))
                    thread.replies.append(Comment(user=users[1], body=self.values["body2"]))
                    thread.replies.append(Comment(user=users[2], body=self.values["body3"]))
            for user in users:
                session.add(user)


        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            user = getUser(session,self.values["uid3"])
            user.threads[0].replies.append(Comment(body=self.values["body3"]))

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            user = getUser(session,self.values["uid3"])
            user.threads[0].replies.append(Comment(user=users[0], body=""))

        with self.assertRaises(IntegrityError), sessionMgr.session_scope() as session:
            user = getUser(session,self.values["uid3"])
            user.threads[0].replies.append(Comment(user=users[0]))
        

    def test_delete(self):
        """test deletion operations"""
        with sessionMgr.session_scope() as session:
            users = []
            users.append(User(id=self.values["uid3"], name=self.values["name3"], profile_picture=self.values["pic3"]))
            users.append(User(id=self.values["uid2"], name=self.values["name3"], profile_picture=self.values["pic3"]))
            for user in users:
                user.threads.append(Thread(heading=self.values["heading1"], body=self.values["body1"]))
                user.threads.append(Thread(heading=self.values["heading1"], body=self.values["body1"]))
            for user in users:
                for thread in user.threads:
                    thread.replies.append(Comment(user=users[0], body=self.values["body1"]))
                    thread.replies.append(Comment(user=users[0], body=self.values["body2"]))
                    thread.replies.append(Comment(user=users[1], body=self.values["body3"]))
            for user in users:
                session.add(user)

        ct = 0
        cid = 0
        with sessionMgr.session_scope() as session:
            user = getUser(session,self.values["uid3"])
            ct = user.threads[0].reply_count
            cid = user.threads[0].replies[0].id
            session.delete(user.threads[0].replies[0])

        with sessionMgr.session_scope() as session:
            self.assertIsNone(getCommentById(session,cid))
            user = getUser(session,self.values["uid3"])
            self.assertTrue(user.threads[0].reply_count + 1 == ct)

        with sessionMgr.session_scope() as session:
            user = getUser(session,self.values["uid3"])
            cid = user.threads[0].replies[0].id
            session.delete(user.threads[0])
        with sessionMgr.session_scope() as session:
            self.assertIsNone(getCommentById(session,cid))

        with sessionMgr.session_scope() as session:
            user = getUser(session,self.values["uid3"])
            cid = user.threads[0].replies[0].id
            session.delete(user)
        with sessionMgr.session_scope() as session:
            self.assertIsNone(getCommentById(session,cid))

    def test_update(self):
        """test update operations"""
        with sessionMgr.session_scope() as session:
            users = []
            users.append(User(id=self.values["uid3"], name=self.values["name3"], profile_picture=self.values["pic3"]))
            users.append(User(id=self.values["uid2"], name=self.values["name3"], profile_picture=self.values["pic3"]))
            for user in users:
                user.threads.append(Thread(heading=self.values["heading1"], body=self.values["body1"]))
            for user in users:
                for thread in user.threads:
                    thread.replies.append(Comment(user=users[0], body=self.values["body1"]))
                    thread.replies.append(Comment(user=users[1], body=self.values["body2"]))
            for user in users:
                session.add(user)

        editTime = None
        with sessionMgr.session_scope() as session:
            user = getUser(session,self.values["uid3"])
            editTime = user.threads[0].time_last_reply
            user.threads[0].replies.append(Comment(user=users[1], body=self.values["body2"]))
            self.assertTrue(editTime < user.threads[0].time_last_reply)
            
        cid = 0
        with sessionMgr.session_scope() as session:
            user = getUser(session,self.values["uid3"])
            user.threads[0].replies[0].body = self.values["body3"]
            self.assertTrue(user.comments[1].body == self.values["body3"])

if __name__ == "__main__":
    unittest.main()

