#!/usr/bin/env python3
"""
Path handling module.
"""

import os
from typing import Optional
from .config import DownloaderConfig

class PathHandler:
    """Handles file path construction and uniqueness checks."""

    def __init__(self, config: DownloaderConfig) -> None:
        self.config = config

    def buildBasePath(self, title: str) -> str:
        """Construct the base path without extension."""
        if self.config.outputDir:
            if self.config.outputName:
                base = os.path.join(self.config.outputDir, self.config.outputName)
            else:
                base = os.path.join(self.config.outputDir, title)
        else:
            base = self.config.outputName if self.config.outputName else title
        return base.rsplit('.', 1)[0]

    def ensureUniquePath(self, title: str, ext: str) -> str:
        """
        Return a unique file path by appending _1, _2 etc. if needed.
        Also returns the template with %(ext)s placeholder.
        """
        base = self.buildBasePath(title)
        finalExt = self.config.audioFormat if self.config.audioFormat != 'best' else ext
        candidate = f"{base}.{finalExt}"
        counter = 1
        while os.path.exists(candidate):
            candidate = f"{base}_{counter}.{finalExt}"
            counter += 1

        if candidate != f"{base}.{finalExt}":
            dirName = os.path.dirname(candidate)
            baseName = os.path.basename(candidate)
            nameWithoutExt = baseName.rsplit('.', 1)[0]
            return os.path.join(dirName, f"{nameWithoutExt}.%(ext)s")
        else:
            if self.config.outputDir:
                if self.config.outputName:
                    return f"{self.config.outputDir}/{self.config.outputName}.%(ext)s"
                return f"{self.config.outputDir}/%(title)s.%(ext)s"
            else:
                if self.config.outputName:
                    return f"{self.config.outputName}.%(ext)s"
                return "%(title)s.%(ext)s"
