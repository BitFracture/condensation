"""
An AWS Python3+Flask web app.
"""

from flask import Flask, redirect, url_for, request, session, flash
from flask_oauthlib.client import OAuth
import boto3
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
from data import query




# This is the EB application, calling directly into Flask
application = Flask(__name__)
# Loads config from file or environment variable
config = ConfigLoader("config.local.json")
# Enable encrypted session, required for OAuth to stick
application.secret_key = config.get("sessionSecret")

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

#database connection
dataSessionMgr = SessionManager(
        config.get("dbUser"),
        config.get("dbPassword"),
        config.get("dbEndpoint"))

@application.route('/', methods=['GET'])
@authManager.enableAuthentication
def indexGetHandler():
    """
    Returns the template "home" wrapped by "body" served as HTML
    """
    threads = None
    #grab threads ordered by time, and zip them with some usernames
    with dataSessionMgr.session_scope() as dbSession:
        threads = query.getThreadsByCommentTime(dbSession)
        urls = [url_for("threadGetHandler", tid=thread.id) for thread in threads]
        usernames = [thread.user.name for thread in threads]
        threads = query.extractOutput(threads)



    homeRendered = homeTemplate.render(threads=threads, urls=urls, usernames=usernames)

    user = authManager.getUserData()

    return bodyTemplate.render(body = homeRendered, user = user )


@application.route('/', methods=['POST'])
@authManager.requireAuthentication
def indexPostHandler():
    """
    Outputs the user's submission to console and returns index GET response.
    """

    print("User's first box: " + request.form["box1"], file=sys.stderr)
    print("User's second box: " + request.form["box2"], file=sys.stderr)

    return indexGetHandler()

@application.route("/thread/<int:tid>)")
def threadGetHandler(tid):
    #grab the thread with attachments
    thread = None
    with dataSessionMgr.session_scope() as dbSession:
        thread = query.getThreadById(dbSession, tid)
        thread_attachments = query.extractOutput(thread.attachments)
        op = thread.user.name
        post_attachments = query.extractOutput(thread.attachments)
        comments = query.getCommentsByThread(dbSession, thread.id)
        comment_attachments = [query.extractOutput(comment.attachments) for comment in comments]
        comment_users = [comment.user.name for comment in comments]
        comments = query.extractOutput(comments)
        thread = query.extractOutput(thread)
        
    threadRendered = threadTemplate.render(
            thread = thread, 
            thread_attachments=thread_attachments,
            op=op, 
            comments=comments, 
            comment_attachments=comment_attachments, 
            comment_users=comment_users)
    return bodyTemplate.render(body=threadRendered)


# Load up Jinja2 templates
templateLoader = jinja2.FileSystemLoader(searchpath="./templates/")
templateEnv = jinja2.Environment(loader=templateLoader)
#we want to zip collections in view
templateEnv.globals.update(zip=zip)


bodyTemplate = templateEnv.get_template("body.html")
homeTemplate = templateEnv.get_template("home.html")
threadTemplate = templateEnv.get_template("thread.html")

# Run Flask app now
if __name__ == "__main__":
    # Enable debug output, disable in prod
    application.debug = True
    application.run()
