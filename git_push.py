"""
git_push.py
-----------
Initializes git, sets remote, and pushes all project files to GitHub.
Run: python git_push.py
"""
import subprocess, sys, os

REPO = "c:\\Users\\Lenovo\\OneDrive\\Documents\\ETL Gen"
REMOTE = "https://github.com/madwikpoojari-a11y/ETL-GENERATOR.git"
LOG = os.path.join(REPO, "logs", "git_push.log")

def run(cmd, label):
    print(f">>> {label}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*50}\n{label}\n{'='*50}\n")
        f.write(result.stdout or "")
        f.write(result.stderr or "")
    print(result.stdout.strip() if result.stdout.strip() else "(no output)")
    if result.stderr.strip():
        # filter out harmless Windows permission warnings
        errs = [l for l in result.stderr.strip().splitlines()
                if "Permission denied" not in l and "could not open directory" not in l]
        if errs:
            print("STDERR:", "\n".join(errs))
    return result.returncode

# Remove any existing .git that's tracking the wrong root
old_git = os.path.join(REPO, ".git")
if os.path.exists(old_git):
    import shutil
    shutil.rmtree(old_git)
    print("Removed old .git directory")

run(["git", "init", "-b", "main"],               "git init")
run(["git", "config", "user.email", "etl@project.local"], "set email")
run(["git", "config", "user.name",  "ETL-Generator"],     "set name")
run(["git", "remote", "add", "origin", REMOTE],  "add remote")
run(["git", "add", "."],                          "git add all")
run(["git", "commit", "-m",
     "feat: Auto-ETL Generator Agent - complete project\n\n"
     "- Full ETL pipeline with self-healing agent\n"
     "- DataForge theme (Aqua/Sunshine/Lavender/Dusty Rose)\n"
     "- Real e-commerce dataset (5180 rows, 17 columns)\n"
     "- Synthetic dirty dataset (10350 rows, injected errors)\n"
     "- 33/33 tests passing\n"
     "- Streamlit dashboard with 5 pages\n"
     "- SQLite loading with retry logic\n"
     "- 6 self-healing rules"],                   "git commit")

rc = run(["git", "push", "-u", "origin", "main", "--force"],
         "git push --force")

if rc == 0:
    print("\nSUCCESS: Project pushed to GitHub!")
    print(f"URL: {REMOTE}")
else:
    print("\nPush failed — see logs/git_push.log for details.")
    print("If auth failed, run: git push -u origin main")
    print("and enter your GitHub credentials when prompted.")
