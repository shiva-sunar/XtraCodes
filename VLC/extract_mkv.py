import os
import sys
import json
import shutil
import threading
import subprocess
from pathlib import Path

# --- Rich Import for Beautiful CLI ---
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich import print as rprint
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# --- CustomTkinter Import for Premium GUI ---
try:
    import customtkinter as ctk
    from tkinter import filedialog, messagebox
    HAS_CTK = True
except ImportError:
    HAS_CTK = False
    # Fallback to standard tkinter if customtkinter is not available
    import tkinter as tk
    from tkinter import filedialog, messagebox


def find_ffmpeg_or_install():
    """
    Ensures ffmpeg and ffprobe are available.
    Integrates with static-ffmpeg, which auto-downloads binaries on demand.
    """
    # 1. Check system path first
    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")
    if ffmpeg_path and ffprobe_path:
        return ffmpeg_path, ffprobe_path

    # 2. Try importing static-ffmpeg (which we installed in the environment)
    try:
        import static_ffmpeg
        # static-ffmpeg adds platform-specific binaries to the PATH dynamically
        static_ffmpeg.add_paths()
        ffmpeg_path = shutil.which("ffmpeg")
        ffprobe_path = shutil.which("ffprobe")
        if ffmpeg_path and ffprobe_path:
            return ffmpeg_path, ffprobe_path
    except ImportError:
        pass

    # 3. If still not found, try to auto-install static-ffmpeg
    try:
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        subprocess.run(
            [sys.executable, "-m", "pip", "install", "static-ffmpeg"],
            capture_output=True, text=True, check=True, startupinfo=startupinfo
        )
        import static_ffmpeg
        static_ffmpeg.add_paths()
        ffmpeg_path = shutil.which("ffmpeg")
        ffprobe_path = shutil.which("ffprobe")
        if ffmpeg_path and ffprobe_path:
            return ffmpeg_path, ffprobe_path
    except Exception:
        pass

    return None, None


def get_subtitle_tracks(mkv_file):
    """
    Queries an MKV file using ffprobe to parse and return all subtitle tracks.
    """
    ffmpeg_bin, ffprobe_bin = find_ffmpeg_or_install()
    if not ffprobe_bin:
        raise RuntimeError("ffprobe binary could not be found or installed.")

    cmd = [
        ffprobe_bin,
        "-v", "error",
        "-select_streams", "s",
        "-show_entries", "stream=index,codec_name:stream_tags=language,title",
        "-of", "json",
        mkv_file
    ]

    startupinfo = None
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
        startupinfo=startupinfo
    )

    data = json.loads(result.stdout)
    tracks = []

    # Common language 3-letter codes map to friendly English names
    lang_map = {
        "eng": "English", "fre": "French", "fra": "French",
        "ger": "German", "deu": "German", "spa": "Spanish",
        "ita": "Italian", "jpn": "Japanese", "chi": "Chinese",
        "zho": "Chinese", "rus": "Russian", "kor": "Korean",
        "por": "Portuguese", "dut": "Dutch", "nld": "Dutch",
        "ara": "Arabic", "swe": "Swedish", "nor": "Norwegian",
        "dan": "Danish", "fin": "Finnish", "pol": "Polish",
        "tur": "Turkish", "und": "Undetermined"
    }

    # Map FFmpeg subtitle codecs to standard extensions and human names
    codec_info_map = {
        "subrip": ("srt", "SubRip (SRT)"),
        "srt": ("srt", "SubRip (SRT)"),
        "ass": ("ass", "Advanced SubStation Alpha"),
        "ssa": ("ass", "SubStation Alpha"),
        "webvtt": ("vtt", "WebVTT"),
        "vtt": ("vtt", "WebVTT"),
        "mov_text": ("srt", "QuickTime Subtitles"),
        "hdmv_pgs_subtitle": ("sup", "HDMV PGS (Blu-ray graphics)"),
        "pgs": ("sup", "HDMV PGS (Blu-ray graphics)"),
        "dvd_subtitle": ("sub", "VobSub (DVD graphics)"),
        "vobsub": ("sub", "VobSub (DVD graphics)")
    }

    for idx, stream in enumerate(data.get("streams", [])):
        index = stream.get("index")
        codec = stream.get("codec_name", "srt")
        tags = stream.get("tags", {})
        lang = tags.get("language", "und")
        title = tags.get("title", "")

        lang_name = lang_map.get(lang.lower(), lang.upper())
        ext, codec_desc = codec_info_map.get(codec.lower(), ("srt", f"Text ({codec})"))

        tracks.append({
            "index": index,
            "relative_idx": idx, # 0-based index of subtitle tracks
            "codec": codec,
            "codec_desc": codec_desc,
            "language": lang_name,
            "lang_code": lang,
            "title": title,
            "extension": ext
        })

    return tracks


