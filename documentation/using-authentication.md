
# Using Google OAuth2 for Authentication

Users are authenticated with Google using OAuth2. This is done with a custom class called GoogleOAuthManager. This is
not a static class, and should be constructed after the Flask app is constructed. All mentions of googleOAuthManager
below refer to an instance of GoogleOAuthManager.

When a user accesses a Flask route (endpoint) decorated with
`@googleOAuthManager.enableAuthentication`, they have access to the authentication context. If a Flask route is
decorated with `@googleOAuthManager.requireAuthentication` then the user is automatically forced to authenticate
before they can access that endpoint. The former is ideal for web pages where content is displayed in read-only format
until a user chooses to sign in. The latter is ideal for user settings pages, or pages with restricted access.

If a user wants to authenticate at their own will, they may be directed to `/login` and the
`GoogleOAuthManager` instance which controls that endpoint will take care of the details. The optional query parameter
`?redirect=url` specifies the URL the user will be directed back to once the action completes. The default URL is
`/`.

If a user wants to end their authentication, the may be directed to `/logout` and the
`GoogleOAuthManager` instance which controls that endpoint will take care of the details. The optional query parameter
`?redirect=url` specifies the URL the user will be directed back to once the action completes. The default URL is
`/`.

What if a user signs out of Google and not this website? This is okay. We do not use OAuth to
access resources externally, we are only using it for user details. Even if the token expires, our session will continue
to work seamlessly until the user explicitly requests to log out.

To access user details, a decorated route function may use `googleOAuthManager.getUserData()`. This will return `None`
if there is no logged-in user. This will raise an exception is called outside of a decorated route function. The
dictionary returned for a valid user is formatted as follows:
```
{
    "id":      "21-character-primary-identifier",
    "name":    "user-chosen-name",
    "picture": "url-to-a-profile-picture",
    "email":   "email.address@email.llama"
}
```

Lastly, our app may need to do some preparation or provisioning upon user login, or housekeeping upon user logout. This
is handled with `@googleOAuthManager.loginCallback` and `logoutCallback` respectively. Decorate a function with these
(limit is 1 each) and the decorated function will be called with a valid user context directly after login, or
immediately before logout. Attempting to assign more than one callback for login or logout will result in an exception.
