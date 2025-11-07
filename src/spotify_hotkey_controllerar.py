"""
Spotify Volume Controller with Global Hotkeys
A Windows background application that listens for keyboard shortcuts to control Spotify volume
"""

import keyboard
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import sys
import json
import os
from pathlib import Path

# Configuration
CONFIG_FILE = Path("spotify_config.json")

# Default hotkeys (can be customized)
VOLUME_UP_KEY = "volume up"
VOLUME_DOWN_KEY = "volume down"


VOLUME_STEP = 5


class SpotifyVolumeController:
    def __init__(self):
        """Initialize the Spotify controller with authentication"""
        self.sp = None
        self.current_volume = 50
        self.load_config()
        self.authenticate()

    def load_config(self):
        """Load Spotify API credentials from config file"""
        if not os.path.exists(CONFIG_FILE):
            print(f"Config file '{CONFIG_FILE}' not found!")
            print(
                "\nPlease create a file named 'spotify_config.json' with your Spotify API credentials:")
            print('''{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uri": "http://localhost:8888/callback"
}''')
            print("\nGet your credentials at: https://developer.spotify.com/dashboard")
            sys.exit(1)

        with open(CONFIG_FILE, 'r') as f:
            self.config = json.load(f)

    def authenticate(self):
        """Authenticate with Spotify API"""
        try:
            scope = "user-modify-playback-state user-read-playback-state"
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=self.config['client_id'],
                client_secret=self.config['client_secret'],
                redirect_uri=self.config['redirect_uri'],
                scope=scope,
                cache_path=".spotify_cache"
            ))

            print("Successfully authenticated with Spotify")
            self.update_current_volume()

        except Exception as e:
            print(f"✗ Authentication failed: {e}")
            sys.exit(1)

    def update_current_volume(self):
        """Get current volume from active Spotify device"""

        try:
            playback = self.sp.current_playback()

            if playback and playback['device']:
                self.current_volume = playback['device']['volume_percent']
            else:
                print("⚠ No active Spotify device found")

        except Exception as e:
            print(f"⚠ Could not get current volume: {e}")

    def set_volume(self, volume):
        """Set Spotify volume (0-100)"""
        try:
            # Clamp volume between 0 and 100
            volume = max(0, min(100, volume))

            # Set the volume
            self.sp.volume(volume)
            self.current_volume = volume
            print(f"♪ Volume set to {volume}%")
            return True
        except Exception as e:
            print(f"[Error]: setting volume: {e}")
            return False

    def volume_up(self):
        """Increase volume by VOLUME_STEP"""
        self.update_current_volume()
        new_volume = self.current_volume + VOLUME_STEP
        self.set_volume(new_volume)

    def volume_down(self):
        """Decrease volume by VOLUME_STEP"""
        self.update_current_volume()
        new_volume = self.current_volume - VOLUME_STEP
        self.set_volume(new_volume)


def main():
    """Main function to run the background hotkey listener"""
    print("=" * 50)
    print("Spotify Volume Controller")
    print("=" * 50)

    # Initialize controller
    controller = SpotifyVolumeController()

    # Register hotkeys
    print(f"\nRegistering hotkeys:")
    print(f"  • Volume Up:   {VOLUME_UP_KEY}")
    print(f"  • Volume Down: {VOLUME_DOWN_KEY}")
    print(f"  • Volume Step: {VOLUME_STEP}%")

    keyboard.add_hotkey(VOLUME_UP_KEY, controller.volume_up)
    keyboard.add_hotkey(VOLUME_DOWN_KEY, controller.volume_down)

    print("\n✓ Hotkeys registered successfully!")
    print("The app is now running in the background.")
    print("Press Ctrl+C to exit.\n")

    # Keep the program running
    try:
        keyboard.wait()  # Wait indefinitely for hotkeys
    except KeyboardInterrupt:
        print("\n\n✓ Shutting down gracefully...")
        sys.exit(0)


if __name__ == "__main__":
    main()
