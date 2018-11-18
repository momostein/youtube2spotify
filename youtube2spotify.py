# Main flask app

import flask
import secret_key
import youtube

app = flask.Flask(__name__)

app.secret_key = secret_key.get(True)

app.register_blueprint(youtube.youtube)


@app.route("/")
def index():
    return "Index page"


if __name__ == "__main__":
    app.run(host='localhost', port=8090, debug=True, ssl_context='adhoc')
