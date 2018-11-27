# Spotify API blueprint and wrapper

import flask
import json

from flask_oauthlib.client import OAuth, OAuthException


CLIENT_SECRETS_FILE = 'spotify_secret.json'
SESSION_KEY = 'spotify_token'

with open(CLIENT_SECRETS_FILE, 'r') as f:
    CLIENT = json.load(f)

oauth = OAuth()

spotify = oauth.remote_app(
    'spotify',
    # Change the scope to match whatever it us you need
    # list of scopes can be found in the url below
    # https://developer.spotify.com/web-api/using-scopes/
    request_token_params={'scope': 'user-read-email'},
    base_url='https://accounts.spotify.com',
    request_token_url=None,
    access_token_url='/api/token',
    authorize_url='https://accounts.spotify.com/authorize',
    app_key='SPOTIFY'
)

spotifyBP = flask.Blueprint('spotify', __name__, url_prefix='/spotify')


@spotifyBP.route('/')
def index():
    if 'spotifyCred' not in flask.session:
        return flask.redirect(flask.url_for('spotify.authorize'))


@spotifyBP.route('/authorize')
def authorize():
    callback = flask.url_for('spotify.oauth2callback', _external=True)

    return spotify.authorize(callback=callback)


@spotifyBP.route('/oauth2callback')
def oauth2callback():
    resp = spotify.authorized_response()

    if resp is None:
        return 'Access denied: reason={0} error={1}'.format(
            flask.request.args['error_reason'],
            flask.request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: {0}'.format(resp.message)

    flask.session['SESSION_KEY'] = (resp['access_token'], '')
    me = spotify.get('/me')
    return 'Logged in as id={0} name={1} redirect={2}'.format(
        me.data['id'],
        me.data['name'],
        flask.request.args.get('next')
    )


@spotify.tokengetter
def get_spotify_oauth_token():
    return flask.session.get('SESSION_KEY')
