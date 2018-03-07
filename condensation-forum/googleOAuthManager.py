"""
This enables authentication with Google accounts via OAuth2. Decorator functions enable locking flask endpoints to
unauthenticated users and loading their authentication context if it exists. Additional endpoints `/login` and
`/authorized` exist to assist a standard OAuth flow.
"""

from flask import Flask, redirect, url_for, request, session
from flask_oauthlib.client import OAuth
from functools import wraps
import sys

class GoogleOAuthManager(object):

    # Preconfigured Google OAuth2 connection details
    BASE_URL         = 'https://www.googleapis.com/oauth2/v1/'
    AUTHORIZE_URL    = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_PARAMS     = {'scope': 'https://www.googleapis.com/auth/userinfo.email'}
    ACCESS_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
    LOGIN_ROUTE      = '/login'
    LOGOUT_ROUTE     = '/logout'
    AUTHORIZED_ROUTE = '/authorized'

    # The OAuth client
    oath = None
    googleAuth = None

    # Cached user properties
    userRetrievalEnabled = False
    userData = None

    def __init__(self, flaskApp, clientId, clientSecret):

        # OAuth setup
        self.oauth = OAuth(flaskApp)
        self.googleAuth = self.oauth.remote_app('google',
                base_url             = self.BASE_URL,
                authorize_url        = self.AUTHORIZE_URL,
                request_token_url    = None,
                request_token_params = self.TOKEN_PARAMS,
                access_token_url     = self.ACCESS_TOKEN_URL,
                access_token_method  = 'POST',
                access_token_params  = None,
                consumer_key         = clientId,
                consumer_secret      = clientSecret)

        @flaskApp.route(self.LOGOUT_ROUTE, methods=['GET'])
        def logoutHandler():
            """
            Logs out the user, then redirects them to the specified 'redirect' query string
            """
            redirectUrl = request.args.get('redirect', default = "/")
            session.clear()
            return redirect(redirectUrl)

        @flaskApp.route(self.LOGIN_ROUTE, methods=['GET'])
        def loginHandler():
            """
            Returns the authorization redirect for the user.
            """
            redirectUrl = request.args.get('redirect', default = None)
            if redirectUrl != None:
                session['userRedirect'] = redirectUrl

            callback = url_for('authorizedHandler', _external = True)
            return self.googleAuth.authorize(callback = callback)

        @flaskApp.route(self.AUTHORIZED_ROUTE, methods=['GET'])
        def authorizedHandler():
            """
            User is authorized, set up the session
            """
            try:
                response = self.googleAuth.authorized_response()
            except:
                return "Insufficient information was provided to authorize a user."

            # Handle failures
            if response is None:
                return 'Access denied: reason=%s error=%s' % (
                    request.args['error_reason'],
                    request.args['error_description']
                )

            # Gather information about this user
            session['accessToken'] = response['access_token']
            me = self.googleAuth.get('userinfo', token = {'access_token': session['accessToken']})
            session['userName'] = me.data['name']
            session['userId'] = me.data['id']
            session['userPicture'] = me.data['picture']

            # Redirect the user to where they requested to be, otherwise redirect to home
            if 'userRedirect' in session:
                redirectUrl = session['userRedirect']
            else:
                redirectUrl = "/"
            return redirect(redirectUrl)

        @self.googleAuth.tokengetter
        def getGoogleAuthToken():
            """
            googleAuth will automatically use this method to retrieve a token for transactions.
            """
            return session['access_token']

    def requireAuthentication(self, func):
        """
        Decorator for a Flask route that requires Google authentication before being accessed. The route will never
        execute if authentication does not have a valid context. The user is redirected back to this route after being
        authenticated.
        """
        # This function REPLACES the original, and does auth first!
        @wraps(func)
        def newAuthFunc():
            access_token = session.get('accessToken')
            if access_token is None:
                session['userRedirect'] = request.url_rule.rule
                return redirect(self.LOGIN_ROUTE)
            else:
                self.__populateUserData()
                self.userRetrievalEnabled = True
                toReturn = func()
                self.__clearUserData()
                self.userRetrievalEnabled = False
                return toReturn

        # Return the auth-enhanced function, which nests the original
        return newAuthFunc

    def enableAuthentication(self, func):
        """
        Decorator for a Flask route that enables Google authentication. The route should check user data exists before
        fetching any properties.
        """
        # This function REPLACES the original, and does auth first!
        @wraps(func)
        def newFunc():
            access_token = session.get('accessToken')

            if access_token is not None:
                self.__populateUserData()

            self.userRetrievalEnabled = True
            toReturn = func()
            self.__clearUserData()
            self.userRetrievalEnabled = False
            return toReturn

        # Return the auth-enhanced function, which nests the original
        return newFunc

    def __enforceRetrievalEnabled(self):
        if not self.userRetrievalEnabled:
            raise Exception("A call to user data was made outside of an authentication-enabled context")

    def __populateUserData(self):
        """
        Populates the contents of the user data from the current session.
        """
        self.userData = {
            'name':    session['userName'],
            'id':      session['userId'],
            'picture': session['userPicture']
        }

    def __clearUserData(self):
        """
        Erases user data at the end of an enable session
        """
        self.userData = None

    def getUserData(self):
        """
        Get the user data or None (be sure to check)
        """
        self.__enforceRetrievalEnabled()
        return self.userData