def extract_track(mkv_file, track_index, output_path, codec):
    """
    Extracts a specific subtitle stream to output_path using ffmpeg.
    """
    ffmpeg_bin, _ = find_ffmpeg_or_install()
    if not ffmpeg_bin:
        raise RuntimeError("ffmpeg binary could not be found or installed.")

    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", mkv_file,
        "-map", f"0:{track_index}"
    ]

    # For graphics subtitles (PGS / VobSub), we MUST use copy to extract properly to .sup/.sub.
    # For text-based tracks, copy is also safest to preserve formatting without transcoding issues.
    cmd.extend(["-c:s", "copy"])
    cmd.append(output_path)

    startupinfo = None
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        startupinfo=startupinfo
    )

    if result.returncode != 0:
        # Fallback in case of copy failures on some systems/formats
        fallback_cmd = [
            ffmpeg_bin,
            "-y",
            "-i", mkv_file,
            "-map", f"0:{track_index}",
            output_path
        ]
        fb_result = subprocess.run(
            fallback_cmd,
            capture_output=True,
            text=True,
            startupinfo=startupinfo
        )
        if fb_result.returncode != 0:
            raise RuntimeError(fb_result.stderr or result.stderr)

    return True


# =====================================================================
#                      PREMIUM CUSTOMTKINTER GUI
# =====================================================================
class SubtitleExtractorGUI:
    def __init__(self):
        if not HAS_CTK:
            self.root = tk.Tk()
            self.setup_standard_tkinter()
            return

        # Setup CustomTkinter dark appearance
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("MKV Subtitle Extractor")
        self.root.geometry("960x650")
        self.root.minsize(900, 600)

        self.mkv_path = ""
        self.detected_tracks = []
        self.checkbox_vars = {}
        self.is_extracting = False

        self.build_gui()
        
        # Check ffmpeg on startup in a non-blocking thread
        threading.Thread(target=self.check_ffmpeg_startup, daemon=True).start()

    def build_gui(self):
        # Configure layout split (Left: Controls & Info, Right: Subtitle Tracks List)
        self.root.grid_columnconfigure(0, weight=4) # Left side controls
        self.root.grid_columnconfigure(1, weight=5) # Right side tracks
        self.root.grid_rowconfigure(0, weight=1)

        # ----------------- LEFT SIDE PANEL (CONTROLS) -----------------
        left_frame = ctk.CTkFrame(self.root, corner_radius=15, fg_color="#18181c")
        left_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        left_frame.grid_rowconfigure(5, weight=1) # Log area stretches
        left_frame.grid_columnconfigure(0, weight=1)

        # App Title Card
        title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="Matroska Subtitle Demuxer", 
            font=ctk.CTkFont(family="Outfit", size=22, weight="bold"),
            text_color="#3b82f6"
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            title_frame, 
            text="Extract subtitle tracks cleanly and fast.", 
            font=ctk.CTkFont(family="Inter", size=12),
            text_color="#8b8b8f"
        )
        subtitle_label.pack(anchor="w")

        # 1. MKV Source File Selection Group
        source_group = ctk.CTkFrame(left_frame, fg_color="#202024", corner_radius=10)
        source_group.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        source_group.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            source_group, 
            text="MKV VIDEO FILE", 
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#a1a1a5"
        ).grid(row=0, column=0, padx=15, pady=(10, 2), sticky="w")
        
        self.mkv_entry = ctk.CTkEntry(
            source_group, 
            placeholder_text="Select MKV video file...", 
            height=35,
            border_color="#303034",
            fg_color="#151518"
        )
        self.mkv_entry.grid(row=1, column=0, padx=(15, 10), pady=(0, 12), sticky="ew")
        
        self.browse_btn = ctk.CTkButton(
            source_group, 
            text="Browse", 
            width=80, 
            height=35,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            font=ctk.CTkFont(weight="bold"),
            command=self.browse_mkv
        )
        self.browse_btn.grid(row=1, column=1, padx=(0, 15), pady=(0, 12), sticky="e")

        # 2. Save Destination Folder Selection Group
        dest_group = ctk.CTkFrame(left_frame, fg_color="#202024", corner_radius=10)
        dest_group.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        dest_group.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            dest_group, 
            text="SAVE DESTINATION FOLDER", 
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#a1a1a5"
        ).grid(row=0, column=0, padx=15, pady=(10, 2), sticky="w")
        
        self.dest_entry = ctk.CTkEntry(
            dest_group, 
            placeholder_text="Defaults to MKV folder...", 
            height=35,
            border_color="#303034",
            fg_color="#151518"
        )
        self.dest_entry.grid(row=1, column=0, padx=(15, 10), pady=(0, 12), sticky="ew")
        
        self.dest_btn = ctk.CTkButton(
            dest_group, 
            text="Choose", 
            width=80, 
            height=35,
            fg_color="#303036",
            hover_color="#404046",
            font=ctk.CTkFont(weight="bold"),
            command=self.browse_dest
        )
        self.dest_btn.grid(row=1, column=1, padx=(0, 15), pady=(0, 12), sticky="e")

        # 3. Actions Group
        action_group = ctk.CTkFrame(left_frame, fg_color="transparent")
        action_group.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        action_group.grid_columnconfigure(0, weight=1)
        action_group.grid_columnconfigure(1, weight=1)

        self.extract_selected_btn = ctk.CTkButton(
            action_group, 
            text="Extract Selected", 
            height=40,
            fg_color="#22c55e",
            hover_color="#16a34a",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.start_selected_extraction,
            state="disabled"
        )
        self.extract_selected_btn.grid(row=0, column=0, padx=(0, 5), pady=0, sticky="ew")

        self.extract_all_btn = ctk.CTkButton(
            action_group, 
            text="Extract All Tracks", 
            height=40,
            fg_color="#303036",
            hover_color="#404046",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.start_all_extraction,
            state="disabled"
        )
        self.extract_all_btn.grid(row=0, column=1, padx=(5, 0), pady=0, sticky="ew")

        # Progress Indicator Section
        self.progress_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        self.progress_frame.grid(row=4, column=0, padx=20, pady=(5, 5), sticky="ew")
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=8, fg_color="#151518", progress_color="#3b82f6")
        self.progress_bar.grid(row=0, column=0, padx=0, pady=5, sticky="ew")
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(
            self.progress_frame, 
            text="System state: Waiting for user action.", 
            font=ctk.CTkFont(size=11), 
            text_color="#8b8b8f"
        )
        self.status_label.grid(row=1, column=0, padx=0, pady=0, sticky="w")

        # 4. Status Logs Terminal
        log_frame = ctk.CTkFrame(left_frame, fg_color="#101012", corner_radius=10, border_width=1, border_color="#202024")
        log_frame.grid(row=5, column=0, padx=20, pady=(10, 20), sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            log_frame, 
            text="EXTRACTION LOGS / SYSTEM CONSOLE", 
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color="#5a5a60"
        ).grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")

        self.log_box = ctk.CTkTextbox(
            log_frame, 
            font=ctk.CTkFont(family="Consolas", size=11), 
            fg_color="transparent",
            text_color="#38bdf8",
            border_width=0
        )
        self.log_box.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.log_box.configure(state="disabled")

        # ----------------- RIGHT SIDE PANEL (TRACKS CHECKLIST) -----------------
        self.right_frame = ctk.CTkFrame(self.root, corner_radius=15, fg_color="#18181c")
        self.right_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(2, weight=1)

        # Header of Tracks Panel
        tracks_header = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        tracks_header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        ctk.CTkLabel(
            tracks_header, 
            text="Subtitle Track Selection", 
            font=ctk.CTkFont(family="Outfit", size=18, weight="bold"),
            text_color="#f8fafc"
        ).pack(side="left")

        # Bulk Select Options
        self.bulk_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.bulk_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        self.select_all_btn = ctk.CTkButton(
            self.bulk_frame, 
            text="Select All", 
            width=90, 
            height=26,
            fg_color="#303036",
            hover_color="#404046",
            text_color="#e2e8f0",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.select_all_tracks,
            state="disabled"
        )
        self.select_all_btn.pack(side="left", padx=(0, 10))
        
        self.deselect_all_btn = ctk.CTkButton(
            self.bulk_frame, 
            text="Deselect All", 
            width=90, 
            height=26,
            fg_color="#303036",
            hover_color="#404046",
            text_color="#e2e8f0",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.deselect_all_tracks,
            state="disabled"
        )
        self.deselect_all_btn.pack(side="left")

        # Scrollable tracks container
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.right_frame, 
            fg_color="#101012", 
            corner_radius=10,
            border_width=1,
            border_color="#202024"
        )
        self.scroll_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # Placeholder inside scroll frame when no MKV is loaded
        self.placeholder_label = ctk.CTkLabel(
            self.scroll_frame, 
            text="Please browse and select an MKV file to scan for subtitle tracks.", 
            font=ctk.CTkFont(size=12),
            text_color="#5a5a60"
        )
        self.placeholder_label.grid(row=0, column=0, padx=20, pady=150, sticky="center")

    def check_ffmpeg_startup(self):
        self.log("Detecting FFmpeg environment binaries...")
        ffmpeg_bin, ffprobe_bin = find_ffmpeg_or_install()
        if ffmpeg_bin and ffprobe_bin:
            self.log(f"FFmpeg located: {ffmpeg_bin}")
            self.log(f"FFprobe located: {ffprobe_bin}")
            self.log("Ready to demux Matroska containers!")
            self.status_label.configure(text="System state: Ready. Select an MKV file.")
        else:
            self.log("CRITICAL: FFmpeg/FFprobe binaries could not be loaded!")
            self.log("Please install static-ffmpeg manually or ensure FFmpeg is in PATH.")
            self.status_label.configure(text="System error: FFmpeg binaries missing.", text_color="#ef4444")
            messagebox.showerror(
                "FFmpeg Missing", 
                "FFmpeg binaries could not be located. Subtitle extraction will fail.\n\n"
                "Please run `pip install static-ffmpeg` or add FFmpeg to your system PATH."
            )

    def log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"{text}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def browse_mkv(self):
        file_path = filedialog.askopenfilename(
            title="Select MKV File", 
            filetypes=[("Matroska Video Files", "*.mkv"), ("All Files", "*.*")]
        )
        if file_path:
            self.mkv_path = os.path.abspath(file_path)
            self.mkv_entry.delete(0, "end")
            self.mkv_entry.insert(0, self.mkv_path)
            
            # Default destination directory is the same folder
            default_dest = os.path.dirname(self.mkv_path)
            self.dest_entry.delete(0, "end")
            self.dest_entry.insert(0, default_dest)
            
            # Scan tracks asynchronously to keep UI fast and interactive
            self.status_label.configure(text="Scanning video streams...", text_color="#3b82f6")
            self.log(f"Scanning MKV: {os.path.basename(self.mkv_path)}")
            
            # Clear previous checklist
            for widget in self.scroll_frame.winfo_children():
                widget.destroy()
            
            self.placeholder_label = ctk.CTkLabel(
                self.scroll_frame, 
                text="Scanning stream headers... Please wait.", 
                font=ctk.CTkFont(size=12),
                text_color="#8b8b8f"
            )
            self.placeholder_label.grid(row=0, column=0, padx=20, pady=150, sticky="center")
            
            threading.Thread(target=self.scan_mkv_tracks, daemon=True).start()

    def browse_dest(self):
        folder_path = filedialog.askdirectory(title="Select Destination Folder")
        if folder_path:
            self.dest_entry.delete(0, "end")
            self.dest_entry.insert(0, os.path.abspath(folder_path))

    def scan_mkv_tracks(self):
        try:
            self.detected_tracks = get_subtitle_tracks(self.mkv_path)
            # Switch back to main GUI thread to update widgets
            self.root.after(0, self.populate_track_list)
        except Exception as e:
            self.root.after(0, lambda: self.handle_scan_error(e))

    def handle_scan_error(self, err):
        self.log(f"Scan error: {err}")
        self.status_label.configure(text="Failed to scan MKV.", text_color="#ef4444")
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.placeholder_label = ctk.CTkLabel(
            self.scroll_frame, 
            text="Could not parse MKV file headers. Check system logs.", 
            font=ctk.CTkFont(size=12),
            text_color="#ef4444"
        )
        self.placeholder_label.grid(row=0, column=0, padx=20, pady=150, sticky="center")
        messagebox.showerror("Scan Error", f"An error occurred while parsing subtitle streams:\n\n{err}")

    def populate_track_list(self):
        # Clear container
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.checkbox_vars = {}

        if not self.detected_tracks:
            self.log("No subtitle tracks found in the MKV container.")
            self.status_label.configure(text="No subtitle tracks detected.", text_color="#f59e0b")
            self.placeholder_label = ctk.CTkLabel(
                self.scroll_frame, 
                text="Zero subtitle tracks found inside this MKV file.", 
                font=ctk.CTkFont(size=12),
                text_color="#a1a1a5"
            )
            self.placeholder_label.grid(row=0, column=0, padx=20, pady=150, sticky="center")
            self.extract_selected_btn.configure(state="disabled")
            self.extract_all_btn.configure(state="disabled")
            self.select_all_btn.configure(state="disabled")
            self.deselect_all_btn.configure(state="disabled")
            return

        self.log(f"Successfully identified {len(self.detected_tracks)} subtitle streams:")
        for t in self.detected_tracks:
            title_suffix = f" - {t['title']}" if t["title"] else ""
            self.log(f"  Stream #{t['index']}: {t['language']} [{t['codec_desc']}]{title_suffix}")

        # Populate tracks list dynamically with highly refined aesthetic frames
        for idx, track in enumerate(self.detected_tracks):
            track_idx = track["index"]
            
            # Setup track container frame
            track_card = ctk.CTkFrame(self.scroll_frame, fg_color="#18181c", height=50, corner_radius=8)
            track_card.grid(row=idx, column=0, padx=10, pady=5, sticky="ew")
            track_card.grid_columnconfigure(1, weight=1)
            
            # Checkbox
            var = tk.BooleanVar(value=True)
            self.checkbox_vars[track_idx] = var
            cb = ctk.CTkCheckBox(
                track_card, 
                text="", 
                variable=var, 
                width=24,
                checkbox_width=20,
                checkbox_height=20,
                fg_color="#3b82f6",
                hover_color="#2563eb"
            )
            cb.grid(row=0, column=0, padx=(12, 5), pady=10, sticky="w")

            # Description (Info Layout)
            info_frame = ctk.CTkFrame(track_card, fg_color="transparent")
            info_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            
            lang_lbl = ctk.CTkLabel(
                info_frame, 
                text=f"{track['language']}  •  Stream #{track_idx}", 
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#f8fafc"
            )
            lang_lbl.pack(anchor="w")
            
            extra_details = f"[{track['codec_desc']}]"
            if track["title"]:
                extra_details += f"  -  {track['title']}"
            
            detail_lbl = ctk.CTkLabel(
                info_frame, 
                text=extra_details, 
                font=ctk.CTkFont(size=10),
                text_color="#8b8b8f"
            )
            detail_lbl.pack(anchor="w")

            # Codec type badge on the far right
            badge_color = "#3b82f6" # Text / Standard
            if track["extension"] in ["sup", "sub"]:
                badge_color = "#eab308" # Graphics (PGS/Vobsub) warning badge
                
            badge_frame = ctk.CTkFrame(track_card, fg_color=badge_color, corner_radius=4, height=18)
            badge_frame.grid(row=0, column=2, padx=15, pady=10, sticky="e")
            
            badge_lbl = ctk.CTkLabel(
                badge_frame, 
                text=track["extension"].upper(), 
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color="#ffffff" if badge_color == "#3b82f6" else "#000000"
            )
            badge_lbl.pack(padx=6, pady=0)

        # Enable actions
        self.extract_selected_btn.configure(state="normal")
        self.extract_all_btn.configure(state="normal")
        self.select_all_btn.configure(state="normal")
        self.deselect_all_btn.configure(state="normal")
        self.status_label.configure(text=f"Loaded {len(self.detected_tracks)} subtitle tracks. Select tracks to extract.", text_color="#22c55e")

    def select_all_tracks(self):
        for var in self.checkbox_vars.values():
            var.set(True)

    def deselect_all_tracks(self):
        for var in self.checkbox_vars.values():
            var.set(False)

    def start_selected_extraction(self):
        selected_ids = [tid for tid, var in self.checkbox_vars.items() if var.get()]
        if not selected_ids:
            messagebox.showwarning("No Subtitles Selected", "Please select at least one subtitle track to extract.")
            return
        
        self.run_extraction_process(selected_ids)

    def start_all_extraction(self):
        all_ids = [track["index"] for track in self.detected_tracks]
        self.run_extraction_process(all_ids)

    def run_extraction_process(self, track_indices):
        if self.is_extracting:
            return

        dest_dir = self.dest_entry.get().strip()
        if not dest_dir:
            dest_dir = os.path.dirname(self.mkv_path)

        if not os.path.isdir(dest_dir):
            try:
                os.makedirs(dest_dir, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Directory Error", f"Unable to create destination folder:\n{e}")
                return

        self.is_extracting = True
        self.set_ui_state("disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="Extracting subtitles...", text_color="#3b82f6")

        # Run extraction in a separate worker thread so that progressbar and logs update in real time
        threading.Thread(
            target=self.extraction_worker, 
            args=(track_indices, dest_dir), 
            daemon=True
        ).start()

    def set_ui_state(self, state):
        self.browse_btn.configure(state=state)
        self.dest_btn.configure(state=state)
        self.extract_selected_btn.configure(state=state)
        self.extract_all_btn.configure(state=state)
        self.select_all_btn.configure(state=state)
        self.deselect_all_btn.configure(state=state)

    def extraction_worker(self, target_indices, dest_dir):
        total = len(target_indices)
        success_count = 0
        
        mkv_basename = Path(self.mkv_path).stem
        
        for idx, track_idx in enumerate(target_indices):
            # Find track info dictionary
            track = next(t for t in self.detected_tracks if t["index"] == track_idx)
            
            # Format clean destination filename
            lang_suffix = track["lang_code"]
            if track["title"]:
                # Clean title for filesystem safety
                clean_title = "".join(c for c in track["title"] if c.isalnum() or c in (" ", "_", "-")).strip()
                clean_title = clean_title.replace(" ", "_")
                filename = f"{mkv_basename}.{lang_suffix}.{clean_title}.{track['extension']}"
            else:
                filename = f"{mkv_basename}.{lang_suffix}.{track['extension']}"

            output_file = os.path.join(dest_dir, filename)
            
            self.log(f"Demuxing Track #{track_idx} -> {filename}...")
            self.status_label.configure(text=f"Demuxing track {idx+1} of {total}...")
            
            try:
                extract_track(self.mkv_path, track_idx, output_file, track["codec"])
                self.log(f"  [SUCCESS] Extracted to {output_file}")
                success_count += 1
            except Exception as e:
                self.log(f"  [FAILED] Failed to extract track #{track_idx}: {e}")
            
            # Update progress bar ratio
            progress_ratio = (idx + 1) / total
            self.root.after(0, lambda val=progress_ratio: self.progress_bar.set(val))

        # Extraction complete hook
        self.root.after(0, lambda: self.extraction_complete_callback(success_count, total, dest_dir))

    def extraction_complete_callback(self, success_count, total, dest_dir):
        self.is_extracting = False
        self.set_ui_state("normal")
        self.progress_bar.set(1.0)
        
        msg = f"Demuxing Finished. Successfully extracted {success_count} of {total} subtitle streams."
        self.log("\n==========================================")
        self.log(msg)
        self.log(f"Saved Files are located in: {dest_dir}")
        self.log("==========================================\n")
        
        self.status_label.configure(text="Demuxing Complete!", text_color="#22c55e")
        
        # Friendly modern popups
        if success_count == total:
            messagebox.showinfo("Extraction Complete", f"Successfully extracted all {total} selected subtitle track(s)!\n\nSaved to:\n{dest_dir}")
        else:
            messagebox.showwarning("Extraction Complete with Errors", f"Extracted {success_count} of {total} tracks.\nSome tracks failed to demux. Check logs inside system console.\n\nSaved to:\n{dest_dir}")

    def setup_standard_tkinter(self):
        # Ultra lightweight fallback standard Tkinter GUI in case CustomTkinter isn't available
        self.root.title("MKV Subtitle Extractor (Fallback Mode)")
        self.root.geometry("600x400")
        lbl = tk.Label(
            self.root, 
            text="Please run in terminal mode or install CustomTkinter:\npip install customtkinter",
            font=("Arial", 14), 
            pady=40
        )
        lbl.pack()
        btn = tk.Button(self.root, text="Exit", command=self.root.destroy, width=15)
        btn.pack()

    def run(self):
        self.root.mainloop()


# =====================================================================
#                      PREMIUM RICH CLI INTERFACE
# =====================================================================
def run_cli_mode(mkv_file=None):
    if not HAS_RICH:
        run_fallback_cli(mkv_file)
        return

    console = Console()
    console.print(Panel.fit(
        "[bold cyan]Matroska Subtitle Demuxer[/bold cyan]\n[dim]High-Speed Subtitle Extraction Utility[/dim]",
        border_style="cyan"
    ))

    # Ensure FFmpeg binaries are loaded
    with console.status("[bold yellow]Detecting FFmpeg environment...[/bold yellow]") as status:
        ffmpeg_bin, ffprobe_bin = find_ffmpeg_or_install()
        if not ffmpeg_bin or not ffprobe_bin:
            console.print("[bold red]Error: FFmpeg or FFprobe binaries could not be located on your path.[/bold red]")
            console.print("Please install static-ffmpeg using: [bold yellow]pip install static-ffmpeg[/bold yellow]")
            sys.exit(1)

    if not mkv_file:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        console.print("[yellow]Opening file selection dialog...[/yellow]")
        mkv_file = filedialog.askopenfilename(
            title="Select MKV File",
            filetypes=[("Matroska Video Files", "*.mkv"), ("All Files", "*.*")]
        )
        root.destroy()
        
        if not mkv_file:
            console.print("[bold red]File selection cancelled. Exiting.[/bold red]")
            sys.exit(0)

    if not os.path.exists(mkv_file):
        console.print(f"[bold red]Error: File does not exist at '{mkv_file}'[/bold red]")
        sys.exit(1)

    mkv_path = os.path.abspath(mkv_file)
    mkv_basename = Path(mkv_path).stem
    mkv_dir = os.path.dirname(mkv_path)

    console.print(f"[green]✔[/green] File located: [bold white]{os.path.basename(mkv_path)}[/bold white]")

    # Extract track headers
    with console.status("[bold yellow]Parsing Matroska tracks...[/bold yellow]"):
        try:
            tracks = get_subtitle_tracks(mkv_path)
        except Exception as e:
            console.print(f"[bold red]Failed to scan file headers: {e}[/bold red]")
            sys.exit(1)

    if not tracks:
        console.print("[bold yellow]Warning: No subtitle tracks were detected in this MKV file.[/bold yellow]")
        sys.exit(0)

    # Render a beautiful CLI track selection table
    table = Table(title="Detected Subtitle Tracks", title_style="bold magenta", border_style="dim")
    table.add_column("Index", style="cyan", justify="center")
    table.add_column("Stream Index", style="cyan", justify="center")
    table.add_column("Language", style="green")
    table.add_column("Codec / Extension", style="yellow")
    table.add_column("Title / Label", style="white")

    for i, t in enumerate(tracks):
        table.add_row(
            str(i),
            f"0:{t['index']}",
            t["language"],
            f"{t['codec_desc']} (.{t['extension']})",
            t["title"] if t["title"] else "[italic dim]None[/italic dim]"
        )

    console.print(table)
    console.print("\nEnter the [bold cyan]Index[/bold cyan] of the track you want to extract.")
    console.print("You can extract multiple tracks (e.g. [bold yellow]0,1[/bold yellow]) or write [bold yellow]all[/bold yellow] to extract all.")
    
    choice = input("Your selection: ").strip().lower()
    
    if choice == "all":
        selected_tracks = tracks
    else:
        try:
            indices = [int(x.strip()) for x in choice.split(",") if x.strip()]
            selected_tracks = [tracks[idx] for idx in indices]
        except (ValueError, IndexError):
            console.print("[bold red]Invalid selection index. Exiting.[/bold red]")
            sys.exit(1)

    # Get destination directory
    dest_input = input(f"Output folder [Press Enter for default: '{mkv_dir}']: ").strip(' "\'')
    dest_dir = os.path.abspath(dest_input) if dest_input else mkv_dir

    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    console.print(f"\n[bold green]Extracting {len(selected_tracks)} subtitle track(s) to folder: {dest_dir}[/bold green]\n")

    # Beautiful Rich Progress Bar demuxing process
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40, complete_style="green", finished_style="blue"),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Demuxing streams...", total=len(selected_tracks))
        
        for t in selected_tracks:
            lang_suffix = t["lang_code"]
            if t["title"]:
                clean_title = "".join(c for c in t["title"] if c.isalnum() or c in (" ", "_", "-")).strip()
                clean_title = clean_title.replace(" ", "_")
                filename = f"{mkv_basename}.{lang_suffix}.{clean_title}.{t['extension']}"
            else:
                filename = f"{mkv_basename}.{lang_suffix}.{t['extension']}"

            output_file = os.path.join(dest_dir, filename)
            progress.update(task, description=f"[cyan]Demuxing {filename}...")
            
            try:
                extract_track(mkv_path, t["index"], output_file, t["codec"])
                console.print(f"  [bold green]✔[/bold green] Demuxed Stream #{t['index']} ([dim]{t['language']}[/dim]) -> [white]{filename}[/white]")
            except Exception as e:
                console.print(f"  [bold red]✘[/bold red] Failed to demux Stream #{t['index']}: {e}")
                
            progress.advance(task)

    console.print("\n[bold green]Demuxing operation complete![/bold green]\n")


def run_fallback_cli(mkv_file=None):
    """
    Standard print-based CLI if 'rich' is missing.
    """
    print("\n--- MKV Subtitle Extractor CLI ---")
    ffmpeg_bin, ffprobe_bin = find_ffmpeg_or_install()
    if not ffmpeg_bin or not ffprobe_bin:
        print("Error: FFmpeg or FFprobe binaries not found on path.")
        print("Please install static-ffmpeg using: pip install static-ffmpeg")
        sys.exit(1)

    if not mkv_file:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        print("Opening file selection dialog...")
        mkv_file = filedialog.askopenfilename(
            title="Select MKV File",
            filetypes=[("Matroska Video Files", "*.mkv"), ("All Files", "*.*")]
        )
        root.destroy()
        
        if not mkv_file:
            print("File selection cancelled. Exiting.")
            sys.exit(0)

    if not os.path.exists(mkv_file):
        print(f"Error: File does not exist at '{mkv_file}'")
        sys.exit(1)

    mkv_path = os.path.abspath(mkv_file)
    mkv_basename = Path(mkv_path).stem
    mkv_dir = os.path.dirname(mkv_path)

    try:
        tracks = get_subtitle_tracks(mkv_path)
    except Exception as e:
        print(f"Failed to scan file headers: {e}")
        sys.exit(1)

    if not tracks:
        print("Warning: No subtitle tracks found in this MKV file.")
        sys.exit(0)

    print("\nDetected Subtitle Tracks:")
    for idx, t in enumerate(tracks):
        print(f"  [{idx}] Stream #{t['index']} - {t['language']} ({t['codec_desc']}) {t['title']}")

    choice = input("\nEnter track index(es) to extract (e.g. 0,1 or 'all'): ").strip().lower()
    if choice == "all":
        selected_tracks = tracks
    else:
        try:
            indices = [int(x.strip()) for x in choice.split(",") if x.strip()]
            selected_tracks = [tracks[idx] for idx in indices]
        except (ValueError, IndexError):
            print("Invalid selection index.")
            sys.exit(1)

    dest_input = input(f"Output folder [Press Enter for default: '{mkv_dir}']: ").strip(' "\'')
    dest_dir = os.path.abspath(dest_input) if dest_input else mkv_dir

    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    print(f"\nExtracting {len(selected_tracks)} subtitle track(s) to folder: {dest_dir}\n")

    for t in selected_tracks:
        lang_suffix = t["lang_code"]
        if t["title"]:
            clean_title = "".join(c for c in t["title"] if c.isalnum() or c in (" ", "_", "-")).strip()
            clean_title = clean_title.replace(" ", "_")
            filename = f"{mkv_basename}.{lang_suffix}.{clean_title}.{t['extension']}"
        else:
            filename = f"{mkv_basename}.{lang_suffix}.{t['extension']}"

        output_file = os.path.join(dest_dir, filename)
        print(f"Extracting Stream #{t['index']} ({t['language']}) -> {filename}...")
        try:
            extract_track(mkv_path, t["index"], output_file, t["codec"])
            print(f"  [SUCCESS] Saved to {output_file}")
        except Exception as e:
            print(f"  [FAILED] Failed to extract Stream #{t['index']}: {e}")

    print("\nDemuxing finished.\n")


# =====================================================================
#                          APPLICATION ENTRY POINT
# =====================================================================
if __name__ == "__main__":
    # If file arguments are passed via CLI, automatically run in CLI mode
    if len(sys.argv) > 1:
        # Check if the user specified a command or passed an input file path
        if sys.argv[1] in ["--cli", "-c"]:
            if len(sys.argv) > 2:
                run_cli_mode(sys.argv[2])
            else:
                run_cli_mode()
        elif sys.argv[1] in ["--gui", "-g"]:
            if HAS_CTK:
                app = SubtitleExtractorGUI()
                app.run()
            else:
                # If customtkinter is not installed, fallback to CLI
                print("CustomTkinter is required to run in GUI mode. Running in CLI mode.")
                run_cli_mode()
        else:
            # Assume first argument is the input file path
            run_cli_mode(sys.argv[1])
    else:
        # No arguments: launch modern GUI if customtkinter is available, fallback to CLI otherwise
        if HAS_CTK:
            try:
                app = SubtitleExtractorGUI()
                app.run()
            except Exception as e:
                print(f"Failed to launch GUI: {e}")
                print("Launching interactive CLI instead...")
                run_cli_mode()
        else:
            run_cli_mode()