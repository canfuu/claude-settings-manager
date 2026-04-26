"""
Build script for Claude Settings Manager
Uses PyInstaller to create a standalone executable
"""
import os
import sys
import subprocess
from pathlib import Path


def build_exe():
    """Build the executable using PyInstaller"""
    print("Building Claude Settings Manager...")

    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=ClaudeSettingsManager",
        "--onefile",
        "--windowed",
        "--clean",
        "main.py"
    ]

    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)

    # Run PyInstaller
    result = subprocess.run(cmd, check=True)

    print("-" * 60)
    print("\nBuild completed successfully!")
    print(f"Executable location: dist/ClaudeSettingsManager.exe")

    return result.returncode == 0


if __name__ == "__main__":
    try:
        success = build_exe()
        sys.exit(0 if success else 1)
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error code: {e.returncode}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nBuild cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
