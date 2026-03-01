#!/usr/bin/env python3
import os
import sys
import subprocess

def setup_environment():
    """Sets up the environment, including sys.path and venv discovery."""
    try:
        current_file = os.path.abspath(__file__)
        if "built-in" in current_file:
             raise NameError("Embedded")
        base_dir = os.path.dirname(current_file)
    except (NameError, TypeError):
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    # 1. Add source directory to sys.path
    search_paths = [
        base_dir,
        os.path.join(base_dir, "src"),
        os.path.join(os.path.dirname(base_dir), "src"),
        os.path.join(os.getcwd(), "src")
    ]
    
    found_src = None
    for p in search_paths:
        if os.path.isdir(os.path.join(p, "downloader")):
            if p not in sys.path:
                sys.path.insert(0, p)
            found_src = p
            break

    # 2. Virtual environment / Site-packages discovery
    try:
        import yt_dlp
    except ImportError:
        # Search for venv
        current = found_src or base_dir
        for _ in range(3):
            venv_dir = os.path.join(current, 'venv')
            if os.path.isdir(venv_dir):
                if sys.platform == "win32":
                    site_pkgs = os.path.join(venv_dir, 'Lib', 'site-packages')
                else:
                    py_ver = f"python{sys.version_info.major}.{sys.version_info.minor}"
                    site_pkgs = os.path.join(venv_dir, 'lib', py_ver, 'site-packages')

                if os.path.exists(site_pkgs) and site_pkgs not in sys.path:
                    sys.path.insert(0, site_pkgs)
                return
            
            parent = os.path.dirname(current)
            if parent == current: break
            current = parent
        
        # 3. Active Discovery: Ask the system's python where site-packages are
        for cmd in ["python3", "python", "py"]:
            try:
                # Get site-packages via subprocess
                code = "import site; print(site.getsitepackages()[0])"
                path = subprocess.check_output([cmd, "-c", code], 
                                             stderr=subprocess.DEVNULL,
                                             encoding='utf-8', 
                                             shell=(sys.platform == 'win32')).strip()
                if os.path.isdir(path) and path not in sys.path:
                    sys.path.append(path)
                    # Try to import again
                    import yt_dlp
                    return
            except:
                continue

setup_environment()

from downloader.parsers import ConfigParser
from downloader.core import YouTubeAudioDownloader

def main():
    if len(sys.argv) == 1:
        try:
            config = ConfigParser.fromInteractive()
        except KeyboardInterrupt:
            print("\nDownload cancelled.")
            sys.exit(0)
    else:
        config = ConfigParser.fromCommandLine()
        if not config.url:
            print("Error: URL is required. Use -h for help.", file=sys.stderr)
            sys.exit(1)

    downloader = YouTubeAudioDownloader(config)
    downloader.download()

if __name__ == '__main__':
    main()
