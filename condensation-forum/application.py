"""
An AWS Python3+Flask web app.
"""

from flask import Flask, redirect, url_for, request, session
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

    homeRendered = homeTemplate.render()
    user = authManager.getUserData()
    if user == None:
        homeRendered += "<br/><br/>User is not logged in"
    else:
        homeRendered += "<br/><br/>User is: " + user['name']

    with dataSessionMgr.session_scope() as dbSession:
        threads = query.getThreadsByCommentTime(dbSession)
        if threads:
            for thread in threads:
                homeRendered += "<p><b>%s</b> %s</p>" % (thread.heading, thread.user.name) 
        else:
            homeRendered += "<p>No threads found</p>"
    return bodyTemplate.render(body = homeRendered, title = "Test Home", user = user)


@application.route('/', methods=['POST'])
@authManager.requireAuthentication
def indexPostHandler():
    """
    Outputs the user's submission to console and returns index GET response.
    """

    print("User's first box: " + request.form["box1"], file=sys.stderr)
    print("User's second box: " + request.form["box2"], file=sys.stderr)

    return indexGetHandler()


# Load up Jinja2 templates
templateLoader = jinja2.FileSystemLoader(searchpath="./templates/")
templateEnv = jinja2.Environment(loader=templateLoader)

bodyTemplate = templateEnv.get_template("body.html")
homeTemplate = templateEnv.get_template("home.html")

# Run Flask app now
if __name__ == "__main__":
    # Enable debug output, disable in prod
    application.debug = True
    application.run()
