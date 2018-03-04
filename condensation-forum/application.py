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


config = ConfigLoader("config.local.json")

# This is the EB application, calling directly into Flask
application = Flask(__name__)

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
oauth = OAuth(application)
googleAuth = oauth.remote_app('google',
        base_url = 'https://www.googleapis.com/oauth2/v1/',
        authorize_url = 'https://accounts.google.com/o/oauth2/auth',
        request_token_url = None,
        request_token_params = {
                'scope': 'https://www.googleapis.com/auth/userinfo.email'},
        access_token_url = 'https://accounts.google.com/o/oauth2/token',
        access_token_method = 'POST',
        access_token_params = None,
        consumer_key = config.get("oauthClientId"),
        consumer_secret = config.get("oauthClientSecret"))
tempToken = None


def requireAuthentication(func):
    # This function REPLACES the original, and does auth first!
    def newFunc():
        access_token = session.get('access_token')
        if access_token is None:
            return redirect(url_for('loginHandler'))
        else:
            print("User name is: " + session.get('user_name'), file=sys.stderr)
            return func()

    # Return the auth-enhanced function, which nests the original
    return newFunc


#@googleAuth.tokengetter
@application.route('/', methods=['GET'])
@requireAuthentication
def indexGetHandler():
    """
    Returns the template "home" wrapped by "body" served as HTML
    """

    print("SKINNY GOOSE", file=sys.stderr)

    #homeRendered = homeTemplate.render()
    response = authCacheTable.scan()
    homeRendered = json.dumps(response)
    return bodyTemplate.render(body = homeRendered, title = "Test Home")


@application.route('/', methods=['POST'])
def indexPostHandler():
    """
    Outputs the user's submission to console and returns index GET response.
    """

    print("User's first box: " + request.form["box1"], file=sys.stderr)
    print("User's second box: " + request.form["box2"], file=sys.stderr)

    return indexGetHandler()


@application.route('/google', methods=['GET'])
def authGetHandler():
    """
    Returns the template "testingAuth" wrapped by "body" served as HTML
    """

    authRendered = authTemplate.render()
    return bodyTemplate.render(body = authRendered, title = "Google Auth Test")


@application.route('/login', methods=['GET'])
def loginHandler():
    """
    Returns the template "testingAuth" wrapped by "body" served as HTML
    """
    callback = url_for('authorizedHandler', _external = True)
    return googleAuth.authorize(callback = callback)


@application.route('/authorized', methods=['GET'])
def authorizedHandler():
    """
    Returns the template "home" wrapped by "body" served as HTML
    """

    response = googleAuth.authorized_response()

    if response is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )

    global tempToken
    tempToken = response['access_token']
    session['access_token'] = tempToken
    me = googleAuth.get('userinfo', token = {'access_token': tempToken})
    session['user_name'] = me.data['name']

    homeRendered = "You are authed: " + json.dumps(me.data)
    return bodyTemplate.render(body = homeRendered, title = "Test Home")


@googleAuth.tokengetter
def get_google_oauth_token():
    """
    googleAuth will automatically use this method to retrieve a token for transactions.
    """
    return tempToken



# Load up Jinja2 templates
templateLoader = jinja2.FileSystemLoader(searchpath="./templates/")
templateEnv = jinja2.Environment(loader=templateLoader)

bodyTemplate = templateEnv.get_template("body.html")
homeTemplate = templateEnv.get_template("home.html")
authTemplate = templateEnv.get_template("testingAuth.html")

# Run Flask app now
if __name__ == "__main__":
    # Enable debug output, disable in prod
    application.debug = True
    application.secret_key = config.get("sessionSecret")
    print (application.secret_key, file=sys.stderr)
    application.run()
