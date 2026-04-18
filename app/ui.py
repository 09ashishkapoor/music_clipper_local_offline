import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import theme
import cutter
import validation

class SongClipperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Song Clipper")
        self.root.geometry("700x700")
        self.root.configure(bg=theme.BG_DARK)
        self.root.resizable(True, True)
        # Force window to front and center
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        self.root.deiconify()

        # State
        self.selected_file = None
        self.file_duration = 0
        
        # Check for ffmpeg in tools folder, then try system PATH
        self.ffprobe_path = self._find_tool("ffprobe.exe")
        self.ffmpeg_path = self._find_tool("ffmpeg.exe")

        self.setup_ui()

    def _find_tool(self, name):
        # 1. Check tools/ffmpeg/
        local_path = os.path.join(os.getcwd(), "tools", "ffmpeg", name)
        if os.path.exists(local_path):
            return local_path
        
        # 2. Check system PATH
        import shutil
        system_path = shutil.which(name.replace(".exe", ""))
        if system_path:
            return system_path
            
        return None

    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg=theme.BG_DARK, pady=15)
        header_frame.pack(fill="x", padx=30)
        
        tk.Label(header_frame, text="Completely Offline App", fg=theme.TEXT_SECONDARY, bg=theme.BG_DARK, font=theme.FONT_LABEL).pack(anchor="w")
        tk.Label(header_frame, text="Extract a precise segment from a MP3 File", fg=theme.TEXT_PRIMARY, bg=theme.BG_DARK, font=theme.FONT_HEADING).pack(anchor="w")

        # Drop Zone
        self.drop_zone = tk.Frame(self.root, bg=theme.BG_DROPZONE, highlightthickness=2, highlightbackground=theme.BORDER_DROPZONE, pady=50)
        self.drop_zone.pack(fill="both", expand=True, padx=30, pady=15)
        
        # DND Support
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind('<<Drop>>', self.handle_drop)

        self.drop_label = tk.Label(self.drop_zone, text="Drop music file here", fg=theme.TEXT_PRIMARY, bg=theme.BG_DROPZONE, font=theme.FONT_BOLD)
        self.drop_label.pack()
        
        tk.Label(self.drop_zone, text="or click Browse if drag-and-drop is not convenient", fg=theme.TEXT_SECONDARY, bg=theme.BG_DROPZONE, font=theme.FONT_LABEL).pack(pady=5)
        
        self.browse_btn = tk.Button(self.drop_zone, text="Browse MP3", bg=theme.ACCENT_GREEN, fg="black", borderwidth=0, padx=25, pady=10, command=self.browse_file, font=theme.FONT_BOLD, cursor="hand2")
        self.browse_btn.pack(pady=10)

        # Inputs
        input_frame = tk.Frame(self.root, bg=theme.BG_DARK)
        input_frame.pack(fill="x", padx=30, pady=15)
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=1)

        # From
        from_frame = tk.Frame(input_frame, bg=theme.BG_DARK)
        from_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        tk.Label(from_frame, text="From", fg=theme.TEXT_SECONDARY, bg=theme.BG_DARK, font=theme.FONT_LABEL).pack(anchor="w")
        self.from_val = tk.StringVar(value="00:30")
        self.from_entry = tk.Entry(from_frame, textvariable=self.from_val, bg=theme.BG_CARD, fg=theme.TEXT_PRIMARY, insertbackground="white", borderwidth=0, font=theme.FONT_MAIN)
        self.from_entry.pack(fill="x", pady=5, ipady=5)
        self.from_val.trace_add("write", self.update_output_preview)

        # To
        to_frame = tk.Frame(input_frame, bg=theme.BG_DARK)
        to_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        tk.Label(to_frame, text="To", fg=theme.TEXT_SECONDARY, bg=theme.BG_DARK, font=theme.FONT_LABEL).pack(anchor="w")
        self.to_val = tk.StringVar(value="01:10")
        self.to_entry = tk.Entry(to_frame, textvariable=self.to_val, bg=theme.BG_CARD, fg=theme.TEXT_PRIMARY, insertbackground="white", borderwidth=0, font=theme.FONT_MAIN)
        self.to_entry.pack(fill="x", pady=5, ipady=5)
        self.to_val.trace_add("write", self.update_output_preview)

        # Previews
        preview_frame = tk.Frame(self.root, bg=theme.BG_DARK)
        preview_frame.pack(fill="x", padx=30, pady=10)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.columnconfigure(1, weight=1)

        # Selected File Preview
        self.sel_file_frame = tk.Frame(preview_frame, bg=theme.BG_CARD, padx=8, pady=8)
        self.sel_file_frame.grid(row=0, column=0, sticky="new", padx=(0, 5))
        tk.Label(self.sel_file_frame, text="Selected File", fg=theme.TEXT_SECONDARY, bg=theme.BG_CARD, font=theme.FONT_LABEL).pack(anchor="w")
        self.sel_file_label = tk.Label(self.sel_file_frame, text="None", fg=theme.TEXT_PRIMARY, bg=theme.BG_CARD, font=theme.FONT_MAIN, wraplength=120, justify="left")
        self.sel_file_label.pack(anchor="w", pady=3)

        # Output Preview
        self.out_file_frame = tk.Frame(preview_frame, bg=theme.BG_CARD, padx=8, pady=8)
        self.out_file_frame.grid(row=0, column=1, sticky="new", padx=(5, 0))
        tk.Label(self.out_file_frame, text="Output", fg=theme.TEXT_SECONDARY, bg=theme.BG_CARD, font=theme.FONT_LABEL).pack(anchor="w")
        self.out_file_label = tk.Label(self.out_file_frame, text="None", fg=theme.TEXT_PRIMARY, bg=theme.BG_CARD, font=theme.FONT_MAIN, wraplength=120, justify="left")
        self.out_file_label.pack(anchor="w", pady=3)

        # Footer
        footer_frame = tk.Frame(self.root, bg=theme.BG_DARK)
        footer_frame.pack(fill="x", padx=30, pady=15, side="bottom")
        
        self.status_label = tk.Label(footer_frame, text="Validates timestamps before cutting", fg=theme.TEXT_SECONDARY, bg=theme.BG_DARK, font=theme.FONT_LABEL)
        self.status_label.pack(side="left", fill="x", expand=True)

        self.extract_btn = tk.Button(footer_frame, text="Extract", bg=theme.ACCENT_BLUE, fg="black", borderwidth=0, padx=40, pady=10, command=self.perform_extraction, font=theme.FONT_BOLD, cursor="hand2")
        self.extract_btn.pack(side="right")

    def handle_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        if len(files) > 1:
            self.show_status("Please drop only one file.", theme.ERROR_RED)
            return
        
        file_path = files[0]
        if not file_path.lower().endswith(".mp3"):
            self.show_status("Only MP3 files are supported.", theme.ERROR_RED)
            return
        
        self.load_file(file_path)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path):
        if not self.ffmpeg_path or not self.ffprobe_path:
            # Re-check in case they were added while app was open
            self.ffprobe_path = self._find_tool("ffprobe.exe")
            self.ffmpeg_path = self._find_tool("ffmpeg.exe")
            
            if not self.ffmpeg_path or not self.ffprobe_path:
                self.show_status("FFmpeg not found. Place it in tools/ffmpeg/", theme.ERROR_RED)
                messagebox.showerror("Error", "FFmpeg tools (ffmpeg.exe, ffprobe.exe) not found.\n\nPlease place them in:\ntools/ffmpeg/")
                return

        self.selected_file = file_path
        filename = os.path.basename(file_path)
        self.sel_file_label.config(text=filename)
        
        # Get duration
        duration = cutter.get_duration(self.ffprobe_path, file_path)
        if duration:
            self.file_duration = duration
            self.show_status(f"File loaded. Duration: {duration:.2f}s", theme.TEXT_SECONDARY)
        else:
            self.show_status("Error reading file duration.", theme.ERROR_RED)
            
        self.update_output_preview()

    def update_output_preview(self, *args):
        if not self.selected_file:
            return

        from_ts = self.from_val.get()
        to_ts = self.to_val.get()
        
        filename = os.path.basename(self.selected_file)
        name, ext = os.path.splitext(filename)
        
        out_name = f"{name}-{cutter.format_timestamp_for_filename(from_ts)}-to-{cutter.format_timestamp_for_filename(to_ts)}{ext}"
        self.out_file_label.config(text=out_name)

    def show_status(self, message, color):
        self.status_label.config(text=message, fg=color)

    def perform_extraction(self):
        if not self.selected_file:
            self.show_status("No file selected.", theme.ERROR_RED)
            return

        from_ts = self.from_val.get()
        to_ts = self.to_val.get()

        if not validation.validate_timestamp(from_ts) or not validation.validate_timestamp(to_ts):
            self.show_status("Invalid timestamp format (MM:SS or HH:MM:SS)", theme.ERROR_RED)
            return

        start_secs = cutter.parse_timestamp(from_ts)
        end_secs = cutter.parse_timestamp(to_ts)
        
        valid, err = validation.validate_range(start_secs, end_secs, self.file_duration)
        if not valid:
            self.show_status(err, theme.ERROR_RED)
            return

        # Prepare output path
        dir_name = os.path.dirname(self.selected_file)
        out_filename = self.out_file_label.cget("text")
        output_path = os.path.join(dir_name, out_filename)
        output_path = cutter.get_unique_output_path(output_path)

        self.show_status("Extracting...", theme.ACCENT_BLUE)
        self.extract_btn.config(state="disabled")
        self.root.update()

        success, err_msg = cutter.cut_audio(self.ffmpeg_path, self.selected_file, start_secs, end_secs, output_path)
        
        self.extract_btn.config(state="normal")
        if success:
            self.show_status("Success! Saved next to source.", theme.SUCCESS_GREEN)
            messagebox.showinfo("Success", f"File saved as:\n{os.path.basename(output_path)}")
        else:
            self.show_status("Extraction failed.", theme.ERROR_RED)
            print(f"FFmpeg Error: {err_msg}")
