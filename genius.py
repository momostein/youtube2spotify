# Genius API blueprint and wrapper

import flask
import json

from functools import wraps
from authlib.flask.client import OAuth
from authlib.client.errors import TokenExpiredError, MissingTokenError

CLIENT_SECRETS_FILE = 'genius_secret.json'
SESSION_KEY = 'genius_token'

with open(CLIENT_SECRETS_FILE, 'r') as f:
    CLIENT = json.load(f)


oauth = OAuth()


def fetch_spotify_token():
    return flask.session.get(SESSION_KEY)


def requires_auth(f):

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_url = flask.url_for('genius.authorize')

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


genius = oauth.register(
    'genius',
    # Change the scope to match whatever it us you need
    # list of scopes can be found in the url below
    # https://docs.genius.com/#/authentication-h1
    api_base_url='https://api.genius.com',
    access_token_url='https://api.genius.com/oauth/token',
    authorize_url='https://api.genius.com/oauth/authorize',
    client_id=CLIENT['client_id'],
    client_secret=CLIENT['client_secret'],
    fetch_token=fetch_spotify_token,
    client_kwargs={'scope': 'me'}
)

geniusBP = flask.Blueprint('genius', __name__, url_prefix='/genius')


@geniusBP.route('/')
@requires_auth
def index():
    me = genius.get('/account').json()

    return flask.jsonify(me)


@geniusBP.route('/authorize')
def authorize():
    callback = flask.url_for('genius.oauth2callback',
                             next=flask.request.args.get(
                                 'next') or flask.request.referrer or None,

                             _external=True)

    return genius.authorize_redirect(callback)


@geniusBP.route('/oauth2callback')
def oauth2callback():
    token = genius.authorize_access_token()

    print(token)

    flask.session[SESSION_KEY] = token
    return flask.redirect(flask.url_for('genius.index', next=flask.request.args.get('next')))
