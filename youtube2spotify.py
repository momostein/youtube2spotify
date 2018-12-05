# Main flask app

import flask

import secret_key
import youtube
import spotify
import genius

app = flask.Flask(__name__)

app.secret_key = secret_key.get(True)

app.register_blueprint(youtube.youtube)
app.register_blueprint(spotify.spotifyBP)
app.register_blueprint(genius.geniusBP)

spotify.oauth.init_app(app)
genius.oauth.init_app(app)


@app.route("/")
def index():
    return "Index page"


if __name__ == "__main__":
    app.run(host='localhost', port=8090, debug=True, ssl_context='adhoc')
