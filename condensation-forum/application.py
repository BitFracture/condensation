"""
An AWS Python3+Flask web app.
"""

from flask import Flask, redirect, url_for, request, session, flash, get_flashed_messages, render_template
from flask_oauthlib.client import OAuth
import boto3,botocore
import jinja2
from boto3.dynamodb.conditions import Key, Attr
import urllib.request
import json
import cgi
import time
import random
import sys
from configLoader import ConfigLoader
from googleOAuthManager import GoogleOAuthManager
from data.session import SessionManager
from data import query, schema
from forms import CreateThreadForm, CreateCommentForm
import inspect
from werkzeug.utils import secure_filename
import hashlib
import uuid
import os

###############################################################################
#FLASK CONFIG
###############################################################################

# This is the EB application, calling directly into Flask
application = Flask(__name__)
# Loads config from file or environment variable
config = ConfigLoader("config.local.json")
# Enable encrypted session, required for OAuth to stick
application.secret_key = config.get("sessionSecret")
#used for form validation
application.config["SECRET_KEY"]=config.get("sessionSecret")

# Set up service handles
botoSession = boto3.Session(
    aws_access_key_id = config.get("accessKey"),
    aws_secret_access_key = config.get("secretKey"),
    aws_session_token=None,
    region_name = config.get("region"),
    botocore_session=None,
    profile_name=None)

dynamodb = botoSession.resource('dynamodb')
s3       = botoSession.resource('s3')

authCacheTable = dynamodb.Table('person-attribute-table')
# Example: bucket = s3.Bucket('elasticbeanstalk-us-west-2-3453535353')

# OAuth setup
authManager = GoogleOAuthManager(
        flaskApp     = application,
        clientId     = config.get("oauthClientId"),
        clientSecret = config.get("oauthClientSecret"))
#This is the Upload requirement section
bucket = s3.Bucket('condensation-forum')
bucket_name = 'condensation-forum'
s3client = boto3.client(
   "s3",
   aws_access_key_id=config.get("accessKey"),
   aws_secret_access_key=config.get("secretKey")
)


#database connection
dataSessionMgr = SessionManager(
        config.get("dbUser"),
        config.get("dbPassword"),
        config.get("dbEndpoint"))

# Load up Jinja2 templates
templateLoader = jinja2.FileSystemLoader(searchpath="./templates/")
templateEnv = jinja2.Environment(loader=templateLoader)

#pass in library functions to jinja, isn't python terrifying?
#we want to zip collections in view
templateEnv.globals.update(zip=zip)
#we also want to view our flashed messages
templateEnv.globals.update(get_flashed_messages=get_flashed_messages)


bodyTemplate = templateEnv.get_template("body.html")
homeTemplate = templateEnv.get_template("home.html")
threadTemplate = templateEnv.get_template("thread.html")
createThreadTemplate = templateEnv.get_template("new-thread.html")
createCommentTemplate = templateEnv.get_template("new-comment.html")
fileManagerTemplate = templateEnv.get_template("fileManager.html")


###############################################################################
#END CONFIG
###############################################################################


@application.route('/', methods=['GET'])
@authManager.enableAuthentication
def indexGetHandler():
    """
    Returns the template "home" wrapped by "body" served as HTML
    """
    threads = None
    #grab threads ordered by time, and zip them with some usernames
    with dataSessionMgr.session_scope() as dbSession:

        user = authManager.getUserData()
        if not user:
            flash("Welcome, please login or create an account.")


        threads = query.getThreadsByCommentTime(dbSession)
        urls = [url_for("threadGetHandler", tid=thread.id) for thread in threads]
        usernames = [thread.user.name for thread in threads]
        threads = query.extractOutput(threads)

    #handle thread creation button
    createThreadUrl = url_for("newThreadHandler")


    homeRendered = homeTemplate.render(
            threads=threads,
            urls=urls,
            usernames=usernames,
            createUrl=createThreadUrl)

    user = authManager.getUserData()
    removeUrl="/"
    if user:
        removeUrl=url_for("deleteUserHandler", uid=user["id"])

    return bodyTemplate.render(
            title="Home",
            body=homeRendered,
            user=user,
            removeUrl=removeUrl,
            location=request.url)


