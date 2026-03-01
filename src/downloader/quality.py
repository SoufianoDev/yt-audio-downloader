#!/usr/bin/env python3
"""
Quality fetching module.
"""

from typing import List
import yt_dlp

class QualityFetcher:
    """Fetches available audio qualities for a given URL and format."""

    def __init__(self, url: str, audioFormat: str) -> None:
        self.url = url
        self.audioFormat = audioFormat

    def getAvailableQualities(self) -> List[str]:
        """Return list of available bitrates as strings like '128k'."""
        ydlOpts = {'quiet': True, 'no_warnings': True}
        qualities = []
        try:
            with yt_dlp.YoutubeDL(ydlOpts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                formats = info.get('formats', [])
                for f in formats:
                    if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                        if self.audioFormat == 'best' or f.get('ext') == self.audioFormat or self.audioFormat in f.get('format_note', ''):
                            abr = f.get('abr')
                            if abr:
                                qualities.append(f"{int(abr)}k")
                qualities = sorted(set(qualities), key=lambda x: int(x.rstrip('k')))
        except Exception:
            pass
        return qualities

    def promptForQuality(self) -> str:
        """Interactively ask user to choose a quality, return selected."""
        qualities = self.getAvailableQualities()
        if qualities:
            print("Available audio qualities:")
            for i, q in enumerate(qualities, 1):
                print(f"  {i}. {q}")
            choice = input("Select quality by number, or enter custom (e.g., 192k) [default best]: ").strip()
            if choice:
                if choice.isdigit() and 1 <= int(choice) <= len(qualities):
                    return qualities[int(choice) - 1]
                else:
                    return choice
        else:
            qInput = input("Enter desired quality (e.g., 128k, 192k) or press Enter for best: ").strip()
            return qInput if qInput else '0'
        return '0'
