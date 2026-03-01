#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import platform
import sysconfig

# Project Paths
ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(ROOT, "build")
DIST_DIR = os.path.join(ROOT, "releases")
SRC_DIR = os.path.join(ROOT, "src")
VENV_DIR = os.path.join(ROOT, "venv")
APP_NAME = "yt-audio"

def log(msg): print(f"[*] {msg}")
def error(msg): print(f"[!] Error: {msg}", file=sys.stderr)

def get_main_script():
    paths = [os.path.join(SRC_DIR, "main.py"), os.path.join(ROOT, "main.py")]
    for p in paths:
        if os.path.exists(p): return p
    return None

def get_cython():
    if os.path.isdir(VENV_DIR):
        bin_dir = "Scripts" if sys.platform == "win32" else "bin"
        exe = "cython.exe" if sys.platform == "win32" else "cython"
        path = os.path.join(VENV_DIR, bin_dir, exe)
        if os.path.exists(path): return path
    return shutil.which("cython")

def bundle_dependencies():
    """Copy Python shared libraries to the releases folder for portability.
    NOTE: Bundling can sometimes interfere with standard library discovery in Wine/embedded.
    """
    log("Bundling Python dependencies...")
    if sys.platform == "win32":
        dll_name = f"python{sys.version_info.major}{sys.version_info.minor}.dll"
        search_dirs = [sys.base_prefix, os.path.join(sys.base_prefix, "bin"), "C:\\Windows\\System32"]
        for d in search_dirs:
            dll_path = os.path.join(d, dll_name)
            if os.path.exists(dll_path):
                shutil.copy(dll_path, DIST_DIR)
                log(f"Bundled: {dll_name}")
                return
        log("Warning: Could not find Python DLL to bundle.")
    elif sys.platform == "linux":
        lib_name = f"libpython{sys.version_info.major}.{sys.version_info.minor}.so.1.0"
        lib_dir = sysconfig.get_config_var('LIBDIR')
        if lib_dir:
            lib_path = os.path.join(lib_dir, lib_name)
            if os.path.exists(lib_path):
                shutil.copy(lib_path, DIST_DIR)
                log(f"Bundled: {lib_name}")

def build():
    log("Building executable...")
    
    main_script = get_main_script()
    if not main_script:
        error("main.py not found.")
        sys.exit(1)
        
    cython = get_cython()
    if not cython:
        error("Cython not found. Install it: pip install cython")
        sys.exit(1)
        
    os.makedirs(BUILD_DIR, exist_ok=True)
    os.makedirs(DIST_DIR, exist_ok=True)
    
    c_out = os.path.join(BUILD_DIR, "main.c")
    log(f"Transpiling {os.path.basename(main_script)} -> {os.path.basename(c_out)}")
    subprocess.run([cython, main_script, "--embed", "-o", c_out], check=True)
    
    log("Compiling...")
    
    if sys.platform == "win32":
        inc = sysconfig.get_path('include')
        lib = os.path.join(sys.base_prefix, "libs")
        
        if shutil.which("cl"):
            py_lib = f"python{sys.version_info.major}{sys.version_info.minor}.lib"
            cmd = ["cl", "/O2", c_out, f"/I{inc}", "/link", f"/LIBPATH:{lib}", py_lib, f"/OUT:{os.path.join(BUILD_DIR, APP_NAME + '.exe')}"]
            subprocess.run(cmd, check=True)
        elif shutil.which("gcc"):
            py_lib = f"python{sys.version_info.major}{sys.version_info.minor}"
            out_exe = os.path.join(BUILD_DIR, APP_NAME + ".exe")
            cmd = ["gcc", "-O2", c_out, "-municode", "-mconsole", f"-I{inc}", f"-L{lib}", f"-l{py_lib}", "-o", out_exe]
            log(f"Using MinGW: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
        else:
            error("No compiler (cl.exe or gcc) found in PATH.")
            sys.exit(1)
    else:
        py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
        py_cfg = shutil.which(f"python{py_ver}-config") or shutil.which("python3-config")
        
        if not py_cfg:
             error("python-config utility missing. Please install python3-dev or equivalent.")
             sys.exit(1)
             
        # Extract flags safely
        cflags = subprocess.check_output([py_cfg, "--cflags"]).decode().split()
        ldflags = subprocess.check_output([py_cfg, "--ldflags"]).decode().split()
        
        out_bin = os.path.join(BUILD_DIR, APP_NAME)
        # Use RPATH to look for libpython in the same directory as the binary
        rpath = "-Wl,-rpath,'$ORIGIN'" if sys.platform == "linux" else ""
        cmd = ["gcc", c_out] + cflags + ldflags + ([rpath] if rpath else []) + [f"-lpython{py_ver}", "-o", out_bin]
        subprocess.run(cmd, check=True)
        
    ext = ".exe" if sys.platform == "win32" else ""
    shutil.copy(os.path.join(BUILD_DIR, APP_NAME + ext), os.path.join(DIST_DIR, APP_NAME + ext))
    
    log(f"Done! Created: {os.path.join(DIST_DIR, APP_NAME + ext)}")

def clean():
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
        log("Cleaned build directory.")
    else:
        log("Everything is already clean.")

if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else "build"
    if task == "build": build()
    elif task == "clean": clean()
    elif task == "bundle": bundle_dependencies()
    else: print(f"Usage: {sys.argv[0]} [build|clean|bundle]")
