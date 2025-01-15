from typing import Any, Dict, List, Optional

from gitlab import Gitlab
from gitlab.exceptions import GitlabAuthenticationError, GitlabError, GitlabGetError

from client.git.base import GitClient
from client.git.exceptions import (
    GitAuthException,
    GitClientException,
    GitFileNotExistError,
    GitRepoNotExistException,
)
from logger import logger

NOT_FOUND = "Not Found"


def flatten(list_of_lists: list) -> list:
    """_Helper function to flatten list that comprise of multiple levels nested lists_

    :param list list_of_lists: _description_
    :return list: _description_
    """
    if len(list_of_lists) == 0:
        return list_of_lists
    if isinstance(list_of_lists[0], list):
        return flatten(list_of_lists[0]) + flatten(list_of_lists[1:])
    return list_of_lists[:1] + flatten(list_of_lists[1:])


class GitLabClient(GitClient):  # pragma: no cover
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
            self._git_repo = self.client.projects.get(repo_path)
        except GitlabGetError as err:
            raise GitRepoNotExistException(
                f"Repository not found: {repo_path}"
            ) from err

    def _init_client(self):
        try:
            if self.git_url:
                logger.debug("Establishing connection with GitLab...")
                logger.debug(
                    f"Verify certification: {self.verify}. Git url: {self.git_url}"
                )
                self.client = Gitlab(
                    url=self.git_url,
                    private_token=self.git_token,
                    ssl_verify=self.verify,
                    keep_base_url=True,
                    session=self.session,
                )
            else:
                self.client = Gitlab(
                    private_token=self.git_token,
                    session=self.session,
                    verify=self.verify,
                )
            self.client.auth()
            logger.debug("Connection Established successfully")
        except GitlabAuthenticationError:
            raise GitAuthException(
                f"Failed to authenticate for {self.git_url}. Wrong git credentials."
            )

    def _set_git_attributes(self, git_repo, git_branch):
        super()._set_git_attributes(git_repo, git_branch)
        if self.git_repo and self.git_branch:
            self.git_tree = self._get_repo_tree()

    def _get_repo_tree(self) -> List[Dict[str, Any]]:
        """
        Initialize the repository tree once.
        """
        return self.git_repo.repository_tree(
            ref=self.git_branch, recursive=True, get_all=True
        )

    def get_repos_list(self) -> Optional[list]:

        repo_list = []
        try:
            repos = self.client.projects.list(membership=True, get_all=True)
            for repo in repos:
                repo_list.append(repo.path_with_namespace)
            return repo_list
        except GitlabError as err:
            raise GitClientException(str(err)) from err

    def get_repo_branches(self, repo_path: str) -> Optional[list]:
        branch_list = []
        try:
            git_repo = self.client.projects.get(repo_path)
            branches = git_repo.branches.list()
            for branch in branches:
                branch_list.append(branch.name)
            return branch_list
        except GitlabError as err:
            raise GitRepoNotExistException(
                f"Repository not found: {repo_path}. Cannot retrieve branches."
            ) from err

    def get_branch_files(self, branch_name: str, path: str = "") -> Optional[list]:
        assert self.git_repo is not None, "git_repo is not set"

        try:
            branch = self.git_repo.branches.get(branch_name)
            tree = self.git_repo.repository_tree(
                ref=branch.name, path=path, get_all=True
            )

            files = []
            self._get_branch_files_in_path(tree, files)
            return flatten(files)

        except GitlabError:
            return None

    def filepath_exists(self, filepath: str) -> bool:

        self.call_asserts(self.git_branch, self.git_repo)

        for content in self.git_tree:
            if content.get("path") == filepath:
                return True
        return False

    def get_file_contents(self, file_name: str) -> Optional[str]:

        self.call_asserts(self.git_branch, self.git_repo)

        content_id = None
        try:
            for content in self.git_tree:
                if content.get("type") != "blob":
                    continue
                if content.get("path") == file_name:
                    content_id = content.get("id")
            if not content_id:
                raise GitFileNotExistError("File does not exist")

            contents = self.git_repo.repository_raw_blob(content_id)

            return contents.decode("utf-8")
        except GitlabError as err:
            raise GitClientException(str(err)) from err

    def update_or_create_file(
        self, git_file_path: str, commit_message: str, file_content: str
    ) -> dict:

        self.call_asserts(self.git_branch, self.git_repo)

        try:  # try update first
            content = self.git_repo.files.get(
                file_path=git_file_path, ref=self.git_branch
            )
            content.content = file_content
            content.save(branch=self.git_branch, commit_message=commit_message)

            return {"created": False, "updated": True, "content": content}
        except GitlabError as e:
            if NOT_FOUND in str(e):
                create_content = {
                    "file_path": git_file_path,
                    "branch": self.git_branch,
                    "content": file_content,
                    "commit_message": commit_message,
                }
                content = self.git_repo.files.create(create_content)
                return {"created": True, "updated": False, "content": content}
            else:
                raise GitClientException(str(e)) from e

    def update_or_create_multiple_files(
        self, git_files: Dict, commit_message: str
    ) -> None:

        self.call_asserts(self.git_branch, self.git_repo)

        commit_actions = []
        project = self.client.projects.get(self.git_repo.path_with_namespace)

        for filepath, content in git_files.items():
            action = {"file_path": filepath, "content": content}
            try:
                content = self.git_repo.files.get(
                    file_path=filepath, ref=self.git_branch
                )
                action["action"] = "update"
            except GitlabError as e:
                if NOT_FOUND in str(e):
                    action["action"] = "create"

            commit_actions.append(action)

        data = {
            "branch": self.git_branch,
            "commit_message": commit_message,
            "actions": commit_actions,
        }
        project.commits.create(data)

    def delete_file(
        self,
        git_file_path: str,
        commit_message: str,
    ) -> None:

        self.call_asserts(self.git_branch, self.git_repo)

        try:
            git_file = self.git_repo.files.get(
                file_path=git_file_path, ref=self.git_branch
            )
            git_file.delete(commit_message=commit_message, branch=self.git_branch)
        except GitlabError as e:
            if NOT_FOUND in str(e):
                raise GitFileNotExistError("File does not exist") from e
            else:
                raise GitClientException(str(e)) from e

    def _get_branch_files_in_path(self, tree, files: Optional[list]):
        """
        Recursive function that search through directories and subdirectories to list all available files.
        """
        for item in tree:
            if item["type"] == "tree":
                subfolder_files = []
                sub_tree = self.git_repo.repository_tree(
                    path=item["path"], ref=self.git_branch, get_all=True
                )
                self._get_branch_files_in_path(sub_tree, subfolder_files)
                files.append(subfolder_files)
            elif item["type"] == "blob":
                files.append(item["path"])
