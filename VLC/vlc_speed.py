import pysrt
import requests
import time
import xml.etree.ElementTree as ET

# --- Configuration ---
VLC_PASSWORD = "vlc123"          # The password you set in Step 1
VLC_URL = "http://localhost:8080/requests/status.xml"

PADDING_SEC = 2.0   # Extra seconds of normal speed before and after dialogue
NORMAL_SPEED = 1.0
FAST_SPEED = 2.0
# ---------------------

def get_vlc_status():
    """Fetches the current playback time from VLC."""
    try:
        response = requests.get(VLC_URL, auth=('', VLC_PASSWORD))
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            time_elem = root.find('time')
            if time_elem is not None:
                return float(time_elem.text)
    except requests.exceptions.RequestException:
        pass
    return None

def set_vlc_speed(speed):
    """Sends a command to VLC to change the playback rate."""
    try:
        # VLC HTTP API requires the rate to be passed as a float string
        requests.get(f"{VLC_URL}?command=rate&val={speed}", auth=('', VLC_PASSWORD))
        print(f"Speed changed to {speed}x")
    except requests.exceptions.RequestException as e:
        print(f"Failed to change speed: {e}")

def get_dialogue_intervals(srt_path, padding):
    """Parses SRT and creates merged time intervals for dialogue."""
    
    # Try UTF-8 first, fallback to Latin-1 for older/European encodings
    try:
        subs = pysrt.open(srt_path, encoding='utf-8')
    except UnicodeDecodeError:
        print("UTF-8 decoding failed. Falling back to 'latin-1' encoding...")
        subs = pysrt.open(srt_path, encoding='latin-1')

    raw_intervals = []
    
    # Extract start and end times in seconds, applying padding
    for sub in subs:
        start_sec = max(0, (sub.start.ordinal / 1000.0) - padding)
        end_sec = (sub.end.ordinal / 1000.0) + padding
        raw_intervals.append([start_sec, end_sec])
        
    if not raw_intervals:
        return []

    # Merge overlapping intervals
    raw_intervals.sort(key=lambda x: x[0])
    merged_intervals = [raw_intervals[0]]
    
    for current in raw_intervals[1:]:
        previous = merged_intervals[-1]
        if current[0] <= previous[1]:
            # Overlap found, extend the end time of the previous interval
            previous[1] = max(previous[1], current[1])
        else:
            # No overlap, add as a new interval
            merged_intervals.append(current)
            
    return merged_intervals
    
def main():
    import sys
    import tkinter as tk
    from tkinter import filedialog

    # Hide root window
    root = tk.Tk()
    root.withdraw()
    # Keep the dialog on top
    root.attributes('-topmost', True)

    print("Opening file picker to select subtitle file...")
    srt_file = filedialog.askopenfilename(
        title="Select SRT Subtitle File",
        filetypes=[("Subtitle Files", "*.srt"), ("All Files", "*.*")]
    )
    
    # Clean up the root window
    root.destroy()

    if not srt_file:
        print("No file selected. Exiting.")
        sys.exit(0)

    print(f"Parsing {srt_file}...")
    intervals = get_dialogue_intervals(srt_file, PADDING_SEC)
    print(f"Found {len(intervals)} distinct dialogue blocks (after merging overlaps).")
    print("Connecting to VLC...")

    current_speed = None

    while True:
        current_time = get_vlc_status()
        
        if current_time is not None:
            # Check if the current time falls inside any dialogue interval
            is_dialogue = any(start <= current_time <= end for start, end in intervals)
            
            desired_speed = NORMAL_SPEED if is_dialogue else FAST_SPEED
            
            # Only send the command if the speed actually needs to change
            if current_speed != desired_speed:
                set_vlc_speed(desired_speed)
                current_speed = desired_speed
                
        # Poll 4 times a second. Don't poll too fast to avoid overloading VLC's local server.
        time.sleep(0.25) 

if __name__ == "__main__":
    main()