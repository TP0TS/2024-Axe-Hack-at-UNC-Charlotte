from flask import Flask, render_template, redirect, url_for, request, session
from spotipy import oauth2
import spotipy
import os

app = Flask(__name__)
app.secret_key = "random"
# Spotify API credentials
SPOTIPY_CLIENT_ID = 'a8583822cef2478ca27448f3882066c3'
SPOTIPY_CLIENT_SECRET = '7365a5b6693a499db6bf445cd34ca2a3'
SPOTIPY_REDIRECT_URI = 'http://localhost:5000/callback'

# Spotipy authentication
sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope='playlist-modify-private user-top-read')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']
    
    # Store the access token and user ID in the session
    session['access_token'] = access_token
    sp = spotipy.Spotify(auth=access_token)
    current_user = sp.current_user()
    session['user_id'] = current_user['id']
    
    return redirect(url_for('create_playlist'))

@app.route('/create_playlist', methods=['GET', 'POST'])
def create_playlist():
    access_token = session.get('access_token')
    user_id = session.get('user_id')
    sp = spotipy.Spotify(auth=access_token)
    
    if request.method == 'POST':
        playlist_name = request.form['playlist_name']
        sp.user_playlist_create(user=user_id, name=playlist_name, public=False)
        return "Playlist created successfully!"
    
    return render_template('create_playlist.html')


@app.route('/recommended_songs')
def recommended_songs():
    access_token = session.get('access_token')
    sp = spotipy.Spotify(auth=access_token)

    # Fetch user's top tracks to use as seed tracks for recommendations
    top_tracks = sp.current_user_top_tracks(limit=5, time_range='short_term')
    seed_tracks = [track['id'] for track in top_tracks['items']]

    # Get recommended tracks based on the seed tracks
    recommended_tracks = sp.recommendations(seed_tracks=seed_tracks, limit=10)

    # Extract relevant information for each recommended track
    recommended_songs = []
    for track in recommended_tracks['tracks']:
        song_name = track['name']
        artist_name = track['artists'][0]['name']
        album_name = track['album']['name']
        song_image = track['album']['images'][0]['url']
        artist_image = sp.artist(track['artists'][0]['id'])['images'][0]['url']
        recommended_songs.append({
            'song_name': song_name,
            'artist_name': artist_name,
            'album_name': album_name,
            'song_image': song_image,
            'artist_image': artist_image
        })

    return render_template('recommended_songs.html', recommended_songs=recommended_songs)

if __name__ == '__main__':
    app.run(debug=True)
