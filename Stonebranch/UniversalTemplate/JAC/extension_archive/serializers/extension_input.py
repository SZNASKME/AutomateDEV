import json
import os
from json import JSONDecodeError
from typing import Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, Field, root_validator, validator
from universal_extension import logger

from client.uc.enums.enums import UcTypes
from enums import (
    ActionsEnum,
    FeatureFlags,
    GitFileFormat,
    GitServiceProviderEnum,
    ProxyTypeEnum,
    SelectionMethodEnum,
)


class UaCDynamicChoiceSerializer(BaseModel):
    action: ActionsEnum
    credentials_username: str = Field(alias="uc_credentials.user")
    credentials_password: str = Field(None, alias="uc_credentials.password")
    credentials_token: str = Field(None, alias="uc_credentials.token")
    uc_url: AnyHttpUrl
    selection_method: SelectionMethodEnum
    uc_ssl_cert_verification: bool

    @validator(
        "action",
        "selection_method",
        pre=True,
    )
    def retrieve_value_from_list(cls, value: list) -> Optional[str]:
        return value[0] if value and value[0] else None

    @validator("uc_url")
    def validate_uc_url(cls, uc_url: str) -> str:
        return uc_url.rstrip("/")

    class Config:
        use_enum_values = True


class GitDynamicChoiceSerializer(BaseModel):
    git_service_provider: GitServiceProviderEnum
    git_service_provider_url: Union[AnyHttpUrl, str]
    git_access_token: str = Field(None, alias="git_credentials.token")
    git_user: str = Field(None, alias="git_credentials.user")
    git_repository: Optional[Union[list, str]]
    git_repository_branch: Optional[Union[list, str]]
    proxy_type: Optional[ProxyTypeEnum]
    proxy: Optional[Union[AnyHttpUrl, str]]
    proxy_ca_bundle_file: Optional[str]
    proxy_user: str = Field(None, alias="proxy_credentials.user")
    proxy_password: str = Field(None, alias="proxy_credentials.password")
    git_ssl_cert_verification: bool = True

    @validator(
        "git_repository",
        "git_repository_branch",
        "git_service_provider",
        "proxy_type",
        pre=True,
    )
    def retrieve_value_from_list(cls, value: list) -> Optional[str]:
        return value[0] if value and value[0] else None

    @validator("git_service_provider_url", pre=True)
    def validate_git_service_provider_url(cls, value: AnyHttpUrl, values: dict) -> str:
        return replace_git_url(value, values["git_service_provider"])


