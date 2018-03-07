"""Data layer for the condensation forum.

Modules:
    - data.session
        - utilities for managing the session information and completing 
          transactions
    - data.schema
        - the database schema, and runtime objects
    - data.admin
        - utilities for managing the database, meant for db administration
    - data.query
        - convenience functions for queries on the database

    - data._test_schema
        - unit tests for the schema, used for regression testing during 
          development should not be run on cloud resources, very intense
          data IO, could get expensive

##USAGE##

All of the above modules work together to harness the power of condensation 
forum's data tier, and the sqlalchemy orm framework. So a little needs to 
be understood about sqlalchemy to use this correctly.

SESSIONS:

Everything in sqlalchemy revolves around a session. these are instantiated
from a global singleton pool, and do not play nicely with concurrency. 

Create one and use it for the lifetime of your application like so:

sessionMgr = SessionManager("user","password","endpoint")

It follows the singleton pattern and will not allow additional instatiations

Using it is pretty easy. Whenever you need to do something with the database
open up a session using the provided session_scope context manager.

with sesssionMger.session_scope() as session:
    #do stuff

you can then use this session object provided just like a normal sqlalchemy
session.

CREATE:

The schema is in the you guessed it, data.schema module. where each one of
the classes in the forum is provided. These have been give full safety and
consistency constraints. To use them just import them. 

Creating Objects:
creating objects is really easy, the only use case where we will be creating
objects is creating users. all other objects are just variations on updating
users, because it is the only strong entity in the system.

To create a strong entity just instantiate it and add it to the session.

from data.session import sessionManager
from data.schema import User

with sesssionMger.session_scope() as session:
    user = User(certificate="123123123123123", name = "chipper mcstevenson the third")
    session.add(user)

RETRIEVE:

For convenience some queries have been provided to look up entities in the 
system, look for them in the query package, and adding more is very easy.

from data.session import sessionManager
from data.query import getUser


with sesssionMger.session_scope() as session:
    user = getUser(session,"123123123123123")

UPDATE:

Updating is easy, let's examine updating our user from before. Let's
introduce the query module for convenience. The steps to update an object
are to obtain a reference to it, make modifications, and let the session close.


from data.session import sessionManager
from data.schema import User
from data.query import getUser


with sesssionMger.session_scope() as session:
    user = getUser(session,"123123123123123")
    user.name = "chipper mcstevenson the fourth"

Nested Objects:
Remember how I said nested objects are just variations on updates? Let's see
that in action. Let's create a thread for our user.

from data.session import sessionManager
from data.schema import User
from data.query import getUser

with sesssionMger.session_scope() as session:
    user = getUser(session,"123123123123123")
    user.threads.append(Thread(heading="Hello World!", body="Lorem Ipsum..."))

Easy as that, the ORM will take care of filling in and updating all the proper
data.

We can do the same thing with weak entities too once they are in the system:

from data.session import sessionManager
from data.schema import User
from data.query import getUser, getThreadById

with sesssionMger.session_scope() as session:
    thread = getThreadById(123)
    user = getUser("123123123123123")
    thread.attachments.append(user.uploads[0])

DELETE:

To delete an object it can be done two ways:

(1) orphan it

from data.session import sessionManager
from data.schema import User
from data.query import getUser, getThreadById

with sesssionMger.session_scope() as session:
    thread = getThreadById(123)
    user = getUser("123123123123123")
    thread.attachments.remove(user.uploads[0])
    
(2) explicitly delete it from the session

from data.session import sessionManager
from data.schema import User
from data.query import getUser

with sesssionMger.session_scope() as session:
    thread = getThreadById(123)
    session.delete(thread)


EXCEPTIONS:
A note about exception safety. Exceptions are raised until a session closes.
There are 2 common exceptions that you will experience when you input bad data
or misuse the API, there are over 30 different kinds of exceptions raised by 
sqlalchemy, but these are what you will run in to 90% of the time.
- sqlalchemy.exc.IntegrityError: violated a relationship
- sqlalchemy.exc.DataError: violated a data constraint
"""
__all__ = ["session","admin", "schema", "query"]


