import os
import shutil
import subprocess
import datetime

# Use current working directory as repo root
d = os.getcwd()
PDF_SOURCE = os.path.join(d, "latest.pdf")
DOCS_DIR = os.path.join(d, "docs")
PDF_DEST = os.path.join(DOCS_DIR, "latest.pdf")


def run(cmd):
    """Run a shell command, print stdout/stderr."""
    print(f"Running: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=d, capture_output=True, text=True)
    if proc.stdout:
        print(proc.stdout.strip())
    if proc.stderr:
        print(proc.stderr.strip())
    return proc


def update_site():
    print("\n== Copying PDF to docs folder ==")
    os.makedirs(DOCS_DIR, exist_ok=True)
    shutil.copy(PDF_SOURCE, PDF_DEST)

    print("\n== Sync remote changes ==")
    run(["git", "pull", "origin", "main"]);  # fetch latest

    print("\n== Staging update ==")
    run(["git", "add", "docs/latest.pdf"])

    # Check if there is anything to commit
    check = run(["git", "diff", "--cached", "--quiet"])
    if check.returncode != 0:
        commit_msg = f"Automated PDF update: {datetime.datetime.now().isoformat()}"
        print(f"\n== Committing: {commit_msg} ==")
        run(["git", "commit", "-m", commit_msg])
        print("\n== Pushing to origin/main ==")
        run(["git", "push", "origin", "main"])
    else:
        print("\nNo changes detected; nothing to commit or push.")


if __name__ == "__main__":
    update_site()
