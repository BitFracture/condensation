#! /usr/bin/env python3
"""Test suite for testing the schema constraints"""

import unittest, traceback
from admin import dropSchema, declareSchema
from session import SessionManager
from query import getUser, getFilesByUser,getFileByName, getFileById, getThreadById, getCommentById
from sqlalchemy.exc import IntegrityError, DataError, InvalidRequestError
import sqlalchemy
from schema import User, File, Thread, Comment

sessionMgr = SessionManager("postgres","password","localhost", debug=True)

class SchemaTest(unittest.TestCase):
    """base setup for all schema related tests"""


    def setUp(self):
        
        with sessionMgr.session_scope() as session:
            dropSchema(sessionMgr.engine)
            declareSchema(sessionMgr.engine)
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
        self.values["heading1"] = "420 yolo swag 4 real"
        self.values["heading2"] = "shitpost"
        self.values["heading3"] = "I ate a melon, rind and all. AMA"
        self.values["body1"] = "Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit..."
        self.values["body2"] = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut eu lacus nibh. Vestibulum neque leo, viverra nec eros sit amet, vehicula feugiat ligula. Quisque maximus, neque in gravida ultricies, nunc mauris pretium orci, ut porta augue purus in nulla. Integer non aliquet risus. Nam ligula urna, euismod scelerisque metus eu, malesuada suscipit lorem. Proin ullamcorper lorem quis rhoncus iaculis. Integer sollicitudin sed lectus quis faucibus.
        
        Morbi est ligula, bibendum quis faucibus vitae, tempus nec ante. In sit amet odio maximus, blandit leo id, vulputate tortor. Nunc non laoreet lorem, ut finibus lorem. In vulputate porta nunc vitae maximus. In hac habitasse platea dictumst. Donec ex neque, malesuada vestibulum sem quis, pharetra varius ligula. Quisque nec lectus urna. Nulla facilisi. In in turpis odio.
        
        Etiam ullamcorper leo eros, in placerat risus posuere nec. Morbi elementum sapien a quam finibus sollicitudin. Suspendisse id viverra dui, sed vestibulum nunc. Nunc tempor sed ante metus."""
        self.values["body3"] = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin a semper nunc. Quisque bibendum egestas auctor. Phasellus varius, nunc in porttitor tristique, tortor quam vestibulum turpis, a porta tellus enim ac enim. In at massa in mauris placerat semper. Curabitur bibendum ut odio nec cursus. Suspendisse non ipsum sed velit sollicitudin pulvinar at nec orci. Donec nibh orci, porttitor at dignissim ut, suscipit nec justo.
        
        Suspendisse lacinia nec risus sit amet convallis. Proin malesuada dapibus tellus in venenatis. Duis ac ex vehicula, facilisis sem ac, pulvinar elit. Suspendisse porttitor ex tincidunt sagittis aliquam. Etiam at elementum dui. Suspendisse pulvinar magna purus, a sagittis nulla cursus gravida. Donec lacinia risus orci. Nullam placerat tortor at arcu semper, eu bibendum felis molestie.
        
        Proin eleifend odio neque, in lobortis nunc posuere nec. Nunc a lorem et tortor suscipit semper eget nec mauris. Pellentesque viverra elit eget justo posuere, ut interdum justo tristique. Vivamus semper arcu sapien, sed porttitor arcu mollis quis. Duis pretium mauris velit. Mauris viverra velit nec fermentum tristique. Maecenas venenatis, elit id rutrum mollis, velit mi iaculis dui, blandit pulvinar nisl erat quis orci. Maecenas fermentum id tortor id tincidunt. Morbi pulvinar nunc vel tempor sagittis. Mauris porttitor velit ut arcu malesuada, at efficitur velit porttitor. Etiam sed nulla quam. Praesent eleifend mollis turpis at interdum. Nulla dignissim porttitor gravida. Praesent in velit facilisis, tempus ante et, feugiat lorem. In non elit eget eros gravida rutrum. Aenean mattis quis ante quis bibendum.
        
        Pellentesque sed lectus efficitur, rutrum mauris non, tincidunt urna. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Aenean varius nisi et justo euismod tristique vitae et ante. Aenean dolor nunc, suscipit sit amet lectus varius, hendrerit volutpat justo. Vestibulum nibh nisl, malesuada ut dolor ac, consequat commodo ante. Nam mattis aliquam mattis. Vestibulum non porta sem. Ut tristique pretium libero sed semper. Nulla dictum leo sem, quis sodales quam sollicitudin elementum. Interdum et malesuada fames ac ante ipsum primis in faucibus. Curabitur sit amet blandit metus. Curabitur elementum fringilla ligula, ut egestas massa molestie nec. Etiam semper eros sit amet rhoncus rhoncus. Aliquam id metus eu tellus volutpat venenatis id ac ligula.
        
        Vestibulum pellentesque laoreet consequat. Etiam imperdiet tortor sem, at vestibulum nisi maximus in. Sed sed sodales justo. Aliquam luctus, diam non tempor lacinia, nisl justo iaculis nulla, et pulvinar augue ipsum vitae est. Cras pulvinar dolor eget ullamcorper venenatis. Quisque eu sapien elementum, porta erat at, volutpat sapien. In sit amet ex aliquam, aliquam erat quis, iaculis ex. In volutpat erat hendrerit libero posuere, at mattis dolor congue. Morbi mollis nulla nisi, non interdum odio dignissim eget. Etiam convallis metus non dui posuere tristique.
        
        In viverra dictum elit, at rhoncus lectus elementum eu. Quisque ut leo non eros sollicitudin tristique et quis tellus. Quisque pharetra tellus ac dolor ultrices ultrices. Nulla semper arcu quis ex sodales, pulvinar lacinia nisl mollis. Nulla consectetur, erat pretium ultricies lobortis, justo arcu commodo eros, nec vehicula nisi mauris quis urna. Donec nec massa bibendum, mollis odio nec, dapibus nisi. Ut a dui sit amet nibh iaculis dignissim. Ut sem eros, accumsan in porttitor malesuada, pulvinar et urna. Etiam purus tortor, facilisis nec feugiat ut, pellentesque et lectus. Proin sit amet sodales justo. Integer egestas ac diam nec aliquet. Nullam vitae leo metus.
        
        Pellentesque laoreet porttitor quam vitae dictum. Quisque ultrices urna id sapien fermentum, non pellentesque tellus tincidunt. Mauris porttitor tellus vel elit congue pulvinar. Curabitur non maximus purus, eu aliquam massa. Pellentesque cursus aliquam mi at facilisis. In purus mauris, mattis et tortor eu, faucibus hendrerit diam. Sed at aliquet lectus, non aliquam purus.
        
        Donec sit amet elit odio. Nunc ornare, mi eu faucibus sagittis, velit mi lobortis orci, laoreet dapibus risus orci ac leo. Nam posuere sollicitudin lorem sed semper. Donec malesuada rhoncus sem, sit amet sodales mauris. Aenean arcu turpis, dignissim id enim ac, vehicula maximus lacus. Etiam pharetra ligula et est pharetra rhoncus. Fusce vitae ex fermentum, scelerisque dolor ac, sagittis ex. Praesent ipsum magna, congue gravida mauris vel, pellentesque congue enim. Phasellus nec hendrerit velit.
        
        Quisque hendrerit commodo placerat. Vestibulum suscipit augue eget maximus laoreet. Sed et ante id leo scelerisque malesuada non sit amet dolor. Nam pharetra rhoncus dui, in ullamcorper ante sodales vel. Sed placerat fringilla turpis, a mattis massa posuere sit amet. Vestibulum a pulvinar dolor. Cras magna orci, consequat id condimentum sed, consectetur eget est. Nullam vitae hendrerit nisi. Donec ultrices, ipsum et blandit imperdiet, turpis risus dignissim ipsum, vitae dignissim ligula velit id nisl. Nullam condimentum placerat commodo. Sed ut eleifend mauris. Nunc sed sollicitudin massa. Pellentesque in dolor id metus aliquam tincidunt non et lorem. Sed id lobortis leo. Praesent euismod eros posuere turpis tristique accumsan. Cras gravida velit vel lacus mollis fermentum.
        
        Donec porta eu lacus sit amet pellentesque. Aenean accumsan rutrum ultricies. Proin est libero, suscipit sit amet condimentum sit amet, facilisis et orci. Proin finibus consequat augue. Pellentesque pretium ex et quam imperdiet, vitae congue nibh hendrerit. Mauris justo enim, dapibus ut diam in, fringilla vehicula metus. Mauris tristique turpis ornare nunc laoreet, quis varius sem blandit. Sed at varius libero, a viverra diam. Pellentesque condimentum eget urna id condimentum. Etiam vehicula pretium tellus ut fermentum. In sodales tortor et neque euismod, at pulvinar nisl scelerisque. In odio nulla, congue vel sodales nec, egestas quis odio. Pellentesque scelerisque, dui a venenatis gravida, sem eros tempus nulla, vitae venenatis neque nulla ac ligula. Suspendisse ligula tortor, consequat non vehicula sed, commodo quis elit. Maecenas congue nunc nec justo convallis, ut laoreet tortor egestas.
        
        Aliquam at urna vel velit cursus varius sit amet dapibus nulla. Vivamus id nibh sem. Integer faucibus, turpis nec interdum suscipit, mauris libero malesuada diam, quis elementum odio augue vel est. Ut ut leo porta, feugiat tellus eget, rutrum ex. Aenean rhoncus ante augue, vitae pharetra eros dignissim et. In blandit augue risus, eu interdum est euismod vitae. Donec id lobortis augue. Mauris consectetur, ligula vel maximus molestie, nunc felis tempus odio, sagittis cursus justo sapien eu mauris. Praesent pellentesque cursus odio, in elementum ex mollis eu. Nullam eu ligula ac turpis tempus efficitur.
        
        Mauris tempus, velit vitae tincidunt congue, magna magna maximus ligula, ut dignissim neque mi eu eros. Curabitur tincidunt eget massa fermentum vulputate. Curabitur fringilla lectus et libero auctor, et scelerisque mauris rutrum. Phasellus mollis, magna in aliquam porttitor, sem mi vestibulum magna, nec sollicitudin diam ligula at eros. Ut et nulla eget risus malesuada viverra. Sed interdum felis non nibh ullamcorper pulvinar. Duis vitae turpis sed neque luctus pharetra. Nulla pharetra massa vel lectus faucibus sodales. Fusce molestie erat id bibendum accumsan. Etiam sed felis quis neque ullamcorper ultricies. Curabitur id lorem luctus dui varius ultricies. Sed at velit in elit tristique eleifend vel ac dui. Cras tristique feugiat pellentesque. Duis at enim hendrerit, tincidunt erat a, pretium nisi. Ut nec egestas felis. Ut lobortis lobortis mi ut lacinia.
        
        Pellentesque porttitor quis purus eu imperdiet. Phasellus at lectus bibendum, eleifend felis id, vehicula lacus. Aenean a orci dolor. Phasellus eu hendrerit justo. Morbi rhoncus aliquam sapien et volutpat. Aenean in viverra eros, ac mollis nisl. Vivamus cursus dolor justo, at imperdiet felis molestie commodo. Etiam eleifend ante quam, eget blandit quam consequat congue. Sed in est laoreet massa porttitor tempus sed in augue.
        
        Donec convallis faucibus nibh, ut pellentesque justo venenatis eget. Curabitur vel mollis erat. Nulla consectetur pretium risus id tincidunt. Cras bibendum interdum mattis. Mauris varius sem et sem volutpat porttitor. Etiam condimentum purus ut venenatis viverra. Maecenas aliquam lorem at enim auctor, sit amet interdum odio fermentum. Donec sapien felis, interdum et eros sed, accumsan elementum lacus. Donec bibendum ornare nunc et pellentesque. Proin hendrerit rhoncus dignissim. Sed non velit erat.
        
        Pellentesque non rutrum neque, ac posuere sapien. Morbi laoreet turpis urna, et mattis elit scelerisque ornare. Ut euismod odio a faucibus maximus. Ut molestie eleifend nisl vel tristique. Morbi vel ligula sagittis, scelerisque quam id, tincidunt urna. Donec vel efficitur eros. Etiam a turpis auctor, pretium nisl at, lacinia quam. Aenean mollis, tellus id tempus pharetra, ex turpis consequat nibh, sit amet pellentesque tellus elit vitae elit. Praesent a hendrerit sem. Phasellus cursus bibendum placerat. Praesent feugiat porta lorem sed feugiat. Aliquam vulputate pharetra tortor at mattis. Nulla elementum vitae orci in feugiat. Curabitur metus odio, rhoncus sed ligula id, vulputate porta lacus. Quisque tempus finibus vehicula."""


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
            session.add(User(certificate=self.values["uid2"], name=3*"my name is verrrrrrrrrrrrryyyyyyyyyyyyy long"))

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
            self.assertTrue(len(getFilesByUser(session, self.values["uid1"])) ==0)

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
            f1 = getFileByName(session, self.values["uid1"], self.values["fname1"])
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
            user1 = User(certificate=self.values["uid1"], name=self.values["name1"])
            user2 = User(certificate=self.values["uid2"], name=self.values["name2"])
            user1.uploads.append(File(url=self.values["url1"], name=self.values["fname1"]))
            user2.uploads.append(File(url=self.values["url2"], name=self.values["fname2"]))
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
            user1 = User(certificate=self.values["uid1"], name=self.values["name1"])
            user2 = User(certificate=self.values["uid2"], name=self.values["name2"])
            user3 = User(certificate=self.values["uid3"], name=self.values["name2"])
            user1.uploads.append(File(url=self.values["url1"], name=self.values["fname1"]))
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
            users.append(User(certificate=self.values["uid1"], name=self.values["name1"]))
            users.append(User(certificate=self.values["uid2"], name=self.values["name2"]))
            users.append(User(certificate=self.values["uid3"], name=self.values["name3"]))
            for user in users:
                user.threads.append(Thread(heading=self.values["heading1"], body=self.values["body1"]))
                user.threads.append(Thread(heading=self.values["heading2"], body=self.values["body2"]))
            for user in users:
                for thread in user.threads:
                    thread.replies.append(Comment(user=users[0], body=self.values["body1"]))
                    thread.replies.append(Comment(user=users[1], body=self.values["body2"]))
                    thread.replies.append(Comment(user=users[2], body=self.values["body3"]))
            users[0].uploads.append(File(name=self.values["fname1"], url=self.values["url1"]))
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
            user1 = User(certificate=self.values["uid1"], name=self.values["name1"])
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
            user1 = User(certificate=self.values["uid1"], name=self.values["name1"])
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
            user1 = User(certificate=self.values["uid1"], name=self.values["name1"])
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
            users.append(User(certificate=self.values["uid1"], name=self.values["name1"]))
            users.append(User(certificate=self.values["uid2"], name=self.values["name2"]))
            users.append(User(certificate=self.values["uid3"], name=self.values["name3"]))
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
            users.append(User(certificate=self.values["uid3"], name=self.values["name3"]))
            users.append(User(certificate=self.values["uid2"], name=self.values["name3"]))
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
            users.append(User(certificate=self.values["uid3"], name=self.values["name3"]))
            users.append(User(certificate=self.values["uid2"], name=self.values["name3"]))
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

