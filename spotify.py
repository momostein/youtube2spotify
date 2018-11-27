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
    base_url='https://api.spotify.com',
    request_token_url=None,
    access_token_url='https://accounts.spotify.com/api/token',
    authorize_url='https://accounts.spotify.com/authorize',
    app_key='SPOTIFY',
    consumer_key=CLIENT['client_id'],
    consumer_secret=CLIENT['client_secret']
)

spotifyBP = flask.Blueprint('spotify', __name__, url_prefix='/spotify')


@spotifyBP.route('/')
def index():
    if SESSION_KEY not in flask.session:
        return flask.redirect(flask.url_for('spotify.authorize'))

    me = spotify.get('/v1/me')

    try:
        return 'Logged in as id={0} name={1} redirect={2}'.format(
            me.data['id'],
            me.data['name'],
            flask.request.args.get('next')
        )
    except KeyError as error:
        print(error)
        return flask.jsonify(me.data)


@spotifyBP.route('/authorize')
def authorize():
    callback = flask.url_for('spotify.oauth2callback',
                             next=flask.request.args.get(
                                 'next') or flask.request.referrer or None,

                             _external=True)

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

    flask.session[SESSION_KEY] = (resp['access_token'], '')
    return flask.url_for('spotify.index', next=flask.request.args.get('next'))


@spotify.tokengetter
def get_spotify_oauth_token():
    return flask.session.get(SESSION_KEY)
