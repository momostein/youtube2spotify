# Youtube API wrapper and a flask blueprint for the authentication

import flask
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

youtube = flask.Blueprint('youtube', __name__, url_prefix='/youtube')


@youtube.route('/')
def index():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('youtube.authorize'))

    client = get_authenticated_service()

    return channels_list(client,
                         part='snippet,id',
                         forUsername='vloepser')


@youtube.route('/list')
def list():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('youtube.authorize'))

    client = get_authenticated_service()

    return playlists_list(client,
                          part='snippet,id',
                          channelId='UC3N_01dmY6VlPPlfi_XsFcg')


@youtube.route('/videos')
def videos():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('youtube.authorize'))

    client = get_authenticated_service()

    return playlistItems_list(client,
                              part='snippet,contentDetails',
                              playlistId='PLZh_gsoIZWHoU8Diy2MpsDXWKGoPF-Kya',
                              maxResults=10)


@youtube.route('/search')
def search():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('youtube.authorize'))

    client = get_authenticated_service()

    return search_list(client,
                       part='snippet',
                       q='vloepser steven',
                       type='playlist')


@youtube.route('/allvideos')
def allVideos():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('youtube.authorize'))

    client = get_authenticated_service()

    videos = playlistItems_allItems(client,
                                    part='snippet',
                                    playlistId='PLZh_gsoIZWHoU8Diy2MpsDXWKGoPF-Kya')

    out = ""
    for video in videos:
        out += video["snippet"]["title"] + '<br>'

    return out


@youtube.route('/authorize')
def authorize():
    # Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow
    # steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = flask.url_for('youtube.oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
        # This parameter enables offline access which gives your application
        # both an access and refresh token.
        access_type='offline',
        # This parameter enables incremental auth.
        include_granted_scopes='true')

    # Store the state in the session so that the callback can verify that
    # the authorization server response.
    flask.session['state'] = state

    return flask.redirect(authorization_url)


@youtube.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verify the authorization server response.
    state = flask.session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('youtube.oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store the credentials in the session.
    # ACTION ITEM for developers:
    #     Store user's access and refresh tokens in your data store if
    #     incorporating this code into your real app.
    credentials = flow.credentials
    flask.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    return flask.redirect(flask.url_for('youtube.index'))


@youtube.route('/revoke')
def revoke():
    out = "Not logged in"

    if 'credentials' in flask.session:
        credentials = flask.session.pop('credentials', None)

        r = requests.post('https://accounts.google.com/o/oauth2/revoke',
                          params={'token': credentials['token']},
                          headers={'content-type': 'application/x-www-form-urlencoded'})

        out = "logged out, status code {:d}".format(r.status_code)

    return out


@youtube.route('/logout')
def logout():
    flask.session.pop('credentials', None)

    return "Logged out"


def channels_list(client, **kwargs):
    response = client.channels().list(
        **kwargs
    ).execute()

    return flask.jsonify(**response)


def playlists_list(client, **kwargs):
    response = client.playlists().list(
        **kwargs
    ).execute()

    return flask.jsonify(**response)


def playlistItems_list(client, **kwargs):
    response = client.playlistItems().list(
        **kwargs
    ).execute()

    return flask.jsonify(**response)


def search_list(client, **kwargs):
    response = client.search().list(
        **kwargs
    ).execute()

    return flask.jsonify(**response)


def playlistItems_allItems(client, part, playlistId):
    page = 1

    print("Requesting page", page)
    response = response = client.playlistItems().list(
        part=part, playlistId=playlistId, maxResults=50
    ).execute()

    print('items:', len(response['items']))

    for item in response['items']:
        yield item

    while 'nextPageToken' in response:
        token = response['nextPageToken']

        page += 1
        print("Requesting page", page)

        response = client.playlistItems().list(
            part=part, playlistId=playlistId, pageToken=token, maxResults=50
        ).execute()

        print('items:', len(response['items']))

        for item in response['items']:
            yield item


def get_authenticated_service():
    if 'credentials' not in flask.session:
        raise Exception("Program not yet authenticated")

    # Load the credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    return googleapiclient.discovery.build(API_SERVICE_NAME,
                                           API_VERSION,
                                           credentials=credentials)
