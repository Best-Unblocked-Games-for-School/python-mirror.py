import requests
import os
import subprocess

# GitHub Credentials (using the secret token from environment variable)
GITHUB_TOKEN = os.getenv("GH_MIRROR_TOKEN")  # GitHub token from secret environment variable
SOURCE_USERS = ["ubg98", "ubg17"]  # List of source users whose repos you want to mirror

if not GITHUB_TOKEN:
    print("Error: GitHub token not found in environment variables.")
    exit(1)

# Headers for API authentication
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# Create a directory to store cloned repos
if not os.path.exists("mirrored_repos"):
    os.makedirs("mirrored_repos")

def get_repos(user):
    """Fetch all repositories from a given user"""
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{user}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Error fetching repos for {user}: {response.json()}")
            break
        repo_data = response.json()
        if not repo_data:
            break
        repos.extend(repo_data)
        page += 1
    return repos

def mirror_repo(repo):
    """Clone, mirror, and push repo to your account"""
    repo_name = repo["name"]
    source_clone_url = repo["clone_url"]
    target_url = f"https://{GITHUB_TOKEN}@github.com/{repo['owner']['login']}/{repo_name}.git"

    print(f"Cloning {repo_name}...")

    # Clone the repo as a mirror
    try:
        subprocess.run(["git", "clone", "--mirror", source_clone_url, f"mirrored_repos/{repo_name}"], check=True)
    except subprocess.CalledProcessError:
        print(f"Failed to clone {repo_name}")
        return

    # Push the mirrored repo to the same user's account using token-based authentication
    try:
        os.chdir(f"mirrored_repos/{repo_name}")
        subprocess.run(["git", "remote", "set-url", "--push", "origin", target_url], check=True)
        subprocess.run(["git", "push", "--mirror"], check=True)
        os.chdir("../..")
        print(f"Successfully mirrored {repo_name}")
    except subprocess.CalledProcessError:
        print(f"Failed to push {repo_name} to your account")

# Fetch and mirror repositories for all users
for user in SOURCE_USERS:
    repos = get_repos(user)
    print(f"Found {len(repos)} repos for {user}")
    for repo in repos:
        mirror_repo(repo)

print("✅ All repositories have been mirrored successfully!")
