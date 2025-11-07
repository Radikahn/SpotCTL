"""
Advanced volume scroll wheel detector for Windows
Uses pyWinhook or keyboard library for better raw input detection
"""
import sys

# Try using keyboard library (better for raw input)
try:
    import keyboard

    def on_volume_event(event):
        """Callback for volume-related keyboard events"""
        print(
            f"Event: {event.name} | Scan Code: {event.scan_code} | Event Type: {event.event_type}")

        # Common volume control scan codes on Windows
        # These may vary by keyboard manufacturer
        volume_scan_codes = {
            0xAE: "Volume Down",
            0xAF: "Volume Up",
            0xAD: "Volume Mute",
            # Some keyboards use different codes for scroll wheel
            0x20: "Volume Scroll (possible)",
        }

        if event.scan_code in volume_scan_codes:
            print(f"  → Detected: {volume_scan_codes[event.scan_code]}")

    print("Listening for all keyboard events (including volume controls)...")
    print("Press Ctrl+C to exit")
    print("-" * 60)

    # Hook all keyboard events
    keyboard.hook(on_volume_event)
    keyboard.wait('esc')

except ImportError:
    print("Error: 'keyboard' library not found.")
    print("Install it with: pip install keyboard")
    print("\nNote: This script requires administrator privileges on Windows")
    sys.exit(1)
