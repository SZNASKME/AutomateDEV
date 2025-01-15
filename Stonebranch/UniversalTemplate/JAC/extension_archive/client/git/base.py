from abc import ABC, abstractmethod
from typing import Any, Optional

import certifi
from requests import Session

from client.git.exceptions import GitBranchNotExistException
from enums.enums import ProxyTypeEnum
from logger import logger

BRANCH_NOT_SET = "git_branch is not set"
REPO_NOT_SET = "git_repo is not set"


class GitClient(ABC):  # pragma: no cover
    """
    Interface for Git clients
    """

    git_repo_path = None
    git_branch = None

    def __init__(
        self,
        git_token: str,
        git_url: str = None,
        git_repo: str = None,
        git_branch: str = None,
        proxy_url: str = None,
        proxy_type: str = None,
        proxy_ca_file: str = None,
        proxy_user: str = None,
        proxy_password: str = None,
        verify: bool = True,
    ):
        logger.debug(f"Certificates will be obtained from {certifi.where()}")
        self.git_token = git_token
        self.git_url = git_url
        self._git_repo = git_repo
        self._git_branch = git_branch
        self.proxy_url = proxy_url
        self.proxy_type = proxy_type
        self.proxy_ca_file = proxy_ca_file
        self.proxy_user = proxy_user
        self.proxy_password = proxy_password
        self.verify = verify if not proxy_ca_file else proxy_ca_file
        self._init_proxy_session()
        self._init_client()
        self._set_git_attributes(git_repo, git_branch)

    def _init_proxy_session(self):
        """
        Set the proxy in session of the request depending on the input of the user.

        """
        self.session = Session()
        if self.proxy_type == ProxyTypeEnum.HTTP.value:
            http_proxy = {"https": f"{self.proxy_url}"}
            self.session.proxies = http_proxy
        elif self.proxy_type == ProxyTypeEnum.HTTPS.value:
            https_proxy = {"https": f"{self.proxy_url}"}
            self.session.proxies = https_proxy
            self.session.verify = self.proxy_ca_file
        elif self.proxy_type == ProxyTypeEnum.HTTPS_CREDENTIALS:
            scheme, url = self.proxy_url.split("://")
            https_proxy = {
                "https": f"{scheme}://{self.proxy_user}:{self.proxy_password}@{url}"
            }
            self.session.proxies = https_proxy
            self.session.verify = self.proxy_ca_file

    def _set_git_attributes(self, git_repo, git_branch):
        """
        Set git attributes such as repo and branch
        """
        if git_repo:
            self.git_repo = git_repo
        if git_branch:
            self.git_branch_exists(self.git_branch, git_repo)
            self.git_branch = git_branch

    @abstractmethod
    def _init_client(self):
        """
        Instantiate a client to perform api requests
        """
        pass

    @abstractmethod
    def get_repos_list(self) -> Optional[list]:
        """
        Return a list of all available repositories
        """
        pass

    @abstractmethod
    def get_repo_branches(self, repo_path: str) -> Optional[list]:
        """
        Return a list of all available branches of a git repository
        """
        pass

    @abstractmethod
    def get_branch_files(self, branch_name: str, path: str) -> Optional[list]:
        """
        Return a list of all files in a specific branch, including files in sub-folders.

        :param str branch_name: The branch name which files will be retrieved
        """
        pass

    @abstractmethod
    def filepath_exists(self, filepath: str) -> bool:
        """_Checks recursively to find the given filepath in a specified repository and branch_

        :param str filepath: _The filepath to look for inside the repository_
        :return bool: _True, False_
        """
        pass

    @abstractmethod
    def get_file_contents(self, file_name: str) -> Optional[str]:
        """
        Return the contents of a git repository
        """
        pass

    @abstractmethod
    def update_or_create_file(
        self, git_file_path: str, commit_message: str, file_content: Any
    ) -> dict:
        """
        Create a file in git. If the file already exist, update the file instead.

        :param str git_file_path: The content path
        :param str commit_message: The commit message
        :param Any file_content: The updated file content, either base64 encoded, or ready to be encoded.
        :return dict: _description_
        """
        pass

    @abstractmethod
    def update_or_create_multiple_files(
        self, git_files: dict, commit_message: str
    ) -> None:
        """Update or create git files in batch mode, with a single commit.

        Args:
            git_files: dictionary with pairs of { filepath : contents }. Contents should get be encoded bytes.
            git_commit_message: the message to use for the commit
        """
        pass

    @abstractmethod
    def delete_file(
        self,
        git_file_path: str,
        commit_message: str,
    ) -> None:
        """
        Delete a file in git.

        :param str git_file_path: The content path
        :param str commit_message: The commit message
        :return dict: _description_
        """
        pass

    def call_asserts(self, git_branch, git_repo):
        assert git_branch is not None, BRANCH_NOT_SET
        assert git_repo is not None, REPO_NOT_SET

    def git_branch_exists(self, branch_name: str, repository: str):
        branches = self.get_repo_branches(repo_path=repository)
        if branch_name not in branches:
            raise GitBranchNotExistException(
                f"Git branch {branch_name} not found in repository {repository}."
            )
