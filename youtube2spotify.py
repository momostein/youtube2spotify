# Main flask app
#
# use this command to start the celery worker:
# celery -A youtube2spotify.celery worker --pool=eventlet --loglevel=info

import flask
import secret_key
import youtube
import spotify
import celery.exceptions as cex

from flask_celery import make_celery

app = flask.Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='amqp://guest:guest@localhost:5672',
    CELERY_RESULT_BACKEND='rpc://guest:guest@localhost:5672'
)

celery = make_celery(app)

app.secret_key = secret_key.get(True)

app.register_blueprint(youtube.youtube)
app.register_blueprint(spotify.spotifyBP)

spotify.oauth.init_app(app)


@app.route("/")
def index():
    return "Index page"


@app.route("/process/<name>")
def process(name):

    result = reverse.delay(name)

    try:
        return result.wait(timeout=2)
    except cex.TimeoutError as e:
        return str(e)


@celery.task(name='celery_example.reverse')
def reverse(string):
    return string[::-1]


if __name__ == "__main__":
    app.run(host='localhost', port=8090, debug=True, ssl_context='adhoc')
