
# Condensation Forum

Condensation Forum is a Python 3 web service in EC2 via Elastic Beanstalk.  

## Accessing The Deployed Service

The deployed web service lives at `condensation-forum.us-west-2.elasticbeanstalk.com`.

## Local Instance Prerequisites

 - Install Python 3.6 and PIP 3
 - Install virtual environment support: `pip3 install virtualenv --user`
 - Install GNU Make or manually execute the commands in Makefile when needed

## Deployment Prerequisites

 - Install Local Instance Prerequisites from above
 - Install AWS CLI from AWS wElastic Beanstalkite
 - Use `aws config` to connect to AWS account and region
 - Install Elastic Beanstalk CLI: `pip3 install awsebcli --user`
    - Read here for details: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html
 - Nav your shell to the `condensation-forum` folder
 - Have an Elastic Beanstalk instance to deploy to. Ex: `condensation-forum` is our deployed instance
 - Init deployment path: `eb init condensation-forum`
    - Choose region `us-west-2` which is Oregon
	- Do not set up CodeCommit, as we use GitHub and our own deploy script
 - Before deploying, confirm with group members. Run `eb deploy`
 - Quick deployment command `make deploy` is set up already
 - deploying the database is done seperately with th `generate_database` scripts

## Running the local server

 - In the `condensation-forum` folder, create a local config file called `config.local.json`<br/>
```
{
    "accessKey":         "AAAABBBBCCCCDDDDEEEE",
    "secretKey":         "aaaaaaaabbbbbbbbccccccccddddddddeeeeeeee",
    "region":            "us-west-2",
    "oauthClientId":     "000000000000000000000000000000000000000000000.apps.googleusercontent.com",
    "oauthClientSecret": "111122223333444455556666",
    "sessionSecret":     "11aa22bb33cc44dd55ee77hh",
    "dbEndpoint": "www.example.com"
    "dbUser": "pg_sql",
    "dbPassword": "password"
}
```
 - If you have GNU Make, use `make run`
 - If you do not, run `./scripts/run.sh` or `scripts\run.bat`
 - Note: You may need to `chmod u+x run.sh` before you can run in \*nix
 - Note: You should run scripts from the Git root, not from inside the scripts folder
 - Access the site at `http://localhost:5000` or OAuth redirects won't work

# Architecture

## RDS Schema


## File Uploads


## Authentication

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
    "picture": "url-to-a-profile-picture"
}
```

Lastly, our app may need to do some preparation or provisioning upon user login, or housekeeping upon user logout. This
is handled with `@googleOAuthManager.loginCallback` and `logoutCallback` respectively. Decorate a function with these
(limit is 1 each) and the decorated function will be called with a valid user context directly after login, or
immediately before logout. Attempting to assign more than one callback for login or logout will result in an exception.

## Views and Rendering

Jinja2 and Flask are used to render HTML templates into responses and send them at the appropriate times.

## Deployment

The Python3 application is deployed to EC2 via Elastic Beanstalk. The configuration steps are listed above and are compiled into bash and batch scripts.

To redeploy the database follow the same procedure.



# Report Components

## Design Diagrams

### Entity Relationship Diagram

![alt text](images/data_layer_hi_rez.png)

## Scaling

## Monitoring
