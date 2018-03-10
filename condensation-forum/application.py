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
#generate urls for buttons in the view
templateEnv.globals.update(url_for=url_for)


bodyTemplate = templateEnv.get_template("body.html")
bodySimpleTemplate = templateEnv.get_template("body-simple.html")
homeTemplate = templateEnv.get_template("home.html")
threadTemplate = templateEnv.get_template("thread.html")
editThreadTemplate = templateEnv.get_template("edit-thread.html")
editCommentTemplate = templateEnv.get_template("edit-comment.html")
fileManagerTemplate = templateEnv.get_template("file-manager.html")
fileListTemplate = templateEnv.get_template("file-list.html")


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
        user = authManager.getUserData()
        threads = query.extractOutput(threads)



    homeRendered = homeTemplate.render(
            threads=threads,
            urls=urls,
            usernames=usernames)

    user = authManager.getUserData()
    return bodyTemplate.render(
            title="Home",
            body=homeRendered,
            user=user,
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
    rendered = editThreadTemplate.render(form=form)

    return bodyTemplate.render(
            title="Create Thread",
            body=rendered,
            user=user,
            location=url_for('indexGetHandler', _external=True))

@application.route("/edit-thread?tid=<int:tid>", methods=["GET", "POST"])
@authManager.requireAuthentication
def editThreadHandler(tid):
    """Renders an existing threaed to be modified """

    #do not allow unauthenticated users to submit
    form = CreateThreadForm()

    #verify security no error handling because if this fails we have problems, we should fail too
    user = authManager.getUserData()
    if not user:
        abort(403)
    with dataSessionMgr.session_scope() as dbSession:
         thread = query.getThreadById(dbSession, tid)
         if user["id"] != thread.user_id:
             abort(403)

    if form.validate_on_submit():
        try:
            with dataSessionMgr.session_scope() as dbSession:
                thread = query.getThreadById(dbSession, tid)
                if user["id"] != thread.user_id:
                    abort(403)
                thread.heading = form.heading.data
                thread.body = form.body.data
            flash("Thread Updated")
            #redirect to the created thread view
            return redirect(url_for("threadGetHandler", tid=tid))
        except:
            flash("Thread Update Failed")
            return redirect(url_for("indexGetHandler"))

    #populate with old data from forms
    with dataSessionMgr.session_scope() as dbSession:
         thread = query.getThreadById(dbSession, tid)
         form.heading.data = thread.heading
         form.body.data = thread.body

    #error handling is done in the html forms
    rendered = editThreadTemplate.render(form=form, edit = True)
    return bodyTemplate.render(
            title="Edit Thread",
            body=rendered,
            user=user,
            location=url_for('indexGetHandler', _external=True))

@application.route("/delete-thread?tid=<int:tid>", methods=["GET"])
@authManager.requireAuthentication
def deleteThreadHandler(tid):
    """Deletes a thread."""

    #verify security no error handling because if this fails we have problems, we should fail too
    user = authManager.getUserData()
    if not user:
        abort(403)
    try:
        with dataSessionMgr.session_scope() as dbSession:
            thread = query.getThreadById(dbSession, tid)
            if not thread:
                abort(404)
            if user["id"] != thread.user_id:
                abort(403)
            dbSession.delete(thread)
        flash("Thread Deleted")
    except:
        flash("Thread Deletion Failed")
    return redirect(url_for("indexGetHandler"))

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

    rendered = editCommentTemplate.render(form=form)
    user = authManager.getUserData()

    return bodyTemplate.render(
            title="Reply",
            body=rendered,
            user=user,
            location=url_for('indexGetHandler', _external=True))

@application.route("/edit-comment?cid=<int:cid>", methods=["GET", "POST"])
@authManager.requireAuthentication
def editCommentHandler(cid):
    """Renders an existing comment to be modified """

    print("hello world comment edit", file=sys.stderr)
    #do not allow unauthenticated users to submit
    form = CreateCommentForm()

    #verify security no error handling because if this fails we have problems, we should fail too
    user = authManager.getUserData()
    if not user:
        abort(403)
    with dataSessionMgr.session_scope() as dbSession:
         comment = query.getCommentById(dbSession, cid)
         if user["id"] != comment.user_id:
             abort(403)

    if form.validate_on_submit():
        try:
            with dataSessionMgr.session_scope() as dbSession:
                comment = query.getCommentById(dbSession, cid)
                tid = comment.thread_id
                if user["id"] != comment.user_id:
                    abort(403)
                comment.body = form.body.data
            flash("Comment Updated")
            #redirect to the created thread view
            return redirect(url_for("threadGetHandler", tid=tid))
        except:
            flash("Comment Update Failed")
            return redirect(url_for("indexGetHandler"))

    #populate with old data from forms
    with dataSessionMgr.session_scope() as dbSession:
         comment = query.getCommentById(dbSession, cid)
         form.body.data = comment.body

    #error handling is done in the html forms
    rendered = editCommentTemplate.render(form=form, edit = True)
    return bodyTemplate.render(
            title="Edit Comment",
            body=rendered,
            user=user,
            location=url_for('indexGetHandler', _external=True))

@application.route("/delete-comment?cid=<int:cid>", methods=["GET"])
@authManager.requireAuthentication
def deleteCommentHandler(cid):
    """Deletes a comment."""

    #verify security no error handling because if this fails we have problems, we should fail too
    user = authManager.getUserData()
    if not user:
        abort(403)
    try:
        with dataSessionMgr.session_scope() as dbSession:
            comment = query.getCommentById(dbSession, cid)
            if not comment:
                abort(404)
            if user["id"] != comment.user_id:
                abort(403)
            dbSession.delete(comment)
        flash("Comment Deleted")
    except:
        flash("Comment Deletion Failed")
    return redirect(url_for("indexGetHandler"))

@application.route("/thread/<int:tid>)", methods=["GET"])
@authManager.enableAuthentication
def threadGetHandler(tid):
    """Renders a thread, attachments, and all relevant comments"""
    #grab the thread with attachments
    thread = None
    with dataSessionMgr.session_scope() as dbSession:
        thread = query.getThreadById(dbSession, tid)
        thread_attachments = query.extractOutput(thread.attachments)

        user = authManager.getUserData()
        uid = user["id"] if user else 0

        op = thread.user.name
        op_permission = thread.user_id == uid

        replyUrl = url_for("newCommentHandler", tid=thread.id)
        post_attachments = query.extractOutput(thread.attachments)

        comments = query.getCommentsByThread(dbSession, thread.id)
        comment_attachments =[]
        comment_users = []
        edit_permissions = []
        for comment in comments:
            comment_attachments.append(query.extractOutput(comment.attachments))
            comment_users.append(comment.user.name)
            edit_permissions.append(uid == comment.user_id)

        comments = query.extractOutput(comments)
        thread = query.extractOutput(thread)

    threadRendered = threadTemplate.render(
            thread=thread,
            thread_attachments=thread_attachments,
            op=op,
            op_permission=op_permission,
            comments=comments,
            comment_attachments=comment_attachments,
            comment_users=comment_users,
            edit_permissions=edit_permissions,
            replyUrl=replyUrl)

    user = authManager.getUserData();
    return bodyTemplate.render(
            title="Thread",
            body=threadRendered,
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


@application.route("/delete-user", methods=["GET"])
@authManager.requireAuthentication
def deleteUserHandler():
    """Deletes a user and redirects them home"""
    user = authManager.getUserData()
    print("delete", user["id"], file = sys.stderr)
    if user:
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
    This is invoked when a user logs out, immediately before user context is destroyed.
    """
    user = authManager.getUserData()
    print("User signed out: " + user["name"], file=sys.stderr)


@application.route('/file-manager', methods=['GET'])
@authManager.enableAuthentication
def fileManagerGetHandler():

    user = authManager.getUserData();
    if not user:
        return 401;
    id = user['id']

    fileManagerRendered = fileManagerTemplate.render()
    return bodyTemplate.render(
        title="File Manager",
        body=fileManagerRendered,
        user=user,
        location=request.url)


@application.route('/file-delete', methods=['POST'])
@authManager.requireAuthentication
def fileListDeleteHander():
    user = authManager.getUserData()
    fid = int(request.form['file'])
    id = user['id']

    # Find the file in S3
    try:
        with dataSessionMgr.session_scope() as dbSession:
            file1 = query.getFileById(dbSession,fid)
            file1 = query.extractOutput(file1)
    except Exception as e:
        flash("An unexpected error occurred while finding the file in our cloud storage. "\
                + "Please try again later.<br/><br/>", e);
        return redirect(url_for("fileListGetHandler"))

    # Delete the file from S3
    key = file1['cloud_key']
    try:
        s3client.delete_object(Bucket=bucket_name,Key=key)
    except Exception as e:
        flash("An unexpected error occurred while removing the file from our cloud storage. "\
                + "Please try again later.<br/><br/>", e);
        return redirect(url_for("fileListGetHandler"))

    # Delete the file by fileID in RDS
    try:
        with dataSessionMgr.session_scope() as dbSession:
            file = query.getFileById(dbSession,fid)
            if file:
                dbSession.delete(file)
    except Exception as e:
        flash("An unexpected error occurred while removing this file from our database. "\
                + "Please try again later.<br/><br/>", e);
        return redirect(url_for("fileListGetHandler"))

    return redirect(url_for("fileListGetHandler"))


@application.route('/file-list', methods=['GET'])
@authManager.requireAuthentication
def fileListGetHandler():
    user = authManager.getUserData()

    id = user['id']
    #Get the user's profile from the DB and zip it first
    with dataSessionMgr.session_scope() as dbSession:
        files = query.getFilesByUser(dbSession,id)
        files = query.extractOutput(files)

    if not files:
        files = [];

    fileManagerRendered = fileListTemplate.render(files=files)
    return bodySimpleTemplate.render(
        title="File Manager",
        body=fileManagerRendered)


@application.route('/file-list', methods=['POST'])
@authManager.requireAuthentication
def fileListPostHandler():
    user = authManager.getUserData()

    # Get the user session and file to upload
    id = user['id']
    file = request.files['file']

    # If user does not select file, browser also submit a empty part without filename
    if not file or file.filename.strip() == '':
        flash('You must select a file in order to upload one.')
        return redirect(request.url)

    # Determine shortened file name (secure)
    filename = secure_filename(file.filename.strip())
    while (len(filename) > 50):
        cutString = len(filename) % 50
        filename = filename[cutString:len(filename)]

    # Determine the S3 key
    try:
        myUuid = uuid.uuid4().hex
        fn, fileExtension = os.path.splitext(filename)
        key = id + "/" + myUuid + fileExtension.lower()

        # If the file already exists, we need to warn and abort
        try:
            with dataSessionMgr.session_scope() as dbSession:
                checkFile = query.getFileByName(dbSession,id,filename)
                checkFile = query.extractOutput(checkFile)
        except Exception as e:
            flash("Something happen", e);
            return e

        if checkFile is not None:
            flash("That file already exists. Please delete it first and then re-upload. " \
                    + "This will <b>remove</b> any attachments you have made to this file.")
            return redirect(request.url)

        # Since the file does not exist, we will upload it now
        s3client.upload_fileobj(file, bucket_name, key, ExtraArgs={"ACL": "public-read", "ContentType": file.content_type})
        url = "https://s3-us-west-2.amazonaws.com/condensation-forum/" + key

        storeToDB(id, url, key, filename)

        return redirect(request.url)
    except Exception as e:
        flash("An unexpected error occurred while uploading your file. Things to try: "\
                 + "<br/> - Rename the file to something shorter"\
                 + "<br/> - Make sure the file size is under 1 megabyte"\
                 + "<br/> - Make sure there are no special characters in the file name<br/><br/>", e);
        return redirect(request.url)

    # Redirect to end the POST handling the redirect can be to the same route or somewhere else
    return redirect(request.url)


def storeToDB(userID,url,key,filename):
    """This method is used to store the data uploaded into DB"""
    try:
        with dataSessionMgr.session_scope() as dbSession:
                 user = query.getUser(dbSession, userID)
                 file = schema.File(url=url, cloud_key=key, name=filename)
                 user.uploads.append(file)
    except Exception as e:
        flash("Something happen: ",e)
        return e


# Run Flask app now
if __name__ == "__main__":
    # Enable debug output, disable in prod
    application.debug = True
    application.run()
