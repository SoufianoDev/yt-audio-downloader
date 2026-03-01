# YouTube Audio Downloader

[![macOS Build Validation](https://github.com/SoufianoDev/yt-audio-downloader/actions/workflows/macos.yml/badge.svg)](https://github.com/SoufianoDev/yt-audio-downloader/actions/workflows/macos.yml)

A robust, cross-platform CLI tool for extracting high-quality audio from YouTube. It features an interactive guided mode, a precise command-line interface, and a built-in Cython build system for creating standalone executables.

## Core Features

- **Native Audio Processing:** Uses `PyAV` (`av`) directly—**no external `ffmpeg` binary required**.
- **Interactive & CLI Modes:** Choose between guided prompts or direct command-line arguments.
- **Environment-Aware:** Automatically discovers and adapts to your local Python 3 interpreter (3.8 - 3.13).
- **Standalone Builds:** Compile the project into a C-based executable using the included `py2c` tool.
- **Cross-Platform:** Full support for Linux, macOS, and Windows (7+).

---

## Quick Start (Build & Run)

The recommended way to use this tool is by building a standalone executable. This ensures all internal paths and dependencies are correctly aligned with your local environment.

### 1. Setup & Install Dependencies
```bash
# Clone the repository
git clone https://github.com/SoufianoDev/yt-audio-downloader.git
cd yt-audio-downloader

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Build the Executable
Use the included `py2c` tool to compile the project into a native binary.

**Linux / macOS:**
```bash
chmod +x py2c
./py2c build
```

**Windows:**
```bash
py2c.bat build
```

### 3. Run the Release
The standalone binary will be generated in the `releases/` folder.

**Interactive Mode:**
```bash
./releases/yt-audio        # Linux / macOS
releases\yt-audio.exe       # Windows
```

---

## Why Build?
- **Portability:** The binary uses **Dynamic Linking** to align with the host's Python environment, ensuring it works even if your Python version differs from the build machine.
- **Performance:** Cython transpilation provides a modest boost and protects the source code.
- **Zero Configuration:** The build system auto-discovers `python3-dev` headers and compilers.

---

## Detailed Usage

### Command Line Interface
Pass arguments directly for automation or power use:
```bash
./releases/yt-audio "https://www.youtube.com/..." -f mp3 -q 192k
```

**Available Options:**
- `-o`, `--output-dir`: Path to save the audio.
- `-n`, `--output-name`: Custom filename (uses video title by default).
- `-f`, `--format`: Extension (`mp3`, `m4a`, `wav`, `opus`, `flac`, etc.).
- `-q`, `--quality`: Bitrate or quality level (e.g., `192k`, `0`).
- `-k`, `--keep-video`: Retain the source `.webm`/`.mp4` file after conversion.

---

## Prerequisites

- **Python 3.8+:** Any installed version will be auto-detected.
- **C Compiler:** `gcc`, `clang`, or MSVC (for building only).
- **Python Headers:** `python3-dev` (Linux) or a standard Windows/macOS Python install.

## Build System & CI
The project uses GitHub Actions to automatically validate macOS builds on every push, ensuring the Cython toolchain remains stable.

## License
MIT
