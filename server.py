import os
import spotipy
from urllib.parse import quote
from spotipy.oauth2 import SpotifyClientCredentials
from flask import Flask, request, render_template, jsonify, session, redirect

app = Flask(__name__, static_folder='public', template_folder='views')

app.secret_key = 'random string'

CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_BASE_URL = 'https://api.spotify.com'
API_VERSION = 'v1'
SPOTIFY_API_URL = f'{SPOTIFY_API_BASE_URL}/{API_VERSION}'

CLIENT_SIDE_URL = 'http://localhost'
PORT = 5000
REDIRECT_URI = f'{CLIENT_SIDE_URL}:{PORT}/callback/'
SCOPE = 'user-top-read'

auth_query_parameters = {
    'client_id': CLIENT_ID,
    'response_type': 'code',
    'redirect_uri': REDIRECT_URI,
    'scope': SCOPE
}


@app.route('/')
def homepage():
    if session.get('user'):
        return render_template('index.html')
    else:
        return render_template('index.html')


@app.route('/login')
def login_spotify():
    url_args = '&'.join(['{}={}'.format(key, quote(val, safe=''))
                         for key, val in auth_query_parameters.items()])
    auth_url = '{}/?{}'.format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)


@app.route('/callback/')
def callback():
    code = request.args['code']
    if code:
        spAuth = spotipy.oauth2.SpotifyOAuth(
            CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scope=SCOPE)
        token = spAuth.get_access_token(code)
        session['user'] = token['access_token']
        return redirect('/')


if __name__ == '__main__':
    app.run()
