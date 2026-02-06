import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import datetime

def main():
    # Get credentials from environment variables
    CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
    CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
    REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
    REFRESH_TOKEN = os.getenv('SPOTIPY_REFRESH_TOKEN')

    # Validate environment variables
    if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, REFRESH_TOKEN]):
        raise ValueError("Missing required environment variables. Please check your secrets.")

    # Set up auth manager with refresh token
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope='playlist-read-private playlist-modify-private playlist-modify-public'
    )

    # Refresh access token using refresh token
    try:
        token_info = auth_manager.refresh_access_token(REFRESH_TOKEN)
        access_token = token_info['access_token']
    except Exception as e:
        print(f"❌ Error refreshing token: {e}")
        raise

    sp = spotipy.Spotify(auth=access_token)

    # Get user ID
    try:
        user_id = sp.current_user()['id']
        print(f"✅ Authenticated as user: {user_id}")
    except Exception as e:
        print(f"❌ Error getting user info: {e}")
        raise

    # Get current week's Monday and Sunday
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    sunday = monday + datetime.timedelta(days=6)
    playlist_name = f"DWA {monday.month}/{monday.day}–{sunday.month}/{sunday.day}"

    print(f"📅 Creating playlist: {playlist_name}")

    # Find Discover Weekly
    discover_weekly_id = None
    
    try:
        # Get all user playlists
        playlists = sp.current_user_playlists(limit=50)
        
        for playlist in playlists['items']:
            if playlist['name'] == 'Discover Weekly':
                discover_weekly_id = playlist['id']
                print(f"✅ Found Discover Weekly playlist: {discover_weekly_id}")
                break
        
        # If not found, try the common ID as fallback
        if not discover_weekly_id:
            print("⚠️ Discover Weekly not found in your playlists, trying common ID...")
            discover_weekly_id = '37i9dQZEVXcL2w06awwMAa'
    
    except Exception as e:
        print(f"⚠️ Error searching playlists: {e}. Using common Discover Weekly ID.")
        discover_weekly_id = '37i9dQZEVXcL2w06awwMAa'

    # Get tracks from Discover Weekly
    try:
        tracks = sp.playlist_items(discover_weekly_id)
        track_uris = [item['track']['uri'] for item in tracks['items'] if item['track']]
        print(f"✅ Found {len(track_uris)} tracks in Discover Weekly")
    except Exception as e:
        print(f"❌ Error getting Discover Weekly tracks: {e}")
        print("💡 Tip: Make sure you follow the Discover Weekly playlist in Spotify")
        raise

    if not track_uris:
        print("⚠️ No tracks found in Discover Weekly. Exiting.")
        return

    # Check if playlist already exists for this week
    existing_playlists = sp.current_user_playlists(limit=50)
    for playlist in existing_playlists['items']:
        if playlist['name'] == playlist_name:
            print(f"⚠️ Playlist '{playlist_name}' already exists. Skipping creation.")
            return

    # Create new weekly playlist
    try:
        new_playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False,
            description=f"Auto-saved Discover Weekly for {monday.strftime('%B %d')} to {sunday.strftime('%B %d, %Y')}"
        )
        new_playlist_id = new_playlist['id']
        print(f"✅ Created new playlist: {playlist_name}")
    except Exception as e:
        print(f"❌ Error creating playlist: {e}")
        raise

    # Add tracks to the new playlist
    try:
        # Spotify API limits to 100 tracks per request
        for i in range(0, len(track_uris), 100):
            batch = track_uris[i:i+100]
            sp.playlist_add_items(new_playlist_id, batch)
        
        print(f"✅ Successfully saved {len(track_uris)} tracks to '{playlist_name}'")
        print(f"🎵 Playlist URL: https://open.spotify.com/playlist/{new_playlist_id}")
    except Exception as e:
        print(f"❌ Error adding tracks to playlist: {e}")
        raise

if __name__ == "__main__":
    main()
