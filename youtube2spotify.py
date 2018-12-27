# Main flask app
import eventlet
eventlet.monkey_patch()

import time
from threading import Thread

import flask
from flask_socketio import SocketIO, emit, join_room, disconnect
import os

import secret_key
import youtube_authlib as youtube
import spotify

app = flask.Flask(__name__)
app.secret_key = secret_key.get(True)

app.register_blueprint(youtube.youtubeBP)
app.register_blueprint(spotify.spotifyBP)
spotify.oauth.init_app(app)
youtube.oauth.init_app(app)

socketio = SocketIO(app)

thread = None


@app.route("/")
def index():
    return "Index page"


@app.route('/socket')
def socket():
    global thread
    if thread is None:
        thread = Thread(target=background_stuff)
        thread.start()
    return flask.render_template('socket.html')


def background_stuff():
    print('In background_stuff')
    while True:
        time.sleep(1)
        t = str(time.process_time())
        socketio.emit('message', {'data': 'this is data', 'time': t}, namespace='/test')


if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    socketio.run(app, host='localhost', port=8090, debug=True)
