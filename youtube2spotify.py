# Main flask app
import eventlet
eventlet.monkey_patch()

import time
import json
import os
import queue
from threading import Thread

import flask
from flask_socketio import SocketIO


import secret_key
import youtube_authlib as youtube
import spotify
import genius

app = flask.Flask(__name__)
app.secret_key = secret_key.get(True)

app.register_blueprint(youtube.youtubeBP)
app.register_blueprint(spotify.spotifyBP)
app.register_blueprint(genius.geniusBP)

spotify.oauth.init_app(app)
genius.oauth.init_app(app)
youtube.oauth.init_app(app)

socketio = SocketIO(app)

thread = None
convertThread = None

threads = []


@app.route("/")
def index():
    return "Index page"


@app.route('/socket')
def socket():
    global thread
    if thread is None or not thread.isAlive():
        thread = Thread(target=background_stuff)
        thread.start()
    return flask.render_template('socket.html')


@app.route('/asyncreq')
def asyncreq():
    # Wrap the target function to copy the request context
    target = flask.copy_current_request_context(async_request)
    thread = Thread(target=target)

    thread.start()

    threads.append(thread)

    return flask.render_template('asyncreq.html')


@app.route('/convert')
@youtube.requires_auth
def convert():
    global convertThread
    if convertThread is None or not convertThread.isAlive():
        # Wrap the target function to copy the request context
        target = flask.copy_current_request_context(convertplayist)
        convertThread = Thread(target=target, args=['PLZh_gsoIZWHoU8Diy2MpsDXWKGoPF-Kya'])
        convertThread.start()
        return 'thread started'

    return 'thread busy'


def background_stuff():
    print('In background_stuff')
    for i in range(15):
        time.sleep(1)
        t = '{} ({:d})'.format(str(time.process_time()), i + 1)
        socketio.emit('message', {'data': 'this is data', 'time': t}, namespace='/test')

    time.sleep(1)
    socketio.emit('message', {'data': 'this is data', 'time': 'Done!'}, namespace='/test')


def convertplayist(playlistId):
    print('Conversion started')

    target = flask.copy_current_request_context(pageGetter)

    pageQueue = queue.Queue()
    pageThread = Thread(target=target, args=['PLZh_gsoIZWHoU8Diy2MpsDXWKGoPF-Kya', pageQueue])
    pageThread.start()

    # Clear out the file
    with open('titles.txt', 'w') as title_file:
        pass

    while True:
        page = pageQueue.get()
        if page is None:
            break

        print('Got a page')

        with open('titles.txt', 'a', encoding='utf-8') as title_file:
            for item in page['items']:
                title = item['snippet']['title']

                title_file.write(title)
                title_file.write('\n')

        pageQueue.task_done()

    print('Conversion finished')


def pageGetter(playlistId, q):
    with open('pages.txt', 'w') as page_file:
        for i, page in enumerate(youtube.playlistItems_allPages(part='snippet', playlistId=playlistId)):
            q.put(page)
            print('On Page {:d}'.format(i + 1))
            page_file.write("Page {:d}\n".format(i + 1))
            page_file.write(json.dumps(page, sort_keys=True, indent=4))
            page_file.write('\n')

        # Wait for all pages to be processed
        q.join()

        # Terminate the queue
        q.put(None)


def async_request():
    print('Requesting')

    channels = youtube.channels_list(part='snippet,id',
                                     forUsername='vloepser')

    print('Requested:')
    print(json.dumps(channels, indent=4, sort_keys=True))

    time.sleep(2)

    socketio.emit('request', {'channels': json.dumps(channels)}, namespace='/youtube')


if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    socketio.run(app, host='localhost', port=8090, debug=True)
