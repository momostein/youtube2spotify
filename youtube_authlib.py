# Youtube API wrapper and a flask blueprint for the authentication

import flask
import requests
import json

from functools import wraps
from authlib.flask.client import OAuth
from authlib.client.errors import TokenExpiredError, MissingTokenError

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "youtube_secret.json"
SESSION_KEY = 'youtube_token'

with open(CLIENT_SECRETS_FILE, 'r') as f:
    CLIENT = json.load(f)

oauth = OAuth()


def fetch_token():
    return flask.session.get(SESSION_KEY)


def requires_auth(f):

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_url = flask.url_for('youtube.authorize')

        if SESSION_KEY not in flask.session:
            return flask.redirect(auth_url)

        try:
            return f(*args, **kwargs)

        except TokenExpiredError as error:
            print(error)
            return flask.redirect(auth_url)

        except MissingTokenError as error:
            print(error)
            return flask.redirect(auth_url)

    return decorated


youtube = oauth.register(
    'youtube',
    api_base_url='https://www.googleapis.com',
    access_token_url='https://www.googleapis.com/oauth2/v4/token',
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    authorize_params={'scope': 'https://www.googleapis.com/auth/youtube.force-ssl'},
    client_id=CLIENT['client_id'],
    client_secret=CLIENT['client_secret'],
    fetch_token=fetch_token
)


# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

youtubeBP = flask.Blueprint('youtube', __name__, url_prefix='/youtube')


@youtubeBP.route('/')
@requires_auth
def index():
    if SESSION_KEY not in flask.session:
        return flask.redirect(flask.url_for('youtube.authorize'))

    return channels_list(part='snippet,id',
                         forUsername='vloepser')


@youtubeBP.route('/authorize')
def authorize():
    callback = flask.url_for('youtube.oauth2callback',
                             next=flask.request.args.get(
                                 'next') or flask.request.referrer or None,

                             _external=True)

    return youtube.authorize_redirect(callback)


@youtubeBP.route('/oauth2callback')
def oauth2callback():
    token = youtube.authorize_access_token()

    print(token)

    flask.session[SESSION_KEY] = token
    return flask.redirect(flask.url_for('youtube.index', next=flask.request.args.get('next')))


@youtubeBP.route('/revoke')
def revoke():
    out = "Not logged in"

    if SESSION_KEY in flask.session:
        credentials = flask.session.pop(SESSION_KEY, None)

        print(credentials)

        r = requests.post('https://accounts.google.com/o/oauth2/revoke',
                          params={'token': credentials['access_token']},
                          headers={'content-type': 'application/x-www-form-urlencoded'})

        out = "logged out, status code {:d}".format(r.status_code)

    return out


@youtubeBP.route('/logout')
def logout():
    flask.session.pop(SESSION_KEY, None)

    return "Logged out"


def channels_list(**kwargs):
    response = youtube.get('/youtube/v3/channels', params=kwargs).json()

    return flask.jsonify(**response)
