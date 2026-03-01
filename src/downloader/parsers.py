#!/usr/bin/env python3
"""
Parsers for command-line and interactive input.
"""

import os
import argparse
from typing import Optional, Tuple
from .config import DownloaderConfig
from .quality import QualityFetcher

AUDIO_EXTENSIONS = {'.mp3', '.m4a', '.opus', '.aac', '.flac', '.wav', '.ogg'}

class ConfigParser:
    """Parses configuration from command line or interactive input."""

    @staticmethod
    def parseFullOutputPath(path: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        If path ends with known audio extension, return (dir, name, format).
        Otherwise return (None, None, None).
        """
        path = os.path.expanduser(path)
        dirname, basename = os.path.split(path)
        if not basename:
            return None, None, None
        name, ext = os.path.splitext(basename)
        if ext.lower() in AUDIO_EXTENSIONS:
            return dirname or None, name, ext[1:].lower()
        return None, None, None

    @classmethod
    def fromInteractive(cls) -> DownloaderConfig:
        """Gather config interactively from user."""
        print("\n=== YouTube Audio Downloader ===\n")
        url = input("Enter YouTube video URL: ").strip()
        while not url:
            print("URL cannot be empty. Please try again.")
            url = input("Enter YouTube video URL: ").strip()

        outputPath = input("Output path (press Enter for current directory): ").strip()
        outputDir = None
        outputName = None
        audioFormat = 'best'

        if outputPath:
            d, n, f = cls.parseFullOutputPath(outputPath)
            if d is not None:
                outputDir = d
                outputName = n
                audioFormat = f
            else:
                outputDir = outputPath

        if outputDir is None:
            outputDir = input("Output directory (press Enter for current): ").strip() or None

        if outputName is None:
            nameInput = input("Custom filename (without extension, press Enter to use video title): ").strip()
            outputName = nameInput if nameInput else None

        if audioFormat == 'best':
            fmtPrompt = "Audio format (best/mp3/m4a/opus/aac/etc., press Enter for 'best'): "
            fmt = input(fmtPrompt).strip().lower()
            audioFormat = fmt if fmt else 'best'

        audioQuality = '0'
        if audioFormat != 'best':
            fetcher = QualityFetcher(url, audioFormat)
            audioQuality = fetcher.promptForQuality()

        keep = input("Keep the intermediate video file? (y/N): ").strip().lower()
        keepVideo = keep in ('y', 'yes')

        print("\n" + "=" * 40)
        return DownloaderConfig(
            url=url,
            outputDir=outputDir,
            outputName=outputName,
            audioFormat=audioFormat,
            audioQuality=audioQuality,
            keepVideo=keepVideo
        )

    @classmethod
    def fromCommandLine(cls) -> DownloaderConfig:
        """Parse command-line arguments into a config."""
        parser = argparse.ArgumentParser(
            description="Download audio from YouTube videos."
        )
        parser.add_argument('url', nargs='?',
                            help='YouTube video URL (leave empty for interactive mode)')
        parser.add_argument('-o', '--output-dir',
                            help='Output directory or full file path (e.g., ~/music/song.mp3)')
        parser.add_argument('-n', '--output-name',
                            help='Custom filename (without extension)')
        parser.add_argument('-f', '--format', default='best',
                            help='Audio format (mp3, m4a, opus, aac, best, etc.)')
        parser.add_argument('-q', '--quality', default='0',
                            help='Audio quality (e.g., 128k, 192k, 0 for best). If unavailable, you will be prompted.')
        parser.add_argument('-k', '--keep-video', action='store_true',
                            help='Keep the downloaded video after extraction')

        args = parser.parse_args()

        url = args.url
        outputDir = args.output_dir
        outputName = args.output_name
        audioFormat = args.format
        audioQuality = args.quality
        keepVideo = args.keep_video

        if outputDir:
            d, n, f = cls.parseFullOutputPath(outputDir)
            if d is not None:
                outputDir = d
                outputName = n
                audioFormat = f

        if audioFormat != 'best' and audioQuality != '0':
            fetcher = QualityFetcher(url, audioFormat)
            available = fetcher.getAvailableQualities()
            if available and audioQuality not in available:
                print(f"Requested quality '{audioQuality}' not available.", file=sys.stderr)
                print("Available qualities:", ', '.join(available), file=sys.stderr)
                print("\nPlease select an available quality.")
                for i, q in enumerate(available, 1):
                    print(f"  {i}. {q}")
                choice = input("Enter number or custom quality: ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(available):
                    audioQuality = available[int(choice) - 1]
                else:
                    audioQuality = choice if choice else '0'

        return DownloaderConfig(
            url=url,
            outputDir=outputDir,
            outputName=outputName,
            audioFormat=audioFormat,
            audioQuality=audioQuality,
            keepVideo=keepVideo
        )
