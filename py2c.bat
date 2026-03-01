@echo off
setlocal enabledelayedexpansion
set "ROOT=%~dp0"
cd /d "%ROOT%"

:: Discover Python 3
set PYTHON=
for %%P in (python py python3) do (
    if "!PYTHON!"=="" (
        %%P --version >nul 2>&1
        if !errorlevel! equ 0 (
            %%P -c "import sys; sys.exit(0 if sys.version_info.major == 3 else 1)" >nul 2>&1
            if !errorlevel! equ 0 (
                set "PYTHON=%%P"
            )
        )
    )
)

if "!PYTHON!"=="" (
    echo [!] Error: Python 3 not found in PATH.
    exit /b 1
)

!PYTHON! "%ROOT%py2c.py" %*

if !errorlevel! neq 0 (
    echo [!] Build failed.
    exit /b !errorlevel!
)

endlocal
