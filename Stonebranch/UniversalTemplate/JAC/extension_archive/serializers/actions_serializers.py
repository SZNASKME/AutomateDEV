from typing import Optional, Union

from pydantic import BaseModel, validator

from enums.enums import ProxyTypeEnum


class ActionSerializer(BaseModel):
    pass


class ActionOutputSerializer(BaseModel):
    definitions_selected: dict


class ListUacActionInputSerializer(ActionSerializer):
    credentials_username: str
    credentials_password: Optional[str]
    credentials_token: Optional[str]
    uc_url: str
    selection_method: str
    selection_name: Optional[str]
    selection_exclude_list: Optional[list]
    uc_verify: Optional[Union[str, bool]]


class ListUacActionOutputSerializer(ActionOutputSerializer):
    errors: Optional[list]

    @validator("errors")
    def convert_null_to_empty_list(cls, errors: list) -> list:
        if errors is None:
            return []

        return errors


class ExportToGitRepositoryInputSerializer(ListUacActionInputSerializer):
    git_service_provider: str
    git_service_provider_url: Optional[str]
    git_access_token: str
    git_user: str
    git_repository: str
    git_repository_branch: str
    git_repository_path: Optional[str]
    git_commit_message: Optional[str]
    git_repository_file_format: Optional[str]
    proxy_type: Optional[ProxyTypeEnum]
    proxy: Optional[str]
    proxy_ca_bundle_file: Optional[str]
    proxy_user: Optional[str]
    proxy_password: Optional[str]
    git_ssl_cert_verification: bool
    ff_commit_msg: bool

    class Config:
        use_enum_types: True


class ExportToGitRepositoryOutputSerializer(ListUacActionOutputSerializer):
    definitions_exported: dict


class ImportUacActionInputSerializer(ActionSerializer):
    git_service_provider: str
    git_service_provider_url: Optional[str]
    git_access_token: str
    git_user: str
    git_repository: str
    git_repository_branch: str
    git_repository_path: Optional[str]
    git_commit_message: Optional[str]
    git_repository_file_format: Optional[str]
    add_uc_definitions_list: Optional[Union[list, str]]
    modify_uc_definitions_list: Optional[Union[list, str]]
    remove_uc_definitions_list: Optional[Union[list, str]]
    proxy_type: Optional[ProxyTypeEnum]
    proxy: Optional[str]
    proxy_ca_bundle_file: Optional[str]
    proxy_user: Optional[str]
    proxy_password: Optional[str]
    git_ssl_cert_verification: bool
    webhook_payload: Optional[dict]

    @validator("git_repository_path")
    def construct_git_repo_path(cls, value) -> str:
        return f"{value}/" if value else ""


class ImportUacActionOutputSerializer(ActionOutputSerializer):
    definitions_added: dict
    definitions_modified: dict
    definitions_removed: dict
    errors: Optional[list]
