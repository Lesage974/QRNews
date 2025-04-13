import shutil
import os
import datetime
import subprocess
from datetime import datetime

# Paths
REPO_PATH = "/home/pdfuploader/qrnews"
PDF_SOURCE = os.path.join(REPO_PATH, "latest.pdf")
DOCS_DIR = os.path.join(REPO_PATH, "QRNews")
PDF_DEST = os.path.join(DOCS_DIR, "latest.pdf")

def update_github_repo():
    print("Copying PDF to repo...")
    print(PDF_SOURCE)
    print(PDF_DEST)

    #Make a pull to be up to date
    os.chdir(DOCS_DIR)
    subprocess.run(["git", "pull"])

    # Make sure the 'docs' folder exists
    os.makedirs(DOCS_DIR, exist_ok=True)

    shutil.copy(PDF_SOURCE, PDF_DEST)

    print("Committing and pushing to GitHub...")
    subprocess.run(["git", "add", "latest.pdf"])
    commit_msg = f"Update PDF on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    subprocess.run(["git", "commit", "-m", commit_msg])
    subprocess.run(["git", "push"])

if __name__ == "__main__":
    update_github_repo()

