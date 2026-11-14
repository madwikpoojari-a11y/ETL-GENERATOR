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

run(["git", "add", "."], "git add")
run(["git", "commit", "-m",
     "feat: enterprise UI redesign v2.0 - RiskGraph-inspired dark theme\n\n"
     "FRONTEND OVERHAUL:\n"
     "- Full dark theme: bg #0B1020, card #1E293B, border #334155\n"
     "- JetBrains Mono for all numeric values\n"
     "- Inter font throughout\n"
     "- Plotly charts: gauge, bar, donut, area, grouped bar\n"
     "- Animated pipeline stage nodes (done/run/warn/fail/idle states)\n"
     "- KPI cards with hover animations and delta indicators\n"
     "- Self-healing monitor with color-coded rule cards\n"
     "- Execution timeline component\n"
     "- Dataset side-by-side comparison (raw vs cleaned)\n"
     "- Null distribution bar chart\n"
     "- Issue distribution donut chart\n"
     "- Quality gauge charts before/after\n"
     "- Dimension comparison grouped bar chart\n"
     "- Professional sidebar with pipeline status indicator\n"
     "- Section labels in uppercase with letter-spacing\n"
     "- All pages redesigned: Command Center, Upload, Validation, Pipeline, Reports\n\n"
     "DEPENDENCIES:\n"
     "- Added plotly>=5.18.0 to requirements.txt\n\n"
     "DOCS:\n"
     "- Updated README tech stack with Plotly and UI theme details"],
    "git commit")
rc = run(["git", "push", "-u", "origin", "main", "--force"], "git push")
print("\nSUCCESS" if rc == 0 else "\nFAILED")
