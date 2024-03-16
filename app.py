from flask import Flask, render_template, redirect, url_for, request, session
from spotipy import oauth2, Spotify
import spotipy
import os

class Swipify:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = "random"
        self.sp_oauth = oauth2.SpotifyOAuth(
            'a8583822cef2478ca27448f3882066c3', 
            '7365a5b6693a499db6bf445cd34ca2a', 
            'http://localhost:5000/callback', 
            scope='playlist-modify-private user-top-read'
        )

    def index(self):
        return render_template('index.html')

    def login(self):
        auth_url = self.sp_oauth.get_authorize_url()
        return redirect(auth_url)

    def callback(self):
        code = request.args.get('code')
        token_info = self.sp_oauth.get_access_token(code)
        access_token = token_info['access_token']

        # Store the access token and user ID in the session
        session['access_token'] = access_token
        sp = spotipy.Spotify(auth=access_token)
        current_user = sp.current_user()
        session['user_id'] = current_user['id']

        return redirect(url_for('create_playlist'))

    def create_playlist(self):
        access_token = session.get('access_token')
        user_id = session.get('user_id')
        sp = spotipy.Spotify(auth=access_token)

        if request.method == 'POST':
            playlist_name = request.form['playlist_name']
            sp.user_playlist_create(user=user_id, name=playlist_name, public=False)
            return "Playlist created successfully!"

        return render_template('create_playlist.html')

    def recommended_songs(self):
        access_token = session.get('access_token')
        sp = spotipy.Spotify(auth=access_token)

        # Fetch user's top tracks to use as seed tracks for recommendations
        top_tracks = sp.current_user_top_tracks(limit=5, time_range='short_term')
        seed_tracks = [track['id'] for track in top_tracks['items']]

        # Get recommended tracks based on the seed tracks
        recommended_tracks = sp.recommendations(seed_tracks=seed_tracks, limit=1)

        # Extract relevant information for the recommended track
        recommended_song = recommended_tracks['tracks'][0]
        song_name = recommended_song['name']
        artist_name = recommended_song['artists'][0]['name']
        album_name = recommended_song['album']['name']
        song_image = recommended_song['album']['images'][0]['url']
        artist_image = sp.artist(recommended_song['artists'][0]['id'])['images'][0]['url']
        song_uri = recommended_song['uri']

        # Get the Spotify embed code for the recommended song with autoplay
        embed_code = f'<iframe src="https://open.spotify.com/embed/track/{song_uri.split(":")[-1]}" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media" autoplay="1"></iframe>'

        return render_template('recommended_song_embed.html', 
                            song_name=song_name, 
                            artist_name=artist_name, 
                            album_name=album_name, 
                            song_image=song_image, 
                            artist_image=artist_image, 
                            embed_code=embed_code)

    def add_song_to_playlist(self, playlist_id, song_uri):
        access_token = session.get('access_token')
        sp = spotipy.Spotify(auth=access_token)
        sp.playlist_add_items(playlist_id, [song_uri])

    def run(self):
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/login', 'login', self.login)
        self.app.add_url_rule('/callback', 'callback', self.callback)
        self.app.add_url_rule('/create_playlist', 'create_playlist', self.create_playlist, methods=['GET', 'POST'])
        self.app.add_url_rule('/add_song','add_song_to_playlist', self.add_song_to_playlist, methods=['GET', 'POST'])
        self.app.add_url_rule('/recommended_songs', 'recommended_songs', self.recommended_songs)
        self.app.run(debug=True)

if __name__ == '__main__':
    swipify = Swipify()
    swipify.run()
