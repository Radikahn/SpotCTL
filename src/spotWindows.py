"""
Spotify Volume Controller with Hardware Volume Keys (pynput version)
A background application that intercepts hardware volume keys to control Spotify volume
This version uses pynput which doesn't require root privileges on Linux
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import sys
import json
import os
import signal
from pynput import keyboard

# Configuration
CONFIG_FILE = "spotify_config.json"

# Default hotkeys - using pynput's format
# Volume up: Ctrl+Shift+Up
# Volume down: Ctrl+Shift+Down
VOLUME_STEP = 10  # Volume change percentage (0-100)

# Spotify redirect URI (127.0.0.1 works with HTTP)
DEFAULT_REDIRECT_URI = "http://127.0.0.1:8888/callback"


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
            print(f'''{{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uri": "{DEFAULT_REDIRECT_URI}"
}}''')
            print("\nGet your credentials at: https://developer.spotify.com/dashboard")
            print(f"Note: Use {DEFAULT_REDIRECT_URI} as your redirect URI")
            sys.exit(1)

        with open(CONFIG_FILE, 'r') as f:
            self.config = json.load(f)

        # Use default redirect URI if not specified
        if 'redirect_uri' not in self.config:
            self.config['redirect_uri'] = DEFAULT_REDIRECT_URI

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
            print("✓ Successfully authenticated with Spotify")
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
            print(f"✗ Error setting volume: {e}")
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

    def on_press(self, key):
        """Handle key press events"""
        try:
            # Check for media volume keys
            if key == keyboard.Key.media_volume_up:
                self.volume_up()
            elif key == keyboard.Key.media_volume_down:
                self.volume_down()

        except AttributeError:
            pass


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n✓ Shutting down gracefully...")
    sys.exit(0)


def main():
    """Main function to run the background hotkey listener"""
    print("=" * 50)
    print("Spotify Volume Controller")
    print("(Using Hardware Volume Keys)")
    print("=" * 50)
    print("\n✓ No root/sudo required!")

    # Initialize controller
    controller = SpotifyVolumeController()

    # Register signal handler for clean exit
    signal.signal(signal.SIGINT, signal_handler)

    # Display hotkey information
    print(f"\nListening for keyboard volume keys:")
    print(f"  • Volume Up Key   → Controls Spotify volume up")
    print(f"  • Volume Down Key → Controls Spotify volume down")
    print(f"  • Volume Step: {VOLUME_STEP}%")

    print("\n✓ Hotkeys registered successfully!")
    print("The app is now running in the background.")
    print("Press Ctrl+C to exit.\n")

    # Start the keyboard listener
    with keyboard.Listener(on_press=controller.on_press) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            signal_handler(None, None)


if __name__ == "__main__":
    main()
