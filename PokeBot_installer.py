#!/usr/bin/env python
import subprocess
import sys
import os

REQUIREMENTS_FILE = "requirements.txt"

def create_requirements_file():
    if not os.path.exists(REQUIREMENTS_FILE):
        print(f"{REQUIREMENTS_FILE} not found. Creating one...")
        with open(REQUIREMENTS_FILE, "w") as f:
            f.write("requests\nbeautifulsoup4\n")
        print(f"{REQUIREMENTS_FILE} created.")

def install_dependencies():
    create_requirements_file()
    try:
        print("Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print("Error: Failed to install dependencies.")
        sys.exit(1)

if __name__ == "__main__":
    install_dependencies()
    print("\nSetup thing is complete. You may now do the thing.... (e.g., 'python .\PokeBot.py').")
