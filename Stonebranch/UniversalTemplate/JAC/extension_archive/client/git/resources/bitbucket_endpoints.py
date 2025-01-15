# Convert the http baseurl to REST API appropriate
# https://bitbucket.org -> https://api.bitbucket.org/2.0
#
# Bit Bucket Cloud does not support custom domains,
# so the baseurl should always be https://api.bitbucket.org.

PUBLIC_REPOSITORIES = "{base_url}/2.0/repositories?role=contributor"
REPO_BRANCHES = "{base_url}/2.0/repositories/{repo_full_name}/refs/branches"
LIST_BRANCH = "{base_url}/2.0/repositories/{repo_full_name}/src/{branch}/{dirpath}"
REPO_SOURCE = "{base_url}/2.0/repositories/{repo_full_name}/src/"
COMMIT_DIFFSTATS = "{base_url}/2.0/repositories/{repo_full_name}/diffstat/{commits}"
