import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES
import os
import theme
import cutter
import validation

class SongClipperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Song Clipper")
        self.root.geometry("720x720")
        self.root.configure(bg=theme.BG_DARK)
        self.root.resizable(True, True)
        # Force window to front and center
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        self.root.deiconify()

        # State
        self.clip_selected_file = None
        self.clip_file_duration = 0
        self.loop_selected_file = None
        
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

    def _init_ttk_styles(self):
        # Keep ttk widgets consistent with the existing dark theme.
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "TNotebook",
            background=theme.BG_DARK,
            borderwidth=0,
        )
        style.configure(
            "TNotebook.Tab",
            background=theme.BG_CARD,
            foreground=theme.TEXT_PRIMARY,
            padding=(14, 8),
            font=theme.FONT_BOLD,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", theme.BG_DROPZONE), ("active", theme.BG_DROPZONE)],
            foreground=[("selected", theme.TEXT_PRIMARY), ("active", theme.TEXT_PRIMARY)],
        )

    def _ensure_ffmpeg_tools(self):
        if self.ffmpeg_path and self.ffprobe_path:
            return True

        # Re-check in case they were added while app was open
        self.ffprobe_path = self._find_tool("ffprobe.exe")
        self.ffmpeg_path = self._find_tool("ffmpeg.exe")

        if self.ffmpeg_path and self.ffprobe_path:
            return True

        messagebox.showerror(
            "Error",
            "FFmpeg tools (ffmpeg.exe, ffprobe.exe) not found.\n\nPlease place them in:\ntools/ffmpeg/",
        )
        return False

    def setup_ui(self):
        self._init_ttk_styles()

        # Header
        header_frame = tk.Frame(self.root, bg=theme.BG_DARK, pady=15)
        header_frame.pack(fill="x", padx=30)
        
        tk.Label(header_frame, text="Completely Offline App", fg=theme.TEXT_SECONDARY, bg=theme.BG_DARK, font=theme.FONT_LABEL).pack(anchor="w")
        tk.Label(header_frame, text="Clip a segment or create loops from an MP3", fg=theme.TEXT_PRIMARY, bg=theme.BG_DARK, font=theme.FONT_HEADING).pack(anchor="w")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=30, pady=(5, 15))

        self.clip_tab = tk.Frame(self.notebook, bg=theme.BG_DARK)
        self.loop_tab = tk.Frame(self.notebook, bg=theme.BG_DARK)

        self.notebook.add(self.clip_tab, text="Clip")
        self.notebook.add(self.loop_tab, text="Loop")

        self._setup_clip_tab(self.clip_tab)
        self._setup_loop_tab(self.loop_tab)

    # --- Clip tab ---

    def _setup_clip_tab(self, parent):
        # Drop Zone
        self.clip_drop_zone = tk.Frame(parent, bg=theme.BG_DROPZONE, highlightthickness=2, highlightbackground=theme.BORDER_DROPZONE, pady=50)
        self.clip_drop_zone.pack(fill="both", expand=True, pady=(15, 10))

        self.clip_drop_zone.drop_target_register(DND_FILES)
        self.clip_drop_zone.dnd_bind("<<Drop>>", self.handle_drop_clip)

        tk.Label(self.clip_drop_zone, text="Drop MP3 here", fg=theme.TEXT_PRIMARY, bg=theme.BG_DROPZONE, font=theme.FONT_BOLD).pack()
        tk.Label(self.clip_drop_zone, text="or click Browse if drag-and-drop is not convenient", fg=theme.TEXT_SECONDARY, bg=theme.BG_DROPZONE, font=theme.FONT_LABEL).pack(pady=5)
        tk.Button(self.clip_drop_zone, text="Browse MP3", bg=theme.ACCENT_GREEN, fg="black", borderwidth=0, padx=25, pady=10, command=self.browse_clip_file, font=theme.FONT_BOLD, cursor="hand2").pack(pady=10)

        # Inputs
        input_frame = tk.Frame(parent, bg=theme.BG_DARK)
        input_frame.pack(fill="x", pady=10)
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=1)

        from_frame = tk.Frame(input_frame, bg=theme.BG_DARK)
        from_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        tk.Label(from_frame, text="From", fg=theme.TEXT_SECONDARY, bg=theme.BG_DARK, font=theme.FONT_LABEL).pack(anchor="w")
        self.from_val = tk.StringVar(value="00:30")
        tk.Entry(from_frame, textvariable=self.from_val, bg=theme.BG_CARD, fg=theme.TEXT_PRIMARY, insertbackground="white", borderwidth=0, font=theme.FONT_MAIN).pack(fill="x", pady=5, ipady=5)
        self.from_val.trace_add("write", self.update_clip_output_preview)

        to_frame = tk.Frame(input_frame, bg=theme.BG_DARK)
        to_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        tk.Label(to_frame, text="To", fg=theme.TEXT_SECONDARY, bg=theme.BG_DARK, font=theme.FONT_LABEL).pack(anchor="w")
        self.to_val = tk.StringVar(value="01:10")
        tk.Entry(to_frame, textvariable=self.to_val, bg=theme.BG_CARD, fg=theme.TEXT_PRIMARY, insertbackground="white", borderwidth=0, font=theme.FONT_MAIN).pack(fill="x", pady=5, ipady=5)
        self.to_val.trace_add("write", self.update_clip_output_preview)

        # Previews
        preview_frame = tk.Frame(parent, bg=theme.BG_DARK)
        preview_frame.pack(fill="x", pady=10)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.columnconfigure(1, weight=1)

        sel_file_frame = tk.Frame(preview_frame, bg=theme.BG_CARD, padx=8, pady=8)
        sel_file_frame.grid(row=0, column=0, sticky="new", padx=(0, 5))
        tk.Label(sel_file_frame, text="Selected File", fg=theme.TEXT_SECONDARY, bg=theme.BG_CARD, font=theme.FONT_LABEL).pack(anchor="w")
        self.clip_sel_file_label = tk.Label(sel_file_frame, text="None", fg=theme.TEXT_PRIMARY, bg=theme.BG_CARD, font=theme.FONT_MAIN, wraplength=200, justify="left")
        self.clip_sel_file_label.pack(anchor="w", pady=3)

        out_file_frame = tk.Frame(preview_frame, bg=theme.BG_CARD, padx=8, pady=8)
        out_file_frame.grid(row=0, column=1, sticky="new", padx=(5, 0))
        tk.Label(out_file_frame, text="Output", fg=theme.TEXT_SECONDARY, bg=theme.BG_CARD, font=theme.FONT_LABEL).pack(anchor="w")
        self.clip_out_file_label = tk.Label(out_file_frame, text="None", fg=theme.TEXT_PRIMARY, bg=theme.BG_CARD, font=theme.FONT_MAIN, wraplength=200, justify="left")
        self.clip_out_file_label.pack(anchor="w", pady=3)

        # Footer
        footer_frame = tk.Frame(parent, bg=theme.BG_DARK)
        footer_frame.pack(fill="x", pady=(10, 0), side="bottom")

        self.clip_status_label = tk.Label(footer_frame, text="Validates timestamps before cutting", fg=theme.TEXT_SECONDARY, bg=theme.BG_DARK, font=theme.FONT_LABEL)
        self.clip_status_label.pack(side="left", fill="x", expand=True)

        self.extract_btn = tk.Button(footer_frame, text="Extract", bg=theme.ACCENT_BLUE, fg="black", borderwidth=0, padx=40, pady=10, command=self.perform_extraction, font=theme.FONT_BOLD, cursor="hand2")
        self.extract_btn.pack(side="right")

    def handle_drop_clip(self, event):
        files = self.root.tk.splitlist(event.data)
        if len(files) > 1:
            self.show_clip_status("Please drop only one file.", theme.ERROR_RED)
            return

        file_path = files[0]
        if not file_path.lower().endswith(".mp3"):
            self.show_clip_status("Only MP3 files are supported.", theme.ERROR_RED)
            return

        self.load_clip_file(file_path)

    def browse_clip_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        if file_path:
            self.load_clip_file(file_path)

    def load_clip_file(self, file_path):
        if not self._ensure_ffmpeg_tools():
            self.show_clip_status("FFmpeg not found. Place it in tools/ffmpeg/", theme.ERROR_RED)
            return

        self.clip_selected_file = file_path
        self.clip_sel_file_label.config(text=os.path.basename(file_path))

        duration = cutter.get_duration(self.ffprobe_path, file_path)
        if duration:
            self.clip_file_duration = duration
            self.show_clip_status(f"File loaded. Duration: {duration:.2f}s", theme.TEXT_SECONDARY)
        else:
            self.show_clip_status("Error reading file duration.", theme.ERROR_RED)

        self.update_clip_output_preview()

    def update_clip_output_preview(self, *args):
        if not self.clip_selected_file:
            return

        from_ts = self.from_val.get()
        to_ts = self.to_val.get()

        filename = os.path.basename(self.clip_selected_file)
        name, ext = os.path.splitext(filename)

        out_name = f"{name}-{cutter.format_timestamp_for_filename(from_ts)}-to-{cutter.format_timestamp_for_filename(to_ts)}{ext}"
        self.clip_out_file_label.config(text=out_name)

    def show_clip_status(self, message, color):
        self.clip_status_label.config(text=message, fg=color)

    def perform_extraction(self):
        if not self.clip_selected_file:
            self.show_clip_status("No file selected.", theme.ERROR_RED)
            return

        from_ts = self.from_val.get()
        to_ts = self.to_val.get()

        if not validation.validate_timestamp(from_ts) or not validation.validate_timestamp(to_ts):
            self.show_clip_status("Invalid timestamp format (MM:SS or HH:MM:SS)", theme.ERROR_RED)
            return

        start_secs = cutter.parse_timestamp(from_ts)
        end_secs = cutter.parse_timestamp(to_ts)

        valid, err = validation.validate_range(start_secs, end_secs, self.clip_file_duration)
        if not valid:
            self.show_clip_status(err, theme.ERROR_RED)
            return

        dir_name = os.path.dirname(self.clip_selected_file)
        out_filename = self.clip_out_file_label.cget("text")
        output_path = cutter.get_unique_output_path(os.path.join(dir_name, out_filename))

        self.show_clip_status("Extracting...", theme.ACCENT_BLUE)
        self.extract_btn.config(state="disabled")
        self.root.update()

        success, err_msg = cutter.cut_audio(self.ffmpeg_path, self.clip_selected_file, start_secs, end_secs, output_path)

        self.extract_btn.config(state="normal")
        if success:
            self.show_clip_status("Success! Saved next to source.", theme.SUCCESS_GREEN)
            messagebox.showinfo("Success", f"File saved as:\n{os.path.basename(output_path)}")
        else:
            self.show_clip_status("Extraction failed.", theme.ERROR_RED)
            print(f"FFmpeg Error: {err_msg}")

    # --- Loop tab ---

    def _setup_loop_tab(self, parent):
        self.loop_drop_zone = tk.Frame(parent, bg=theme.BG_DROPZONE, highlightthickness=2, highlightbackground=theme.BORDER_DROPZONE, pady=50)
        self.loop_drop_zone.pack(fill="both", expand=True, pady=(15, 10))

        self.loop_drop_zone.drop_target_register(DND_FILES)
        self.loop_drop_zone.dnd_bind("<<Drop>>", self.handle_drop_loop)

        tk.Label(self.loop_drop_zone, text="Drop MP3 here", fg=theme.TEXT_PRIMARY, bg=theme.BG_DROPZONE, font=theme.FONT_BOLD).pack()
        tk.Label(self.loop_drop_zone, text="or click Browse if drag-and-drop is not convenient", fg=theme.TEXT_SECONDARY, bg=theme.BG_DROPZONE, font=theme.FONT_LABEL).pack(pady=5)
        tk.Button(self.loop_drop_zone, text="Browse MP3", bg=theme.ACCENT_GREEN, fg="black", borderwidth=0, padx=25, pady=10, command=self.browse_loop_file, font=theme.FONT_BOLD, cursor="hand2").pack(pady=10)

        # Inputs
        input_frame = tk.Frame(parent, bg=theme.BG_DARK)
        input_frame.pack(fill="x", pady=10)
        input_frame.columnconfigure(0, weight=1)

        loops_frame = tk.Frame(input_frame, bg=theme.BG_DARK)
        loops_frame.grid(row=0, column=0, sticky="ew")
        tk.Label(loops_frame, text="Loops", fg=theme.TEXT_SECONDARY, bg=theme.BG_DARK, font=theme.FONT_LABEL).pack(anchor="w")
        self.loop_count_val = tk.StringVar(value="2")
        tk.Entry(loops_frame, textvariable=self.loop_count_val, bg=theme.BG_CARD, fg=theme.TEXT_PRIMARY, insertbackground="white", borderwidth=0, font=theme.FONT_MAIN).pack(fill="x", pady=5, ipady=5)
        self.loop_count_val.trace_add("write", self.update_loop_output_preview)

        # Previews
        preview_frame = tk.Frame(parent, bg=theme.BG_DARK)
        preview_frame.pack(fill="x", pady=10)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.columnconfigure(1, weight=1)

        sel_file_frame = tk.Frame(preview_frame, bg=theme.BG_CARD, padx=8, pady=8)
        sel_file_frame.grid(row=0, column=0, sticky="new", padx=(0, 5))
        tk.Label(sel_file_frame, text="Selected File", fg=theme.TEXT_SECONDARY, bg=theme.BG_CARD, font=theme.FONT_LABEL).pack(anchor="w")
        self.loop_sel_file_label = tk.Label(sel_file_frame, text="None", fg=theme.TEXT_PRIMARY, bg=theme.BG_CARD, font=theme.FONT_MAIN, wraplength=200, justify="left")
        self.loop_sel_file_label.pack(anchor="w", pady=3)

        out_file_frame = tk.Frame(preview_frame, bg=theme.BG_CARD, padx=8, pady=8)
        out_file_frame.grid(row=0, column=1, sticky="new", padx=(5, 0))
        tk.Label(out_file_frame, text="Output", fg=theme.TEXT_SECONDARY, bg=theme.BG_CARD, font=theme.FONT_LABEL).pack(anchor="w")
        self.loop_out_file_label = tk.Label(out_file_frame, text="None", fg=theme.TEXT_PRIMARY, bg=theme.BG_CARD, font=theme.FONT_MAIN, wraplength=200, justify="left")
        self.loop_out_file_label.pack(anchor="w", pady=3)

        # Footer
        footer_frame = tk.Frame(parent, bg=theme.BG_DARK)
        footer_frame.pack(fill="x", pady=(10, 0), side="bottom")

        self.loop_status_label = tk.Label(footer_frame, text="Enter how many times to repeat the track", fg=theme.TEXT_SECONDARY, bg=theme.BG_DARK, font=theme.FONT_LABEL)
        self.loop_status_label.pack(side="left", fill="x", expand=True)

        self.loop_btn = tk.Button(footer_frame, text="Create Loops", bg=theme.ACCENT_BLUE, fg="black", borderwidth=0, padx=40, pady=10, command=self.perform_loop, font=theme.FONT_BOLD, cursor="hand2")
        self.loop_btn.pack(side="right")

    def handle_drop_loop(self, event):
        files = self.root.tk.splitlist(event.data)
        if len(files) > 1:
            self.show_loop_status("Please drop only one file.", theme.ERROR_RED)
            return

        file_path = files[0]
        if not file_path.lower().endswith(".mp3"):
            self.show_loop_status("Only MP3 files are supported.", theme.ERROR_RED)
            return

        self.load_loop_file(file_path)

    def browse_loop_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        if file_path:
            self.load_loop_file(file_path)

    def load_loop_file(self, file_path):
        if not self._ensure_ffmpeg_tools():
            self.show_loop_status("FFmpeg not found. Place it in tools/ffmpeg/", theme.ERROR_RED)
            return

        self.loop_selected_file = file_path
        self.loop_sel_file_label.config(text=os.path.basename(file_path))
        self.show_loop_status("File loaded.", theme.TEXT_SECONDARY)
        self.update_loop_output_preview()

    def update_loop_output_preview(self, *args):
        if not self.loop_selected_file:
            return

        loops = validation.parse_positive_int(self.loop_count_val.get(), min_value=1)
        filename = os.path.basename(self.loop_selected_file)
        name, ext = os.path.splitext(filename)

        if loops is None:
            out_name = f"{name}-loopx?{ext}"
        else:
            out_name = f"{name}-loopx{loops}{ext}"

        self.loop_out_file_label.config(text=out_name)

    def show_loop_status(self, message, color):
        self.loop_status_label.config(text=message, fg=color)

    def perform_loop(self):
        if not self.loop_selected_file:
            self.show_loop_status("No file selected.", theme.ERROR_RED)
            return

        loops = validation.parse_positive_int(self.loop_count_val.get(), min_value=1)
        if loops is None:
            self.show_loop_status("Loops must be a whole number (>= 1).", theme.ERROR_RED)
            return

        dir_name = os.path.dirname(self.loop_selected_file)
        out_filename = self.loop_out_file_label.cget("text")
        output_path = cutter.get_unique_output_path(os.path.join(dir_name, out_filename))

        self.show_loop_status("Creating looped file...", theme.ACCENT_BLUE)
        self.loop_btn.config(state="disabled")
        self.root.update()

        success, err_msg = cutter.loop_audio(self.ffmpeg_path, self.loop_selected_file, loops, output_path)

        self.loop_btn.config(state="normal")
        if success:
            self.show_loop_status("Success! Saved next to source.", theme.SUCCESS_GREEN)
            messagebox.showinfo("Success", f"File saved as:\n{os.path.basename(output_path)}")
        else:
            self.show_loop_status("Looping failed.", theme.ERROR_RED)
            print(f"FFmpeg Error: {err_msg}")
