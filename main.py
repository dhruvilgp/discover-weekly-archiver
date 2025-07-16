import spotipy
from spotipy.oauth2 import SpotifyOAuth
import datetime

# Replace with your credentials
CLIENT_ID = '155270cf325b4caeadc7b9b92b950642'
CLIENT_SECRET = '9aaf252a696d4e6bb55a1ff5c13ddafd'
REDIRECT_URI = 'http://127.0.0.1:8888/callback'

# Set up auth
scope = 'playlist-read-private playlist-modify-private playlist-modify-public'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scope
))

# Get current user's ID
user_id = sp.current_user()['id']

# Step 1: Get current week's Monday and Sunday
today = datetime.date.today()
monday = today - datetime.timedelta(days=today.weekday())         # Monday of current week
sunday = monday + datetime.timedelta(days=6)                      # Sunday of current week
playlist_name = f"DWA {monday.month}/{monday.day}–{sunday.month}/{sunday.day}"

# Step 2: Find Discover Weekly
discover_weekly_id = None
results = sp.current_user_playlists(limit=50)
for playlist in results['items']:
    if playlist['name'] == 'Discover Weekly' and playlist['owner']['id'] == 'spotify':
        discover_weekly_id = playlist['id']
        break

if not discover_weekly_id:
    raise Exception("⚠️ Could not find Discover Weekly playlist.")

# Step 3: Get tracks from Discover Weekly
tracks = sp.playlist_items(discover_weekly_id)
track_uris = [item['track']['uri'] for item in tracks['items'] if item['track']]

# Step 4: Create new weekly playlist
new_playlist = sp.user_playlist_create(
    user=user_id,
    name=playlist_name,
    public=False,
    description=f"Auto-saved Discover Weekly for {monday.month}/{monday.day} to {sunday.month}/{sunday.day}"
)
new_playlist_id = new_playlist['id']

# Step 5: Add tracks
if track_uris:
    sp.playlist_add_items(new_playlist_id, track_uris)
    print(f"✅ {len(track_uris)} tracks saved to '{playlist_name}'.")
else:
    print("⚠️ No tracks found in Discover Weekly.")