@application.route("/new-thread", methods=["GET", "POST"])
@authManager.requireAuthentication
def newThreadHandler():
    """ Renders the thread creation screen, creates thread if all data is validated """

    #do not allow unauthenticated users to submit
    form = CreateThreadForm()

    user = authManager.getUserData()
    if not user:
        abort(403)
    if form.validate_on_submit():
        tid = None
        try:
            with dataSessionMgr.session_scope() as dbSession:
                user = query.getUser(dbSession, user["id"])
                thread = schema.Thread(heading=form.heading.data, body=form.body.data)
                user.threads.append(thread)
                #commits current transactions so we can grab the generated id
                dbSession.flush()
                tid = thread.id
            flash("Thread Created")
            #redirect to the created thread view
            return redirect(url_for("threadGetHandler", tid=tid))
        except:
            flash("Comment Creation Failed")
            return redirect(url_for("indexGetHandler"))

    #error handling is done in the html forms
    user = authManager.getUserData()
    removeUrl="/"
    if user:
        removeUrl=url_for("deleteUserHandler", uid=user["id"])
    rendered = createThreadTemplate.render(form=form)
    return bodyTemplate.render(
            title="Create Thread",
            body=rendered,
            user=user,
            removeUrl=removeUrl,
            location=url_for('indexGetHandler', _external=True))


@application.route("/new-comment?<int:tid>", methods=["GET", "POST"])
@authManager.requireAuthentication
def newCommentHandler(tid):
    """Renders the thread creation screen, creates thread if all data is validated"""

    #do not allow unauthenticated users to submit
    form = CreateCommentForm()

    user = authManager.getUserData()
    if not user:
        abort(403)
    if form.validate_on_submit():
        try:
            with dataSessionMgr.session_scope() as dbSession:
                user = query.getUser(dbSession, user["id"])
                thread = query.getThreadById(dbSession, tid)
                thread.replies.append(schema.Comment(user=user, body=form.body.data))

            flash("Comment Created")
            #redirect to the created thread view
            return redirect(url_for("threadGetHandler", tid=tid))
        except:
            flash("Comment Creation Failed")
            return redirect(url_for("indexGetHandler"))


    #error handling is done in the html forms
    user = authManager.getUserData()
    removeUrl="/"
    if user:
        removeUrl=url_for("deleteUserHandler", uid=user["id"])
    rendered = createCommentTemplate.render(form=form)
    return bodyTemplate.render(
            title="Reply",
            body=rendered,
            user=user,
            removeUrl=removeUrl,
            location=url_for('indexGetHandler', _external=True))


@application.route("/thread/<int:tid>)", methods=["GET"])
@authManager.enableAuthentication
def threadGetHandler(tid):
    """Renders a thread, attachments, and all relevant comments"""
    #grab the thread with attachments
    thread = None
    with dataSessionMgr.session_scope() as dbSession:
        thread = query.getThreadById(dbSession, tid)
        thread_attachments = query.extractOutput(thread.attachments)
        op = thread.user.name

        replyUrl = url_for("newCommentHandler", tid=thread.id)
        post_attachments = query.extractOutput(thread.attachments)
        comments = query.getCommentsByThread(dbSession, thread.id)
        comment_attachments = [query.extractOutput(comment.attachments) for comment in comments]
        comment_users = [comment.user.name for comment in comments]
        comments = query.extractOutput(comments)
        thread = query.extractOutput(thread)

    user = authManager.getUserData();
    removeUrl="/"
    if user:
        removeUrl=url_for("deleteUserHandler", uid=user["id"])    
    threadRendered = threadTemplate.render(
            thread=thread,
            thread_attachments=thread_attachments,
            op=op,
            comments=comments,
            comment_attachments=comment_attachments,
            comment_users=comment_users,
            replyUrl=replyUrl)
    return bodyTemplate.render(
            title="Thread",
            body=threadRendered,
            removeUrl=removeUrl,
            user=user,
            location=request.url)


@authManager.loginCallback
def loginCallback():
    """
    This is invoked when a user logs in, before any other logic.
    """
    user = authManager.getUserData()
    if user:
        try:
            with dataSessionMgr.session_scope() as dbSession:
                #add a new user if not in the database
                if not query.getUser(dbSession, user["id"]):
                    print("User created: " + user["name"], file=sys.stderr)
                    dbSession.add(schema.User(
                        id=user["id"], 
                        name=user["name"], 
                        profile_picture=user["picture"]))
                    flash("Account Created")
        except:
            flash("Account Creation Failed")
            #if this fails logout and redirect home
            return redirect(authManager.LOGOUT_ROUTE)


