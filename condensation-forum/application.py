"""
An AWS Python3+Flask web app.
"""

from flask import Flask, redirect, url_for, request
import boto3
import jinja2
from boto3.dynamodb.conditions import Key, Attr
import urllib.request
import json
import cgi
import time
import random
import sys


# This is the EB application, calling directly into Flask
application = Flask(__name__)

# Set up service handles
session  = boto3.session.Session(
        aws_access_key_id="---",
        aws_secret_access_key="---",
        aws_session_token=None,
        region_name="us-west-2",
        botocore_session=None,
        profile_name=None)

dynamodb = session.resource('dynamodb')
s3       = session.resource('s3')

# Example: authCacheTable = dynamodb.Table('person-table')
# Example: bucket = s3.Bucket('elasticbeanstalk-us-west-2-3453535353')


@application.route('/', methods=['GET'])
def indexGetHandler():
    """
    Returns the template "home" wrapped by "body" served as HTML
    """

    homeRendered = homeTemplate.render()
    return bodyTemplate.render(body = homeRendered, title = "Test Home")


@application.route('/', methods=['POST'])
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
