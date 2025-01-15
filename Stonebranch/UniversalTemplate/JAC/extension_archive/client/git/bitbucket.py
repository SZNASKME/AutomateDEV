from json import JSONDecodeError
from typing import Optional

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from universal_extension import logger

from client.git.base import GitClient
from client.git.exceptions import (
    GitAuthException,
    GitClientException,
    GitFileNotExistError,
    GitRepoNotExistException,
)
from client.git.resources import bitbucket_endpoints as BIT_BUCKET_API
from client.git.utils import (
    get_error_from_response,
    is_status_success,
    parse_json,
    raise_exception_if_not_success,
)


class BitbucketClient(GitClient):
    @property
    def git_branch(self):
        return self._git_branch

    @git_branch.setter
    def git_branch(self, git_branch: str) -> None:
        self._git_branch = git_branch

    def _init_proxy_session(self) -> None:
        super()._init_proxy_session()
        self.headers = {"Authorization": f"Bearer {self.git_token}"}
        self.session.headers.update(self.headers)

    def _init_client(self) -> None:

        if not self.git_token or self.git_token == " ":
            raise GitAuthException(
                f"Failed to authenticate for {self.git_url}. Empty token."
            )

        url = BIT_BUCKET_API.PUBLIC_REPOSITORIES.format(base_url=self.git_url)
        response = self.session.get(url)
        if not is_status_success(response.status_code):
            err = get_error_from_response(response)
            raise GitAuthException(f"Failed to authenticate for {self.git_url}. {err}")

    def get_repos_list(self) -> Optional[list]:

        repo_list = []
        url = BIT_BUCKET_API.PUBLIC_REPOSITORIES.format(base_url=self.git_url)
        response = self.session.get(url)
        if not is_status_success(response.status_code):
            err = get_error_from_response(response)
            raise GitClientException(str(err))
        repo_list = parse_json(response.json(), "$.values[*].full_name")
        logger.debug(f"Parsed repositories: {repo_list}")
        return repo_list

    def get_repo_branches(self, repo_path: str) -> Optional[list]:
        # The repo_path should be provided with full name: {workspace}/{repository}.

        branch_list = []
        url = BIT_BUCKET_API.REPO_BRANCHES.format(
            base_url=self.git_url, repo_full_name=repo_path
        )
        response = self.session.get(url)

        if not is_status_success(response.status_code):
            get_error_from_response(response)
            raise GitRepoNotExistException(
                f"Repository not found: {repo_path}. Cannot retrieve branches."
            )

        branch_list = parse_json(response.json(), '$.values[?type="branch"].name')
        return branch_list

    def get_branch_files(self, branch_name: str, path: str = "") -> Optional[list]:

        self.call_asserts(self.git_branch, self.git_repo)
        total_files = []
        self.get_all_branch_files(branch_name, self.git_repo, total_files)
        return total_files

    def filepath_exists(self, filepath: str) -> bool:

        self.call_asserts(self.git_branch, self.git_repo)

        url = BIT_BUCKET_API.LIST_BRANCH.format(
            base_url=self.git_url,
            repo_full_name=self.git_repo,
            branch=self.git_branch,
            dirpath=filepath,
        )
        response = self.session.get(url)
        return response.status_code == requests.codes.ok

    def get_file_contents(self, file_name: str) -> Optional[str]:

        self.call_asserts(self.git_branch, self.git_repo)

        url = BIT_BUCKET_API.LIST_BRANCH.format(
            base_url=self.git_url,
            repo_full_name=self.git_repo,
            branch=self.git_branch,
            dirpath=file_name,
        )
        response = self.session.get(url)

        if response.status_code == requests.codes.not_found:
            raise GitFileNotExistError(f"File {file_name} does not exist.")
        if response.status_code != requests.codes.ok:
            raise_exception_if_not_success(response)

        return response.text

    def update_or_create_file(
        self, git_file_path: str, commit_message: str, file_content: str
    ) -> dict:

        self.call_asserts(self.git_branch, self.git_repo)

        update_or_create_response = self.get_update_or_create_response(git_file_path)
        payload = {
            "message": (None, commit_message),
            "branch": self.git_branch,
            git_file_path: (file_content),
        }
        self.update_source_files(payload)
        return update_or_create_response

    def update_or_create_multiple_files(
        self, git_files: dict, commit_message: str
    ) -> None:

        self.call_asserts(self.git_branch, self.git_repo)

        payload = {
            "branch": self.git_branch,
            "message": commit_message,
        }
        git_files_encoded = {k: (v.encode("utf-8")) for k, v in git_files.items()}
        payload.update(git_files_encoded)

        # Content types needs to be set to "multipart/form-data" specifically for this call.
        # We create copies of the default session headers to send the request and assign the updated ones to self
        mutlipart_form_headers = self.headers.copy()
        session_headers = self.session.headers.copy()
        mutlipart_encoder = MultipartEncoder(fields=payload)
        mutlipart_form_headers.update({"Content-Type": mutlipart_encoder.content_type})

        self.session.headers = mutlipart_form_headers
        self.update_source_files(post_payload=mutlipart_encoder)

        # Reset session headers to default values
        self.session.headers = session_headers
        del mutlipart_form_headers
        del session_headers

    def delete_file(self, git_file_path: str, commit_message: str) -> None:

        self.call_asserts(self.git_branch, self.git_repo)

        payload = {
            "message": (None, commit_message),
            "branch": self.git_branch,
            "files": (None, git_file_path),
        }
        self.update_source_files(payload)

    def update_source_files(self, post_payload: dict) -> None:
        """Create, update or delete source files, depending on the given payload."""

        url = BIT_BUCKET_API.REPO_SOURCE.format(
            base_url=self.git_url,
            repo_full_name=self.git_repo,
        )
        response = self.session.post(url, data=post_payload)
        if response.status_code != requests.codes.created:
            raise_exception_if_not_success(response)

    def get_update_or_create_response(self, git_file_path: str) -> dict:
        """Create a dictionary used to create/update Git files.

        :param str git_file_path: The file to be created/updated
        :return dict:
        """

        self.call_asserts(self.git_branch, self.git_repo)

        content = {"file_path": git_file_path, "branch": self.git_branch}
        created = not self.filepath_exists(git_file_path)
        return {
            "created": created,
            "updated": not created,
            "content": content,
        }

    def get_all_branch_files(self, branch_name: str, path: str, total_files: list):
        branch_contents = self.list_branch(branch_name, path)
        files = parse_json(branch_contents, '$.values[?type="commit_file"].path')
        total_files.extend(files)

        directories = parse_json(
            branch_contents, '$.values[?type="commit_directory"].path'
        )
        for dir in directories:
            subfolder_files = self.get_branch_files(self.git_branch, dir)
            total_files.extend(subfolder_files)

    def list_branch(self, branch_name: str, path: str = ""):
        url = BIT_BUCKET_API.LIST_BRANCH.format(
            base_url=self.git_url,
            repo_full_name=self.git_repo,
            branch=branch_name,
            dirpath=path,
        )
        response = self.session.get(url)
        raise_exception_if_not_success(response)
        try:
            return response.json()
        except JSONDecodeError:
            raise GitClientException(
                str("Cannot parse JSON response from while listing branch contents.")
            )

    def compare_two_commits_diffstats(self, commits: str) -> dict:
        """Produces a response in JSON format with a record for every path modified,
        including information on the type of the change and the number of lines added and removed.

        :param str commits: diff commits in format <old>..<new>
        :return dict: The response
        """
        self.call_asserts(self.git_branch, self.git_repo)
        url = BIT_BUCKET_API.COMMIT_DIFFSTATS.format(
            base_url=self.git_url, repo_full_name=self.git_repo, commits=commits
        )
        response = self.session.get(url)
        raise_exception_if_not_success(response)
        try:
            return response.json()
        except JSONDecodeError as err:
            raise GitClientException(str(err)) from err
