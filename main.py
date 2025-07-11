# updater_app.py

import sys
import os
import shutil
import tempfile
import zipfile
import requests
import time
from packaging import version
from apscheduler.schedulers.background import BackgroundScheduler

GITHUB_OWNER = "your-username"
GITHUB_REPO  = "your-repo"
CURRENT_VERSION = "1.0.0"
API_LATEST = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"

def check_for_update():
    try:
        r = requests.get(API_LATEST, timeout=10)
        r.raise_for_status()
        data = r.json()
        tag = data["tag_name"].lstrip("v")
        if version.parse(tag) > version.parse(CURRENT_VERSION):
            asset = next(a for a in data["assets"] if a["name"].endswith(".zip"))
            return tag, asset["browser_download_url"]
    except Exception:
        pass
    return None, None

def download_update(url):
    resp = requests.get(url, stream=True)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    for chunk in resp.iter_content(1024*1024):
        tmp.write(chunk)
    tmp.close()
    return tmp.name

def apply_update(zip_path, target_dir):
    # Extract into a temp folder
    extract_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(extract_dir)

    # Overwrite files in target_dir
    for root, dirs, files in os.walk(extract_dir):
        rel = os.path.relpath(root, extract_dir)
        dest = os.path.join(target_dir, rel)
        os.makedirs(dest, exist_ok=True)
        for f in files:
            src_file = os.path.join(root, f)
            dst_file = os.path.join(dest, f)
            # Copy and overwrite
            shutil.copy2(src_file, dst_file)

    # Clean up
    os.remove(zip_path)
    shutil.rmtree(extract_dir)

def launch_update(zip_path):
    exe = sys.executable  # if packaged via PyInstaller, this is your .exe
    # Relaunch self in update mode
    # On Windows, close handles by exiting now, then the child can overwrite files
    os.spawnv(os.P_NOWAIT, exe, [exe, "--update", zip_path])
    sys.exit()

def do_normal_startup():
    # Your real app logic goes here...
    print("Application running version", CURRENT_VERSION)
    # e.g. start your GUI or CLI loop

def schedule_periodic_check():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_startup_update_check, 'interval',
                      hours=24, next_run_time=time.time()+24*3600)
    scheduler.start()
    return scheduler

def run_startup_update_check():
    tag, url = check_for_update()
    if url:
        zip_path = download_update(url)
        launch_update(zip_path)

def main():
    # If we're in update mode, args are: [exe, "--update", "path/to/zip"]
    if len(sys.argv) == 3 and sys.argv[1] == "--update":
        zip_path = sys.argv[2]
        # Target directory: where the exe lives
        target_dir = os.path.dirname(sys.executable)
        # Wait a moment for parent to exit and release locks
        time.sleep(1)
        apply_update(zip_path, target_dir)
        # Relaunch the updated app normally
        os.spawnv(os.P_NOWAIT, sys.executable, [sys.executable])
        sys.exit()

    # Normal startup: check once immediately...
    run_startup_update_check()

    # ...then schedule every 24h
    scheduler = schedule_periodic_check()

    # Continue with your app
    do_normal_startup()

    # Keep process alive if you need the scheduler
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    main()
