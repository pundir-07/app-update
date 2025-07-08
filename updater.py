import os
import requests
import subprocess
import sys

GITHUB_API_URL = "https://github.com/pundir-07/app-update/releases/latest"

def check_for_updates():
    response = requests.get(GITHUB_API_URL)
    if response.status_code == 200:
        latest_release = response.json()
        latest_version = latest_release['tag_name']
        return latest_version
    else:
        print("Failed to fetch the latest release information.")
        return None

def download_update(download_url):
    response = requests.get(download_url)
    if response.status_code == 200:
        with open("app_latest.exe", "wb") as file:
            file.write(response.content)
        print("Update downloaded successfully.")
    else:
        print("Failed to download the update.")

def install_update():
    if os.path.exists("app_latest.exe"):
        subprocess.call(["app_latest.exe"])
        print("Update installed. Please restart the application.")
    else:
        print("No update file found.")

def main():
    current_version = "1.0.0"  # Replace with your current version
    latest_version = check_for_updates()

    if latest_version and latest_version != current_version:
        print(f"A new version {latest_version} is available.")
        download_url = f"https://github.com/pundir-07/app-update/releases/download/{latest_version}/app_latest.exe"  # Adjust the URL as needed
        download_update(download_url)
        install_update()
    else:
        print("You are using the latest version.")

if __name__ == "__main__":
    main()