class ExtensionInputSerializer(BaseModel):
    action: ActionsEnum
    credentials_username: str = Field(alias="uc_credentials.user")
    credentials_password: str = Field(None, alias="uc_credentials.password")
    credentials_token: Optional[str] = Field(None, alias="uc_credentials.token")
    uc_url: Optional[AnyHttpUrl]
    selection_method: Optional[SelectionMethodEnum]
    selection_name: Optional[str]
    selection_exclude_list: Optional[list]
    git_service_provider: Optional[GitServiceProviderEnum]
    git_service_provider_url: Optional[Union[AnyHttpUrl, str]]
    git_access_token: str = Field(None, alias="git_credentials.token")
    git_user: str = Field(None, alias="git_credentials.user")
    git_repository: Optional[Union[list, str]]
    git_repository_branch: Optional[Union[list, str]]
    git_repository_path: Optional[str]
    git_repository_file_format: Optional[Union[GitFileFormat, str]]
    git_commit_message: Optional[str]
    proxy_type: Optional[ProxyTypeEnum]
    proxy: Optional[Union[AnyHttpUrl, str]]
    proxy_ca_bundle_file: Optional[str]
    proxy_user: str = Field(None, alias="proxy_credentials.user")
    proxy_password: str = Field(None, alias="proxy_credentials.password")
    add_uc_definitions_list: Optional[Union[list, str]]
    modify_uc_definitions_list: Optional[Union[list, str]]
    remove_uc_definitions_list: Optional[Union[list, str]]
    uc_ssl_cert_verification: bool = True
    git_ssl_cert_verification: bool = True
    webhook_payload: Optional[Union[str, dict]]
    ff_commit_msg: Union[Optional[str], bool] = None

    class Config:
        use_enum_values = True

    @root_validator
    def return_value_or_none(cls, values) -> dict:
        return replace_empty_string_with_none(values)

    @validator("uc_url")
    def validate_uc_url(cls, uc_url: str) -> str:
        return uc_url.rstrip("/")

    @validator(
        "action",
        "selection_name",
        "selection_method",
        "git_repository",
        "git_repository_branch",
        "git_service_provider",
        "git_repository_file_format",
        "proxy_type",
        pre=True,
    )
    def retrieve_value_from_list(cls, value: list) -> Optional[str]:
        return value[0] if value and value[0] else None

    @validator("selection_name", pre=True)
    def mandatory_selection_name(cls, value, values) -> str:
        if (
            values.get("action")
            in [ActionsEnum.LIST_UAC_DEFINITIONS.value, ActionsEnum.EXPORT_GIT.value]
            and not value
        ):
            raise ValueError("Field `Selection Name` should be populated.")
        return value

    @validator("git_service_provider_url", pre=True)
    def validate_git_service_provider_url(
        cls, value: Optional[AnyHttpUrl], values: dict
    ) -> Optional[str]:
        if value:
            return replace_git_url(value, values["git_service_provider"])

    @validator("git_repository_path")
    def validate_git_repo_path(cls, git_file_path: str) -> Optional[str]:
        """
        Remove unnecessary slashes (/) from git file path. Also if the file path is equal to a git resource
        definition name it raises an input validation error.

        :param str git_file_path: The git file path as provided as an input from the user.
        """
        if not git_file_path:
            return

        uc_types = [uc_type.value for uc_type in UcTypes]
        sanitized_path = git_file_path.strip().strip("/")
        if sanitized_path in uc_types:
            raise ValueError(
                "Git file path cannot be equal to the name of a UC Resource type."
            )

        return git_file_path

    @validator("git_repository_file_format")
    def file_format_to_lower_case(cls, value: Optional[str]) -> Optional[str]:
        if value:
            return value.lower()
        return value

    @validator(
        "add_uc_definitions_list",
        "modify_uc_definitions_list",
        "remove_uc_definitions_list",
        pre=True,
    )
    def convert_str_to_list(
        cls, value: Optional[str], field
    ) -> Optional[Union[str, list]]:
        if (
            str(field.name) in ["add_uc_definitions_list", "modify_uc_definitions_list"]
            and value.strip() == "*"
        ):
            return value

        if not value:
            return

        if cls.is_comma_separated_json_yaml_strings(value) is False:
            raise ValueError(
                "The provided git file paths should end with .json or .yaml and be comma-separated."
            )

        split_def_list = [definition.strip() for definition in value.split(",")]
        return list(set(split_def_list))

    @validator("git_commit_message")
    def validate_git_commit_message(cls, commit_message, values) -> Optional[str]:
        if values["action"] == ActionsEnum.EXPORT_GIT and not commit_message:
            raise ValueError(
                "Git Commit Message is required for action 'Export to Git Repository'"
            )
        return commit_message

    @validator("webhook_payload")
    def validate_bitbucket_webhook(cls, webhook_payload, values) -> Optional[dict]:
        if webhook_payload:
            if values["git_service_provider"] not in [
                GitServiceProviderEnum.BITBUCKET.value,
                GitServiceProviderEnum.AZURE.value,
            ]:
                logger.warning(
                    "Webhook Payload should only be used for BitBucket Git Service Provider. Payload will be ignored."
                )
                return

            try:
                webhook_payload = json.loads(webhook_payload)
                return webhook_payload
            except JSONDecodeError as e:
                raise ValueError("'Webhook Payload' is not a valid JSON string.") from e

    @validator("ff_commit_msg", always=True)
    def validate_ff_disable_default_commit(cls, value: Optional[str]) -> bool:
        ff_value = os.getenv(FeatureFlags.FF_DISABLE_COMMIT_PREFIX.value)
        if not ff_value:
            return False
        try:
            mapper = {"True": True, "true": True, "False": False, "false": False}
            return mapper[ff_value]
        except KeyError as exc:
            raise ValueError(
                f"Invalid value for feature flag '{FeatureFlags.FF_DISABLE_COMMIT_PREFIX.value}': '{value}'."
            ) from exc

    @staticmethod
    def is_comma_separated_json_yaml_strings(input_string: True) -> bool:
        """
        Check if a string is comma separated.
        * The input_string is first split into substrings using the , character as the separator, and these substrings are stored in the substrings variable.
        * Then, a loop is run over each substring in substrings.
        * For each substring, any leading or trailing whitespace is stripped off using the strip() method,
        and the resulting string is stored in the stripped_substring variable.
        * The method then checks whether the stripped_substring ends with either .json or .yaml, and returns False if it does not.
        * It then checks whether the stripped_substring contains more than one occurrence of either .json or .yaml, and again returns False if it does.
        * If both these checks pass for all substrings, the method returns True.

        :param str input_string: the string to be checked.
        :return bool: The result of the evaluation.
        """
        substrings = input_string.split(",")
        for substring in substrings:
            stripped_substring = substring.strip()
            if not (
                stripped_substring.endswith(".json")
                or stripped_substring.endswith(".yaml")
            ):
                return False
            if (
                stripped_substring.count(".json") + stripped_substring.count(".yaml")
                > 1
            ):
                return False
        return True


def replace_git_url(git_url: str, git_service_provider: str) -> str:
    """_Validate if the provided Git URL is consistent with the Service Provider
    that has been selected.
    For GitHub specifically, we need to append the `api` in the base github domain,
    so the GitHub API can be called properly._

    :param AnyHttpUrl value: _The git_service_provider_url to be validated_
    :param dict values: _The input fields_
    :raises ValueError: _Raises Value error when URL is not aligned with
    the Service Provider_
    :return AnyHttpUrl: _The validated and/or reformatted URL_
    """
    if git_service_provider == GitServiceProviderEnum.GITHUB.value:
        github_api_version = "/api/v3"
        # Cloud edition Free
        if "github.com" in git_url:
            git_url = git_url.replace("https://", "https://api.").rstrip("/")
            return git_url

        # Cloud edition Pro
        if "github" in git_url and not git_url.endswith(github_api_version):
            git_url = git_url.rstrip("/") + github_api_version

        # Enterprise edition
        elif git_url.endswith(github_api_version):
            # Do nothing, the URL is already in the desired format
            pass

    if git_service_provider == GitServiceProviderEnum.BITBUCKET.value:
        git_url = git_url.rstrip("/")
        if "https://bitbucket.org" in git_url:
            git_url = git_url.replace("https://", "https://api.")
        else:
            logger.warning(
                "Git Service Provider URL is not matching the expected one for Bit Bucket Cloud. Using default base URL https://bitbucket.org."
            )
            git_url = "https://api.bitbucket.org"
    return git_url


def replace_empty_string_with_none(values: dict) -> dict:
    """_Return None for fields with empty string._

    :param dict values: _The input fields dictionary_
    """
    for key, value in values.items():
        if value == "":
            values[key] = None
        return values
