#!/usr/bin/env python3
import sys
import os
import yt_dlp
import av
import glob
from .config import DownloaderConfig
from .path import PathHandler

class YouTubeAudioDownloader:
    def __init__(self, config: DownloaderConfig):
        self.config = config
        self.path_handler = PathHandler(config)

    def _build_ydl_opts(self, outtmpl: str) -> dict:
        return {
            'format': 'bestaudio/best',
            'outtmpl': outtmpl,
            'quiet': False,
            'no_warnings': False,
            'progress_hooks': [self._progress_hook],
            'ffmpeg_location': '/dev/null' if sys.platform != 'win32' else 'NUL',
            'prefer_ffmpeg': False,
        }

    def _convert_with_av(self, in_path: str, out_path: str, fmt: str):
        in_path = os.path.normpath(in_path)
        out_path = os.path.normpath(out_path)
        
        sys.stderr.write(f"[INFO] Converting to {fmt} using PyAV...\n")
        
        if not os.path.exists(in_path):
             raise FileNotFoundError(f"Input file missing: {in_path}")

        try:
            with av.open(in_path) as input_container:
                in_stream = next((s for s in input_container.streams if s.type == 'audio'), None)
                if not in_stream:
                    raise ValueError("No audio stream found.")

                with av.open(out_path, mode='w', format=fmt) as output_container:
                    codecs = {
                        'mp3': 'libmp3lame', 'wav': 'pcm_s16le', 'm4a': 'aac',
                        'aac': 'aac', 'opus': 'libopus', 'flac': 'flac', 'ogg': 'libvorbis'
                    }
                    codec = codecs.get(fmt, 'libmp3lame')
                    
                    out_stream = output_container.add_stream(codec, rate=in_stream.rate)
                    if hasattr(in_stream, 'layout'):
                        out_stream.layout = in_stream.layout
                    else:
                        out_stream.channels = in_stream.channels
                    
                    for frame in input_container.decode(audio=0):
                        for packet in out_stream.encode(frame):
                            output_container.mux(packet)
                    
                    for packet in out_stream.encode():
                        output_container.mux(packet)
        except Exception as e:
            sys.stderr.write(f"Conversion error: {e}\n")
            raise

    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                percent = downloaded / total
                bar_len = 40
                filled = int(bar_len * percent)
                bar = '█' * filled + '-' * (bar_len - filled)
                line = f'Progress: |{bar}| {percent:.1%}'
                if sys.stderr.isatty():
                    # Real terminal: carriage return overwrites in-place
                    sys.stderr.write(f'\r{line}  ')
                    sys.stderr.flush()
                else:
                    # Non-TTY (CI, pipes): print each update on its own line but
                    # suppress duplicates by only printing at 10% increments
                    if not hasattr(self, '_last_pct') or int(percent * 10) != self._last_pct:
                        self._last_pct = int(percent * 10)
                        sys.stderr.write(f'{line}\n')
                        sys.stderr.flush()
        elif d['status'] == 'finished':
            sys.stderr.write('\nProcessing...\n')

    def download(self):
        try:
            # Get video info first
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                info = ydl.extract_info(self.config.url, download=False)
                title = info.get('title', 'audio')
                ext = info.get('ext', 'mp3')

            target_path = self.path_handler.ensureUniquePath(title, ext)
            opts = self._build_ydl_opts(target_path)
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                dl_path = os.path.normpath(ydl.prepare_filename(info))
                print(f"Downloading: {self.config.url}")
                ydl.download([self.config.url])
            
            # Robust path detection for Wine/Windows/Linux discrepancies
            if not os.path.exists(dl_path):
                base = os.path.splitext(dl_path)[0]
                matches = glob.glob(f"{base}.*")
                if matches:
                    dl_path = os.path.normpath(matches[0])

            actual_ext = os.path.splitext(dl_path)[1].lstrip('.')
            target_ext = self.config.audioFormat if self.config.audioFormat != 'best' else actual_ext
            
            if self.config.audioFormat != 'best' and target_ext != actual_ext:
                final_tmp = self.path_handler.ensureUniquePath(title, target_ext)
                final_path = os.path.normpath(final_tmp.replace('%(ext)s', target_ext).replace('%(title)s', title))

                self._convert_with_av(dl_path, final_path, target_ext)
                
                if not self.config.keepVideo and os.path.exists(dl_path):
                    os.remove(dl_path)
                
                print(f"Finished: {final_path}")
            else:
                print(f"Finished: {dl_path}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
