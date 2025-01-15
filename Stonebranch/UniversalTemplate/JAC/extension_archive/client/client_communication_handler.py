from typing import Any

from actions.utils import extract_folder_subfolder_from_uc_resource
from client.git import AzureDevOpsGitClient, BitbucketClient, GitLabClient
from client.uc.resources import UCResource
from client.uc.uc_client import UCClient
from client.uc.utils.utils import initialize_uc_objects
from enums.enums import GitServiceProviderEnum
from logger import logger
from serializers import ExtensionInputSerializer


class GitClientFactory:
    @staticmethod
    def create_git_client(service_provider, input_data):
        if service_provider == GitServiceProviderEnum.GITLAB.value:
            return GitLabClient(**input_data)
        elif service_provider == GitServiceProviderEnum.BITBUCKET.value:
            return BitbucketClient(**input_data)
        elif service_provider == GitServiceProviderEnum.AZURE.value:
            return AzureDevOpsGitClient(**input_data)
        else:
            from client.git.github import GitHubClient

            return GitHubClient(**input_data)


class ClientCommunicationHandler:
    def __init__(self, convert_input: ExtensionInputSerializer):
        self.git_client = None
        self.uc_client = None
        self.input = convert_input

        self.git_repo_path = (
            f"{convert_input.git_repository_path}/"
            if hasattr(convert_input, "git_repository_path")
            and convert_input.git_repository_path is not None
            else ""
        )
        if (
            (
                hasattr(self.input, "uc_ssl_cert_verification")
                and self.input.uc_ssl_cert_verification == False
            )
            or hasattr(self.input, "git_ssl_cert_verification")
            and self.input.git_ssl_cert_verification == False
        ):
            logger.warning(
                "InsecureRequestWarning: Unverified HTTPS request will be made. Adding certificate verification is strongly advised."
            )

    def set_git_client(self):
        """_Set GitClient object for internal use.
        GitLab or GitHub client will be initialized based on the input field `service_provider`_
        """
        service_provider = self.input.git_service_provider
        input_data = {
            "git_url": self.input.git_service_provider_url,
            "git_token": self.input.git_access_token,
            "git_repo": self.input.git_repository,
            "git_branch": self.input.git_repository_branch,
            "proxy_url": self.input.proxy,
            "proxy_type": self.input.proxy_type,
            "proxy_ca_file": self.input.proxy_ca_bundle_file,
            "proxy_user": self.input.proxy_user,
            "proxy_password": self.input.proxy_password,
            "verify": self.input.git_ssl_cert_verification,
        }

        self.git_client = GitClientFactory.create_git_client(
            service_provider, input_data
        )

    def set_uc_client(self):
        """_Set UCClient object for internal use._"""
        self.uc_client = UCClient(
            url=self.input.uc_url,
            user=self.input.credentials_username,
            password=self.input.credentials_password,
            token=self.input.credentials_token,
            verify=self.input.uc_ssl_cert_verification,
        )

    def get_git_client(self):  # pragma: no cover
        """_Return a Git Client_

        :return _GitClient_: _The internal Git Client_
        """
        return self.git_client

    def get_uc_client(self):  # pragma: no cover
        """_Return a UC Client_

        :return _UCClient_: _The internal UC Client_
        """
        return self.uc_client

    def get_git_path(self, uc_object: UCResource) -> str:
        """_Calculates and returns the absolute filepath, where the given UC definition will be stored on Git._

        :param UCResource uc_object: _The UC object_
        :return str: _The absolute file path on Git._
        """
        filename = f"{uc_object.name}.{self.input.git_repository_file_format.lower()}"

        folder_name, subfolder_name = extract_folder_subfolder_from_uc_resource(
            uc_object
        )

        if subfolder_name:
            git_file_path = (
                f"{self.git_repo_path}{folder_name}/{subfolder_name}/{filename}"
            )
        else:
            git_file_path = f"{self.git_repo_path}{folder_name}/{filename}"

        return git_file_path

    def add_file_to_git(self, git_absolute_filepath: str, uc_contents: str) -> dict:
        """_Upload the contents of UC Object, on Git._

        :param str git_absolute_filepath: _The filepath to store the given UC object_
        :param str uc_object: _The UC contents to upload_
        """

        self.git_client.update_or_create_file(
            git_file_path=git_absolute_filepath,
            file_content=uc_contents,
            commit_message=self.input.git_commit_message,
        )

    def batch_add_files_to_git(self, files: dict) -> None:
        """_Upload the contents of UC Object, on Git._

        :param str git_absolute_filepath: _The filepath to store the given UC object_
        :param str uc_object: _The UC contents to upload_
        """

        self.git_client.update_or_create_multiple_files(
            git_files=files,
            commit_message=self.input.git_commit_message,
        )

    def get_uc_definitions(
        self, uc_definitions_types: list = None, name: str = None
    ) -> list:
        """
        Get the whole definition of a UC Object

        :param list types_to_include: The type of UC definitions to be fetched
        """
        return self.uc_client.get_definitions(types=uc_definitions_types, name=name)

    def add_uc_definitions(self, uc_definitions: list) -> None:
        """_Create definition on Controller_

        :param list uc_definitions: _The list of UC Objects_
        """
        return self.uc_client.create_definitions(uc_definitions, ignore_errors=True)

    def modify_uc_definitions(self, uc_definitions: list) -> Any:
        """_Update definition on Controller_

        :param list uc_definitions: _The list of UC Objects_
        """
        return self.uc_client.update_definitions(uc_definitions, ignore_errors=True)

    def remove_uc_definitions(self, uc_definitions: list) -> Any:
        """_Delete definition from Controller_

        :param list uc_definitions: _The list of UC Objects_
        """
        return self.uc_client.delete_definitions(uc_definitions, ignore_errors=True)

    @staticmethod
    def initialize_uc_resource(
        uc_type_class: UCResource, git_file_contents: dict
    ) -> UCResource:
        """_Initializes a UC object, with the given git contents._

        :param UCResource uc_type_class: _Returns the given_
        :param dict git_file_contents: _the UC definitions as stored on git_
        :return UCResource: _The instantiated UC object_
        """
        return initialize_uc_objects(
            [git_file_contents], uc_type_class.get_class_name()
        )[0]
