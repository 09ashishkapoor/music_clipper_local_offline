import os
import subprocess
import re

def get_duration(ffprobe_path, file_path):
    """Get duration of a file in seconds using ffprobe."""
    try:
        cmd = [
            ffprobe_path, 
            "-v", "error", 
            "-show_entries", "format=duration", 
            "-of", "default=noprint_wrappers=1:nokey=1", 
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Error getting duration: {e}")
        return None

def parse_timestamp(ts_str):
    """Parse MM:SS or HH:MM:SS to seconds."""
    parts = ts_str.strip().split(':')
    try:
        if len(parts) == 2:  # MM:SS
            m, s = map(int, parts)
            return m * 60 + s
        elif len(parts) == 3:  # HH:MM:SS
            h, m, s = map(int, parts)
            return h * 3600 + m * 60 + s
        else:
            return None
    except ValueError:
        return None

def format_timestamp_for_filename(ts_str):
    """Replace colons with dashes for filename safety."""
    return ts_str.replace(':', '-')

def get_unique_output_path(output_path):
    """Generate a unique filename if the file already exists."""
    if not os.path.exists(output_path):
        return output_path
    
    base, ext = os.path.splitext(output_path)
    counter = 1
    while os.path.exists(f"{base}-{counter}{ext}"):
        counter += 1
    return f"{base}-{counter}{ext}"

def cut_audio(ffmpeg_path, input_path, start_time, end_time, output_path):
    """Cut audio using ffmpeg."""
    try:
        # Use stream copy for speed and quality preservation
        cmd = [
            ffmpeg_path,
            "-y",
            "-ss", str(start_time),
            "-to", str(end_time),
            "-i", input_path,
            "-c", "copy",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # Fallback to re-encoding if copy fails (some MP3s are tricky)
            cmd[8:10] = ["-c:a", "libmp3lame", "-q:a", "2"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
        return result.returncode == 0, result.stderr
    except Exception as e:
        return False, str(e)


def loop_audio(ffmpeg_path, input_path, loops, output_path):
    """
    Repeat an MP3 N times and write a new file using ffmpeg.

    Uses `-stream_loop` for reliability and simplicity:
      loops=1 => no looping
      loops=2 => stream_loop=1 (play twice)

    Tries stream copy first, then falls back to re-encoding if needed.
    """
    try:
        loops = int(loops)
        if loops < 1:
            return False, "Loops must be >= 1."

        stream_loop = loops - 1

        # Stream copy for speed and quality preservation
        cmd = [ffmpeg_path, "-y"]
        if stream_loop > 0:
            cmd += ["-stream_loop", str(stream_loop)]
        cmd += ["-i", input_path, "-c", "copy", output_path]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # Fallback: re-encode (some MP3s and/or metadata combinations fail with copy)
            cmd = [ffmpeg_path, "-y"]
            if stream_loop > 0:
                cmd += ["-stream_loop", str(stream_loop)]
            cmd += ["-i", input_path, "-c:a", "libmp3lame", "-q:a", "2", output_path]
            result = subprocess.run(cmd, capture_output=True, text=True)

        return result.returncode == 0, result.stderr
    except Exception as e:
        return False, str(e)