@application.route("/delete-user?id=<int:uid>", methods=["GET"])
@authManager.requireAuthentication
def deleteUserHandler(uid):
    """Deletes a user and redirects them home"""
    user = authManager.getUserData()
    print("delete", uid, user["id"], file = sys.stderr)
    if user and int(user["id"]) == uid:
        try:
            with dataSessionMgr.session_scope() as dbSession:
                account = query.getUser(dbSession, user["id"])
                if account:
                    dbSession.delete(account)
                    flash("Account Deleted")
        except:
            flash("Account Deletion Failed")

    return redirect(authManager.LOGOUT_ROUTE)
        



@authManager.logoutCallback
def logoutCallback():
    """
    This is invoked when a user logs in, before any other logic.
    """
    user = authManager.getUserData()
    print("User signed out: " + user["name"], file=sys.stderr)


@application.route('/file-delete', methods=['POST'])
@authManager.requireAuthentication
def fileManagerDeleteHander():
    user = authManager.getUserData()
    fid = int(request.form['file'])
    
    if not user:
        abort(403)
    id = user['id']

    #delete the file by Cloud_key in AWS S3
    with dataSessionMgr.session_scope() as dbSession:
        file1 = query.getFileById(dbSession,fid)
        file1 = query.extractOutput(file1)
    
    key = file1['cloud_key']
    try:
        s3client.delete_object(Bucket=bucket_name,Key=key)
    except Exception as e:
        print("Something happen: ",e)
        return e
    
    #delete the file by fileID in DB
    with dataSessionMgr.session_scope() as dbSession:
        file = query.getFileById(dbSession,fid)
        if file:
            dbSession.delete(file)
            flash("File Deleted")
  
    return redirect(url_for("fileManager"))

@application.route('/fileManager', methods=['GET', 'POST'])
@authManager.requireAuthentication
def fileManager():
    user = authManager.getUserData()
    if request.method == 'POST':
        # do stuff when the form is submitted
        if not user:
            abort(403)
        id = user['id']

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename.strip() == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            # Determine shortened file name (secure)
            filename = secure_filename(file.filename.strip())
            while (len(filename) > 50):
                cutString = len(filename)%50
                filename = filename[cutString:len(filename)]

            # Determine the S3 key
            try:
                myUuid = uuid.uuid4().hex
                fn, fileExtension = os.path.splitext(filename)
                key = id + "/" + myUuid + fileExtension
                s3client.upload_fileobj(file, bucket_name, key, ExtraArgs={"ACL": "public-read", "ContentType": file.content_type})
                url = "https://s3-us-west-2.amazonaws.com/condensation-forum/" + key
                storeToDB(id, url, key, filename)
                flash('Upload Successfully')
                return redirect("/fileManager")
            except Exception as e:
                print("Something happen: ",e)
                return e

        else:
            return redirect("/fileManager")
        
        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect("/fileManager")
    
    if request.method == 'GET':
        if not user:
            abort(403)
        id = user['id']
        #Get the user's profile from the DB and zip it first
        with dataSessionMgr.session_scope() as dbSession:
            files = query.getFilesByUser(dbSession,id)
            files = query.extractOutput(files)

        if files != None:
            fileManagerRendered = fileManagerTemplate.render(files=files)
            return bodyTemplate.render(
                title="File Manager",
                body = fileManagerRendered,
                user=user,
                # Todo: Incorporate removeURL here
                location=request.url)
        
    fileManagerRendered = fileManagerTemplate.render()
    return bodyTemplate.render(
                title="File Manager",
                body = fileManagerRendered,
                user=user,
                # Todo: Incorporate removeURL here
                location=request.url)

def storeToDB(userID,url,key,filename):
    """This method is used to store the data uploaded into DB"""
    with dataSessionMgr.session_scope() as dbSession:
             user = query.getUser(dbSession, userID)
             file = schema.File(url=url, cloud_key=key, name=filename)
             user.uploads.append(file)

# Run Flask app now
if __name__ == "__main__":
    # Enable debug output, disable in prod
    application.debug = True
    application.run()
