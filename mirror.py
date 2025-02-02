import requests
import os
import subprocess
import shutil

# 🔒 Securely fetch GitHub token from environment variable
GITHUB_TOKEN = os.getenv("MY_SECRET_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("❌ Secret token is missing! Set MY_SECRET_TOKEN as an environment variable.")

# Source users whose repos will be mirrored
SOURCE_USERS = ["ubg98", "ubg44"]
TARGET_USERNAME = "your_target_username"  # Change this to your GitHub username
TARGET_ORG = None  # Change to your org name if pushing to an organization

# Headers for API authentication
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# Create a temporary directory to store cloned repos
TEMP_DIR = "mirrored_repos"
if os.path.exists(TEMP_DIR):
    shutil.rmtree(TEMP_DIR)  # Clean up old files
os.makedirs(TEMP_DIR)

def get_repos(user):
    """Fetch all repositories from a given user"""
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{user}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ Error fetching repos for {user}: {response.json()}")
            break
        repo_data = response.json()
        if not repo_data:
            break
        repos.extend(repo_data)
        page += 1
    return repos

def mirror_repo(repo):
    """Clone, mirror, and push repo to target account"""
    repo_name = repo["name"]
    source_clone_url = repo["clone_url"]
    
    # Determine target URL
    if TARGET_ORG:
        target_url = f"https://{GITHUB_TOKEN}@github.com/{TARGET_ORG}/{repo_name}.git"
    else:
        target_url = f"https://{GITHUB_TOKEN}@github.com/{TARGET_USERNAME}/{repo_name}.git"

    print(f"🔄 Mirroring {repo_name}...")

    try:
        # Clone repo as a mirror
        repo_path = os.path.join(TEMP_DIR, repo_name)
        subprocess.run(["git", "clone", "--mirror", source_clone_url, repo_path], check=True)

        # Push the mirrored repo to target
        os.chdir(repo_path)
        subprocess.run(["git", "remote", "set-url", "--push", "origin", target_url], check=True)
        subprocess.run(["git", "push", "--mirror"], check=True)
        os.chdir("../..")

        print(f"✅ Successfully mirrored {repo_name} to {TARGET_USERNAME}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error mirroring {repo_name}: {e}")

# Fetch and mirror repositories for all users
for user in SOURCE_USERS:
    repos = get_repos(user)
    print(f"📂 Found {len(repos)} repos for {user}")
    for repo in repos:
        mirror_repo(repo)

print("🎉 All repositories have been mirrored successfully!")
