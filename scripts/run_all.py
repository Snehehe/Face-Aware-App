import subprocess
import sys
from pathlib import Path

VENV_PYTHON = Path(".venv") / "Scripts" / "python.exe"

def run(module, desc):
    print(f"\n=== {desc} ===")
    cmd = f'"{VENV_PYTHON}" -m {module}'
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Failed during: {desc}")
        sys.exit(1)

def main():
    run("scripts.run_monitor", "Running face recognition + logging")
    run("scripts.train_model", "Training app usage model")
    run("scripts.suggest_and_launch", "Suggesting next app")
    print("\nDone.")

if __name__ == "__main__":
    main()
