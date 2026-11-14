import subprocess, os
REPO = r"c:\Users\Lenovo\OneDrive\Documents\ETL Gen"
LOG  = os.path.join(REPO, "logs", "git_push.log")

def run(cmd, label):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*50}\n{label}\n{r.stdout}\n{r.stderr}\n")
    if r.stdout.strip(): print(r.stdout.strip())
    errs = [l for l in (r.stderr or "").splitlines()
            if "Permission denied" not in l and "could not open" not in l
            and "LF will be" not in l and l.strip()]
    if errs: print("STDERR:", "\n".join(errs))
    return r.returncode

run(["git", "add", "."], "add")
run(["git", "commit", "-m",
     "deploy: add Streamlit Cloud config\n\n"
     "- .streamlit/config.toml with dark theme\n"
     "- cleaned requirements.txt for cloud compatibility\n"
     "- .gitignore updated to track config but not secrets"], "commit")
rc = run(["git", "push", "-u", "origin", "main", "--force"], "push")
print("SUCCESS" if rc == 0 else "FAILED")
