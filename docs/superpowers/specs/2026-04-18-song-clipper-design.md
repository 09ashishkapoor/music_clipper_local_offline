# Song Clipper Design

**Date:** 2026-04-18

## Goal

Build a completely offline Windows desktop app that lets a user drag and drop a single MP3 file, enter `From` and `To` timestamps, and extract the selected segment as a new MP3 saved next to the source file. The app must launch from a batch file and must not require Python to be installed system-wide.

## Constraints

- Windows desktop only
- Offline only
- Dark mode UI
- One MP3 input at a time
- Drag-and-drop as the primary file input
- Batch file launcher
- Output saved automatically next to the source file

## Recommended Stack

- UI: Python `tkinter`
- Drag-and-drop support: `tkinterdnd2`
- Audio cutting: bundled `ffmpeg.exe`
- Runtime packaging: embedded local Python runtime stored in the project
- Launcher: `run_song_clipper.bat`

## User Experience

The app opens as a compact dark-mode desktop window titled `Song Clipper`.

Main screen elements:

- Drag-and-drop area for one MP3 file
- Fallback `Browse MP3` button
- `From` timestamp input
- `To` timestamp input
- Selected file display
- Output filename preview
- Primary `Extract` button
- Inline status or error message area

Primary user flow:

1. User launches the app from `run_song_clipper.bat`.
2. User drops a single `.mp3` file into the window.
3. App displays the selected filename.
4. User enters `From` and `To` timestamps in `MM:SS` or `HH:MM:SS`.
5. App validates inputs and previews the output filename.
6. User clicks `Extract`.
7. App runs local `ffmpeg.exe`.
8. App shows success or a clear error message.

## Architecture

The application is a thin desktop UI over a local command-line media toolchain.

- The UI layer owns drag-and-drop, field state, validation feedback, button states, and status messages.
- A small service layer owns timestamp parsing, output filename generation, duration checks, and `ffmpeg` command construction.
- The bundled `ffmpeg.exe` performs the actual MP3 segment extraction.
- The batch file launches the embedded Python runtime and starts the desktop app.

This keeps the app small, testable, and easy to run on a Windows machine without global dependencies.

## Project Structure

```text
music_clipper_local_offline/
  app/
    main.py
    ui.py
    cutter.py
    validation.py
    theme.py
  runtime/
    python/
  tools/
    ffmpeg/
      ffmpeg.exe
      ffprobe.exe
  docs/
    superpowers/
      specs/
        2026-04-18-song-clipper-design.md
  run_song_clipper.bat
  requirements.txt
```

Responsibilities:

- `app/main.py`: app startup and dependency wiring
- `app/ui.py`: window layout, drag-and-drop handling, events, status updates
- `app/cutter.py`: probe duration, generate output path, invoke `ffmpeg`
- `app/validation.py`: timestamp parsing and input validation
- `app/theme.py`: dark-mode colors and widget styling
- `run_song_clipper.bat`: launch the local runtime and app entry point

## File Selection Rules

- Accept exactly one file at a time
- Accept only `.mp3`
- Reject multi-file drops
- Reject empty or invalid paths
- Keep the latest accepted file as the active selection

If the user drops an invalid file, the app does not start extraction and shows a clear inline error.

## Timestamp Rules

Accepted input formats:

- `MM:SS`
- `HH:MM:SS`

Validation requirements:

- Both fields are required
- Parsed values must be non-negative
- `From` must be strictly less than `To`
- `To` must not exceed the track duration

The app should normalize parsed timestamps internally to seconds.

## Output Naming

The extracted file is saved in the same folder as the source file.

Base naming pattern:

```text
<original-name>-<from>-to-<to>.mp3
```

Example:

```text
meditation-track-00-30-to-01-10.mp3
```

If that filename already exists, the app generates a unique sibling name:

```text
meditation-track-00-30-to-01-10-1.mp3
meditation-track-00-30-to-01-10-2.mp3
```

## Extraction Strategy

The app should use bundled `ffprobe.exe` first to read track duration, then run bundled `ffmpeg.exe` to cut the selected range.

Expected command shape:

```text
ffmpeg -y -ss <from> -to <to> -i <input.mp3> -c copy <output.mp3>
```

If stream-copy proves unreliable for some MP3 files, the implementation may fall back to re-encoding as MP3 while preserving the same user workflow and output contract.

## Runtime Packaging

The project includes its own Python runtime under `runtime/python/` plus Python dependencies installed into that local runtime. The batch file uses only project-local paths.

Expected launcher responsibility:

- Resolve its own directory
- Find `runtime/python/python.exe`
- Start `app/main.py`
- Surface a useful error if the local runtime is missing

This satisfies the self-contained requirement without depending on system Python.

## Error Handling

The app should handle these cases explicitly:

- No file selected
- Non-MP3 file dropped
- Multiple files dropped
- Invalid timestamp format
- `From >= To`
- `To` beyond track duration
- Missing `ffmpeg` or `ffprobe`
- Extraction process failure

UX rules:

- Show errors inline in the window
- Do not crash the app for user-input mistakes
- Disable `Extract` while extraction is running
- Re-enable controls after completion or failure

## Testing Scope

Required verification:

- App launches from `run_song_clipper.bat`
- App works without system Python installed
- Drag-and-drop accepts one MP3
- Valid timestamps produce a clipped MP3 next to the source file
- Invalid timestamps block extraction and show errors
- Existing output names resolve to a unique filename
- Missing local tools produce a clear startup or runtime error

## Non-Goals

- Batch clipping multiple files
- Waveform editing
- Timeline preview
- Audio playback controls
- Format conversion beyond MP3 output
- Installer packaging in the first version

## Implementation Notes

Keep the first version focused and predictable. The product value is reliable offline extraction, not a complex editor. The code should stay split into small units so validation and command execution can be tested independently from the UI.
