# Spotify API blueprint and wrapper

import flask
import json

from authlib.flask.client import OAuth


CLIENT_SECRETS_FILE = 'spotify_secret.json'
SESSION_KEY = 'spotify_token'

with open(CLIENT_SECRETS_FILE, 'r') as f:
    CLIENT = json.load(f)

oauth = OAuth()


def fetch_spotify_token():
    return flask.session.get(SESSION_KEY)


spotify = oauth.register(
    'spotify',
    # Change the scope to match whatever it us you need
    # list of scopes can be found in the url below
    # https://developer.spotify.com/web-api/using-scopes/
    request_token_params={'scope': 'user-read-email playlist-modify-public'},
    api_base_url='https://api.spotify.com',
    access_token_url='https://accounts.spotify.com/api/token',
    authorize_url='https://accounts.spotify.com/authorize',
    client_id=CLIENT['client_id'],
    client_secret=CLIENT['client_secret'],
    fetch_token=fetch_spotify_token
)

spotifyBP = flask.Blueprint('spotify', __name__, url_prefix='/spotify')


@spotifyBP.route('/')
def index():
    if SESSION_KEY not in flask.session:
        return flask.redirect(flask.url_for('spotify.authorize'))

    me = spotify.get('/v1/me').json()

    try:
        return 'Logged in as id={0} name={1} redirect={2}'.format(
            me['id'],
            me['display_name'],
            flask.request.args.get('next')
        )
    except KeyError as error:
        print(error)
        return flask.jsonify(me)


@spotifyBP.route('/authorize')
def authorize():
    callback = flask.url_for('spotify.oauth2callback',
                             next=flask.request.args.get(
                                 'next') or flask.request.referrer or None,

                             _external=True)

    return spotify.authorize_redirect(callback)


@spotifyBP.route('/oauth2callback')
def oauth2callback():
    token = spotify.authorize_access_token()

    print(token)

    flask.session[SESSION_KEY] = token
    return flask.redirect(flask.url_for('spotify.index', next=flask.request.args.get('next')))
