from client.git.utils import URLString

REF_HEADS = URLString("{base_url}/_apis/git/repositories/{repo}/refs/heads/")
PUSH = URLString("{base_url}/_apis/git/repositories/{repo}/pushes")
BRANCH_FILES = URLString(
    "{base_url}/_apis/git/repositories/{repo}/items?recursionLevel=Full&versionDescriptor.version={branch}&scopePath={filepath}"
)
ITEM = URLString(
    "{base_url}/_apis/git/repositories/{repo}/items?path={filepath}&versionDescriptor.version={branch}"
)
ITEM_CONTENT = URLString(
    "{base_url}/_apis/git/repositories/{repo}/items?path={filepath}&includeContent=true&versionDescriptor.versionType=branch&versionDescriptor.version={branch}"
)
COMMIT = URLString("{base_url}/_apis/git/repositories/{repo}/commits/{id}/changes")
REPOS = URLString("{base_url}/_apis/git/repositories")
