from typing import Any, Optional

from github import Github, InputGitTreeElement
from github.GithubException import (
    BadCredentialsException,
    GithubException,
    UnknownObjectException,
)
from github.Requester import (
    HTTPRequestsConnectionClass,
    HTTPSRequestsConnectionClass,
    Requester,
)

from client.git.base import GitClient
from client.git.exceptions import (
    GitAuthException,
    GitClientException,
    GitFileNotExistError,
    GitRepoNotExistException,
)
from enums.enums import ProxyTypeEnum
from logger import logger

BRANCH_NOT_SET = "git_branch is not set"
REPO_NOT_SET = "git_repo is not set"


class GitHTTPSRequestsConnectionClass(HTTPSRequestsConnectionClass):
    proxy: Optional[dict] = None
    ca_file: Optional[str] = None

    def __init__(
        self,
        host,
        port=None,
        strict=False,
        timeout=None,
        retry=None,
        pool_size=None,
        **kwargs,
    ):
        super().__init__(
            host,
            port,
            strict,
            timeout,
            retry,
            pool_size,
            **kwargs,
        )
        self.session.proxies = self.proxy
        self.session.verify = self.ca_file


class GitHubClient(GitClient):  # pragma: no cover
    @property
    def git_branch(self):
        return self._git_branch

    @git_branch.setter
    def git_branch(self, git_branch: str) -> None:
        self._git_branch = git_branch

    @property
    def git_repo(self):
        return self._git_repo

    @git_repo.setter
    def git_repo(self, repo_path: str) -> None:
        try:
            self._git_repo = self.client.get_repo(repo_path)
        except UnknownObjectException as e:
            raise GitRepoNotExistException(f"Repository not found: {repo_path}.") from e
        except BadCredentialsException:
            raise GitAuthException(
                f"Failed to authenticate for {self.git_url}. Wrong git credentials."
            )

    def _init_client(self):
        if self.proxy_type in {
            ProxyTypeEnum.HTTP,
            ProxyTypeEnum.HTTPS,
            ProxyTypeEnum.HTTPS_CREDENTIALS,
        }:
            GitHTTPSRequestsConnectionClass.proxy = self.session.proxies
            GitHTTPSRequestsConnectionClass.ca_file = self.session.verify

            Requester.injectConnectionClasses(
                HTTPRequestsConnectionClass, GitHTTPSRequestsConnectionClass
            )
        logger.debug("Establishing connection with GitHub...")
        logger.debug(f"Verify certification: {self.verify}. Git url: {self.git_url}")
        try:
            if self.git_url:
                self.client = Github(
                    self.git_token, base_url=self.git_url, verify=self.verify
                )
                logger.debug("Connection Established successfully")
            else:
                self.client = Github(self.git_token, verify=self.verify)
        except BadCredentialsException:
            raise GitAuthException(
                f"Failed to authenticate for {self.git_url}. Wrong git credentials."
            )

    def get_repos_list(self) -> Optional[list]:
        repo_list = []
        try:
            repos = self.client.get_user()
            for repo in repos.get_repos():
                repo_list.append(repo.full_name)
            return repo_list
        except GithubException as e:
            raise GitClientException(str(e)) from e

    def get_repo_branches(self, repo_path: str) -> Optional[list]:
        branch_list = []
        try:
            git_repo = self.client.get_repo(repo_path)
            branches = git_repo.get_branches()
            for branch in branches:
                branch_list.append(branch.name)
            return branch_list
        except GithubException as e:
            raise GitRepoNotExistException(
                f"Repository not found: {repo_path}. Cannot retrieve branches."
            ) from e

    def get_branch_files(self, branch_name: str, path: str = "") -> Optional[list]:
        files = []

        # get all the contents of the repo
        contents = self.git_repo.get_contents(path, ref=branch_name)

        while len(contents) > 0:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(
                    self.git_repo.get_contents(file_content.path, ref=branch_name)
                )
            else:
                if "/" in file_content.path:
                    files.append(file_content.path)
        return files

    def filepath_exists(self, filepath: str) -> bool:

        self.call_asserts(self.git_branch, self.git_repo)

        try:
            self.git_repo.get_contents(filepath, ref=self.git_branch)
            return True
        except UnknownObjectException:
            return False

    def get_file_contents(self, file_name: str) -> Optional[str]:

        self.call_asserts(self.git_branch, self.git_repo)
        try:
            contents = self.git_repo.get_contents(file_name, ref=self.git_branch)
            return contents.decoded_content.decode("utf-8")
        except UnknownObjectException as e:
            raise GitFileNotExistError("File not found") from e
        except GithubException as e:
            raise GitClientException(str(e)) from e

    def update_or_create_file(
        self, git_file_path: str, commit_message: str, file_content: Any
    ) -> dict:

        self.call_asserts(self.git_branch, self.git_repo)
        try:
            contents = self.git_repo.get_contents(git_file_path, ref=self.git_branch)
            response = self.git_repo.update_file(
                path=contents.path,
                message=commit_message,
                content=file_content,
                sha=contents.sha,
                branch=self.git_branch,
            )
            return {"created": False, "updated": True, "content": response}
        except GithubException as e:
            if "Not Found" in str(e):
                response = self.git_repo.create_file(
                    git_file_path, commit_message, file_content, branch=self.git_branch
                )

                return {"created": True, "updated": False, "content": response}
            else:
                raise GitClientException(str(e)) from e

    def update_or_create_multiple_files(
        self, git_files: dict, commit_message: str
    ) -> None:

        self.call_asserts(self.git_branch, self.git_repo)

        last_commit_sha = self.git_repo.get_branch(self.git_branch).commit.sha
        base_tree = self.git_repo.get_git_tree(sha=last_commit_sha)

        commit_changes = []
        for filepath, contents in git_files.items():

            blob = self.git_repo.create_git_blob(contents, "utf-8")
            tree_element = InputGitTreeElement(
                path=filepath, mode="100644", type="blob", sha=blob.sha
            )
            commit_changes.append(tree_element)

        new_tree = self.git_repo.create_git_tree(commit_changes, base_tree)
        parent = self.git_repo.get_git_commit(sha=last_commit_sha)
        new_commit = self.git_repo.create_git_commit(commit_message, new_tree, [parent])
        logger.debug(
            f"Updating references heads/{self.git_branch} to the new commit {new_commit.sha}."
        )
        branch_refs = self.git_repo.get_git_ref(f"heads/{self.git_branch}")
        branch_refs.edit(sha=new_commit.sha)

    def delete_file(self, git_file_path: str, commit_message: str) -> None:

        self.call_asserts(self.git_branch, self.git_repo)

        try:
            contents = self.git_repo.get_contents(git_file_path, ref=self.git_branch)
            self.git_repo.delete_file(
                contents.path, commit_message, contents.sha, branch=self.git_branch
            )
        except GithubException as e:
            raise GitClientException(str(e)) from e
