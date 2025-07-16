import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import datetime

# Get credentials from environment variables
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
REFRESH_TOKEN = os.getenv('SPOTIPY_REFRESH_TOKEN')

# Set up auth manager
auth_manager = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope='playlist-read-private playlist-modify-private playlist-modify-public'
)

# Refresh access token using refresh token directly
token_info = auth_manager.refresh_access_token(REFRESH_TOKEN)
access_token = token_info['access_token']
sp = spotipy.Spotify(auth=access_token)

# Get user ID
user_id = sp.current_user()['id']

# Get current week's Monday and Sunday
today = datetime.date.today()
monday = today - datetime.timedelta(days=today.weekday())
sunday = monday + datetime.timedelta(days=6)
playlist_name = f"DWA {monday.month}/{monday.day}–{sunday.month}/{sunday.day}"

# Find Discover Weekly
discover_weekly_id = None
playlists = sp.current_user_playlists(limit=50)
for playlist in playlists['items']:
    if playlist['name'] == 'Discover Weekly' and playlist['owner']['id'] == 'spotify':
        discover_weekly_id = playlist['id']
        break

if not discover_weekly_id:
    raise Exception("⚠️ Could not find Discover Weekly playlist.")

# Get tracks from Discover Weekly
tracks = sp.playlist_items(discover_weekly_id)
track_uris = [item['track']['uri'] for item in tracks['items'] if item['track']]

# Create new weekly playlist
new_playlist = sp.user_playlist_create(
    user=user_id,
    name=playlist_name,
    public=False,
    description=f"Auto-saved Discover Weekly for {monday.month}/{monday.day} to {sunday.month}/{sunday.day}"
)
new_playlist_id = new_playlist['id']

# Add tracks
if track_uris:
    sp.playlist_add_items(new_playlist_id, track_uris)
    print(f"✅ {len(track_uris)} tracks saved to '{playlist_name}'.")
else:
    print("⚠️ No tracks found in Discover Weekly.")
