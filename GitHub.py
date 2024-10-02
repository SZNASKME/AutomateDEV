from github import Github

from Stonebranch.utils.readFile import loadJson

# Replace with your GitHub token

Auth = loadJson('Auth.json')
Token = Auth['GitHubToken']
g = Github(Token)
# Get the authenticated user
user = g.get_user()
print(f"Authenticated as: {user.login}")
