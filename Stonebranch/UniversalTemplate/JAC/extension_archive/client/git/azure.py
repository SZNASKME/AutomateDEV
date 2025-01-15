import base64
import json
import math

import requests

from client.git.base import GitClient
from client.git.exceptions import GitBranchNotExistException, GitRepoNotExistException
from logger import logger

from .resources import azure_endpoints as AZURE_ENDPOINT


class AzureDevOpsGitClient(GitClient):
    """
    Implementation of GitClient for Azure DevOps Repositories
    """

    API_VERSION = "api-version=7.1"

    @property
    def git_branch(self):
        return self._git_branch

    @git_branch.setter
    def git_branch(self, git_branch: str) -> None:
        self._git_branch = git_branch

    def _init_client(self) -> None:
        pass

    def _init_proxy_session(self):
        super()._init_proxy_session()

        authorization = str(
            base64.b64encode(bytes(":" + self.git_token, "ascii")), "ascii"
        )
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Basic " + authorization,
        }

        self.session.headers.update(self.headers)

    def _send_request(self, method, endpoint, params=None, data=None):

        version = (
            f"?{self.API_VERSION}" if "?" not in endpoint else f"&{self.API_VERSION}"
        )

        url = f"{endpoint}{version}"
        logger.debug(f"Sending requests to {url}")
        response = self.session.request(method, url, params=params, json=data)
        logger.debug(
            f"Response retrieved:  Status code {response.status_code}. Text: {response.text}."
        )
        response.raise_for_status()
        return response.json()

    def get_repos_list(self):
        endpoint = AZURE_ENDPOINT.REPOS.format(base_url=self.git_url)
        response = self._send_request("GET", endpoint)
        return [repo["name"] for repo in response.get("value", [])]

    def get_repo_branches(self, repo_path):
        endpoint = AZURE_ENDPOINT.REF_HEADS.format(
            base_url=self.git_url, repo=self.git_repo
        )
        try:
            response = self._send_request("GET", endpoint)
        except requests.HTTPError as e:
            raise GitRepoNotExistException(
                f"Repository not found: {repo_path}. Cannot retrieve branches."
            ) from e
        return [
            branch["name"].split("refs/heads/")[1]
            for branch in response.get("value", [])
        ]

    def get_branch_files(self, branch_name, path) -> list:
        endpoint = AZURE_ENDPOINT.BRANCH_FILES.format(
            base_url=self.git_url, repo=self.git_repo, branch=branch_name, filepath=path
        )

        response = self._send_request("GET", endpoint)
        files = []
        for item in response.get("value", []):
            if item.get("gitObjectType", "") == "blob":
                file_name = item["path"]
                folder_name = file_name.rsplit("/", 1)[0]
                if folder_name not in files:
                    files.append(file_name)
        return files

    def filepath_exists(self, filepath):
        endpoint = AZURE_ENDPOINT.ITEM.format(
            base_url=self.git_url,
            repo=self._git_repo,
            filepath=filepath,
            branch=self.git_branch,
        )
        try:
            self._send_request("GET", endpoint)
            return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == requests.codes.not_found:
                return False
            return False

    def get_file_contents(self, file_name):
        return self._get_file_info(file_name).get("content")

    def update_or_create_file(self, git_file_path, commit_message, file_content):
        try:
            file_info = self._get_file_info(git_file_path)
            commit_id = file_info.get("commitId")
            created = False
        except requests.exceptions.HTTPError:
            commit_id = self.get_branch_last_commit()
            created = True

        commit_changes = [
            {
                "changeType": "add",  # Default to "add"
                "item": {"path": git_file_path},
                "newContent": {
                    "content": file_content,
                    "contentType": "rawtext",
                },
            }
        ]

        if not created:
            # The file exists, update it
            commit_changes[0]["changeType"] = "edit"

        self._push_changes(commit_message, commit_id, commit_changes)
        content = self.get_file_contents(git_file_path)

        return {
            "created": True if created else False,
            "updated": False if created else True,
            "content": content,
        }

    def update_or_create_multiple_files(
        self, git_files: dict, commit_message: str
    ) -> None:

        self.call_asserts(self.git_branch, self.git_repo)
        commit_actions = {}
        for file, contents in git_files.items():
            try:
                self._get_file_info(file)
                commit_actions[file] = ("edit", contents)
            except requests.exceptions.HTTPError:
                commit_actions[file] = ("add", contents)

        for idx, changes in enumerate(self._iter_changes(commit_actions)):
            commit_id = self.get_branch_last_commit()
            message = commit_message if idx == 0 else f"{commit_message} (part {idx})"
            logger.debug(f"Pushing commit part {idx}")
            self._push_changes(message, commit_id, changes)

    def _iter_changes(self, commit_actions: dict):
        REQUEST_MAX_SIZE: int = 26214400  # 25Mi
        # play it safe by not utilizing the entire available space for the
        # payload to account for encoding and json serialization quirks in the
        # bellow implementation, 3/4 may be too conservative, could use 9/10
        max_size_offset: int = math.ceil(REQUEST_MAX_SIZE * 0.25)
        payload_max_size: int = REQUEST_MAX_SIZE - max_size_offset

        current_size = 0
        changes = []

        for file, commit_details in commit_actions.items():
            change = {
                "changeType": commit_details[0],
                "item": {"path": file},
                "newContent": {
                    "content": commit_details[1],
                    "contentType": "rawtext",
                },
            }

            change_size = len(json.dumps(change))

            if change_size > payload_max_size:
                raise RuntimeError(
                    f"Payload data ({change_size}) exceeds maximum request size (payload_max_size)"
                )

            if (current_size + change_size) > payload_max_size:
                logger.debug(
                    f"Payload data exceeds maximum size. Yielding {len(changes)} changes"
                )
                yield changes

                current_size = 0
                changes.clear()

            changes.append(change)
            current_size += change_size

        if changes:
            logger.debug(f"Yielding {len(changes)} changes")
            yield changes

    def delete_file(self, git_file_path, commit_message):
        file_info = self._get_file_info(git_file_path)
        commit_id = file_info.get("commitId")
        commit_changes = [
            {
                "changeType": "delete",  # Default to "add"
                "item": {"path": git_file_path},
            }
        ]
        self._push_changes(commit_message, commit_id, commit_changes)

    def git_branch_exists(self, branch_name: str, repository: str):
        branches = self.get_repo_branches(repo_path=repository)
        found = any(branch_name in string for string in branches)
        if not found:
            raise GitBranchNotExistException(
                f"Git branch {branch_name} not found in repository {repository}."
            )

    def _get_file_info(self, git_file_path: str):
        endpoint = AZURE_ENDPOINT.ITEM_CONTENT.format(
            base_url=self.git_url,
            repo=self.git_repo,
            filepath=git_file_path,
            branch=self.git_branch,
        )
        return self._send_request("GET", endpoint)

    def get_commit_changes(self, commit_id: str, repository_id: str):
        """
        Get changes from a specific commit id

        Args:
            commit_id: The commit id to extract the changes
            repository_id: The repository_id to extract the changes
        """
        endpoint = AZURE_ENDPOINT.COMMIT.format(
            base_url=self.git_url, repo=repository_id, id=commit_id
        )
        return self._send_request("GET", endpoint)

    def get_branch_last_commit(self) -> str:
        """Get the last commit from ref branch."

        Returns:
            The commit ID
        """
        endpoint = AZURE_ENDPOINT.REF_HEADS.format(
            base_url=self.git_url, repo=self.git_repo
        )
        response = self._send_request("GET", endpoint)
        branch = [
            branch
            for branch in response.get("value")
            if self.git_branch in branch.get("name")
        ]
        commit_id = branch[0].get("objectId")
        return commit_id

    def _push_changes(self, commit_message: str, commit_id: str, changes: list):
        """Push changes on the remote branch.

        Args:
            commit_message: Message to use for the commit.
            commit_id: The last commit id of the item to update.
                For single fle commit, is the last commit of the file.
                For multiple files commit, is the last commit of the branch.
            changes: A structured list of dictionaries, for the items that will be included in the commit.
                Example for addition:
                    {
                        "changeType": "add"
                        "item": {"path": "some/path/filename.txt"},
                        "newContent": {
                            "content": "My file contents",
                            "contentType": "rawtext",
                    }
        """
        data = {
            "refUpdates": [
                {"name": f"refs/heads/{self.git_branch}", "oldObjectId": commit_id}
            ],
            "commits": [{"comment": f"{commit_message}", "changes": changes}],
        }

        endpoint = AZURE_ENDPOINT.PUSH.format(base_url=self.git_url, repo=self.git_repo)
        self._send_request("POST", endpoint, data=data)
