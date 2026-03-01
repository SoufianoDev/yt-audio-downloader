#!/usr/bin/env python3
"""
Configuration module for YouTube Audio Downloader.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class DownloaderConfig:
    """Immutable configuration for a download."""
    url: str
    outputDir: Optional[str] = None
    outputName: Optional[str] = None
    audioFormat: str = 'best'
    audioQuality: str = '0'
    keepVideo: bool = False
