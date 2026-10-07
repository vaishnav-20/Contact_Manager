"""
Packaging automation script for Contact Manager Pro using PyInstaller.
Builds standalone ContactManagerPro.exe with embedded icons, assets, and dependencies.
"""
import sys
import os
import subprocess
import argparse
from pathlib import Path

def build(check_only=False):
    project_dir = Path(__file__).resolve().parent
    spec_file = project_dir / "ContactManagerPro.spec"
    
    if not spec_file.exists():
        print(f"Error: Spec file not found at {spec_file}")
        sys.exit(1)
        
    print(f"=== Contact Manager Pro Packaging Tool ===")
    print(f"Project Directory: {project_dir}")
    print(f"Spec File: {spec_file.name}")
    
    if check_only:
        print("[CHECK MODE] Verifying environment & dependencies...")
        try:
            import PyInstaller
            import sqlalchemy
            import pandas
            import matplotlib
            import openpyxl
            import PIL
            print(f"• PyInstaller: {PyInstaller.__version__}")
            print(f"• SQLAlchemy: {sqlalchemy.__version__}")
            print(f"• Pandas: {pandas.__version__}")
            print(f"• Matplotlib: {matplotlib.__version__}")
            print(f"• OpenPyXL: {openpyxl.__version__}")
            print("Environment verification PASSED! Ready to build executable.")
            return
        except ImportError as e:
            print(f"Missing dependency: {e}")
            sys.exit(1)

    print("Launching PyInstaller build process...")
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_file)
    ]
    res = subprocess.run(cmd, cwd=str(project_dir))
    if res.returncode == 0:
        dist_exe = project_dir / "dist" / "ContactManagerPro.exe"
        print("=" * 60)
        print("🎉 BUILD SUCCESSFUL!")
        print(f"Standalone Executable: {dist_exe}")
        print("=" * 60)
    else:
        print(f"Build failed with exit code {res.returncode}")
        sys.exit(res.returncode)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Perform sanity check only")
    args = parser.parse_args()
    build(check_only=args.check)
