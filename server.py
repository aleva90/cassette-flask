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

spAuth = spotipy.oauth2.SpotifyOAuth(
    CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scope=SCOPE)


@app.route('/')
def homepage():
    if session.get('user'):
        if spAuth._is_token_expired(session.get('user')):
            session.pop('user', None)
            return redirect('/')

        sp = spotipy.Spotify(auth=session.get('user')['access_token'])
        results = sp.current_user_top_tracks(limit=5, time_range='medium_term')
        top_songs = [[res['name'][:20], res['artists'][0]['name'][:20]]
                     for res in results['items']]
        user_info = sp.current_user()
        data = {
            'top_songs': top_songs,
            'name': user_info['display_name'].split(' ')[0],
            'followers': user_info['followers']['total'],
        }
        return render_template('cassette.html', **data)
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
        token = spAuth.get_access_token(code)
        session['user'] = token
        return redirect('/')


if __name__ == '__main__':
    app.run()
