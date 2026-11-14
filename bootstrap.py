"""
bootstrap.py
------------
Run this once to install all dependencies and generate the dataset.
Usage: python bootstrap.py
"""

import subprocess
import sys
import os

BASE = os.path.dirname(os.path.abspath(__file__))
LOG  = os.path.join(BASE, "logs", "bootstrap.log")
os.makedirs(os.path.join(BASE, "logs"), exist_ok=True)

def run(cmd, label):
    print(f"\n>>> {label}")
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n{label}\n{'='*60}\n")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=BASE
    )
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(result.stdout)
        f.write(result.stderr)
    if result.returncode == 0:
        print(f"    OK")
    else:
        print(f"    FAILED (exit {result.returncode})")
        print(result.stderr[-500:] if result.stderr else "no stderr")
    return result.returncode

# Step 1: install deps
rc = run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], "pip install")

# Step 2: generate dataset
rc2 = run([sys.executable, "data/generate_dataset.py"], "generate dataset")

print(f"\nBootstrap complete. See logs/bootstrap.log for details.")
print(f"Now run:  streamlit run app.py")
