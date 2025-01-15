import itertools
import json
from dataclasses import dataclass
from json.decoder import JSONDecodeError
from typing import Dict, List, Optional, Tuple, Union

import requests
from jsonpath_ng.ext import parse
from tabulate import tabulate

from actions.base import BaseAction, create_output_definitions
from actions.utils import extract_name_subtype_from_filepath, get_uc_type
from adaptors.adaptors import ActionAdaptors
from client.client_communication_handler import ClientCommunicationHandler
from client.git.utils import convert_yaml_to_json
from client.uc.resources import UCResource
from enums import ExcludedDefinitions, GitFileFormat, GitServiceProviderEnum
from exceptions import InvalidGitContents
from logger import logger
from serializers import (
    ExtensionInputSerializer,
    ImportUacActionInputSerializer,
    ImportUacActionOutputSerializer,
)

UAC_FILE_PREFIX = "ops_"
ALL_DEFINITIONS = "*"
ADD = "added"
MODIFY = "modified"
REMOVE = "removed"
BITBUCKET_WEBHOOK_JSONPATH = "$.push.changes[*].links.diff.href"

# Messages
INVALID_GIT_PATH_MSG = "Invalid git filepath. File will be ignored:"
INVALID_DEFINITION_MSG = "Definition type or definition name cannot be exported from filepath. File will be ignored:"
INVALID_AZURE_WEBHOOK_PAYLOAD = (
    "Azure DevOps webhook payload is invalid. Cannot extract commit changes."
)

excluded_definitions = [member.value for member in ExcludedDefinitions]
definitions_selected = create_output_definitions()
definitions_added = create_output_definitions()
definitions_modified = create_output_definitions()
definitions_removed = create_output_definitions()


class ImportUacDefinitionsAction(BaseAction):
    """
    Class responsible for executing the Import UAC Definitions action.

    """

    input_adapter = ActionAdaptors.import_uac_definitions_input_adaptor
    input_serializer = ImportUacActionInputSerializer
    output_serializer = ImportUacActionOutputSerializer
    handler = None

    def __init__(self, action_input: ExtensionInputSerializer):
        super().__init__(action_input)
        self.invalid_path_error_list = []
        self.action_input_serialized = self.get_input_data()
        self.handler = self._init_client_communication_handler(action_input)
        self._discover_files_to_import()

    def _discover_files_to_import(self):
        logger.info("Validate given filepaths.")

        if (  # pragma: no cover
            self.action_input_serialized.git_service_provider
            == GitServiceProviderEnum.BITBUCKET.value
            and self.action_input_serialized.webhook_payload
        ):
            (
                self.action_input_serialized.add_uc_definitions_list,
                self.action_input_serialized.modify_uc_definitions_list,
                self.action_input_serialized.remove_uc_definitions_list,
            ) = self.extract_files_from_bitbucket_webhook(
                self.handler, self.action_input_serialized.webhook_payload
            )

        elif (  # pragma: no cover
            self.action_input_serialized.git_service_provider
            == GitServiceProviderEnum.AZURE.value
            and self.action_input_serialized.webhook_payload
        ):
            (
                self.action_input_serialized.add_uc_definitions_list,
                self.action_input_serialized.modify_uc_definitions_list,
                self.action_input_serialized.remove_uc_definitions_list,
            ) = self.extract_files_from_azure_webhook(
                self.handler, self.action_input_serialized.webhook_payload
            )

        self.add_uc_definitions_list = (
            self.get_git_filepaths(self.action_input_serialized.add_uc_definitions_list)
            if self.action_input_serialized.add_uc_definitions_list
            else None
        )

        self.modify_uc_definitions_list = (
            self.get_git_filepaths(
                self.action_input_serialized.modify_uc_definitions_list
            )
            if self.action_input_serialized.modify_uc_definitions_list
            else None
        )

        self.remove_uc_definitions_list = (
            self.action_input_serialized.remove_uc_definitions_list
            if self.action_input_serialized.remove_uc_definitions_list
            else None
        )

    def action_cancel(self):  # pragma: no cover
        super().action_cancel()
        self.handler.uc_client.cancel_operation()

    def _init_client_communication_handler(  # pragma: no cover
        self, action_input: ExtensionInputSerializer
    ) -> ClientCommunicationHandler:
        handler = ClientCommunicationHandler(action_input)
        handler.set_uc_client()
        handler.set_git_client()
        return handler

    def execute(self) -> dict:
        """_Main executor function for the Import Action.
        Goes through all 3 UC definition lists, and performs the UC related CRUD actions._
        """
        errors = (
            [] if not self.invalid_path_error_list else [self.invalid_path_error_list]
        )
        add_result = ()
        update_result = ()
        delete_result = ()

        logger.info("Importing Git files into UAC.")

        if self.action_input_serialized.add_uc_definitions_list:
            if self.is_extension_cancelled is False:
                add_result = self.import_uac_definitions(
                    ADD, self.add_uc_definitions_list, errors
                )
        if self.action_input_serialized.modify_uc_definitions_list:
            if self.is_extension_cancelled is False:
                update_result = self.import_uac_definitions(
                    MODIFY, self.modify_uc_definitions_list, errors
                )
        if self.action_input_serialized.remove_uc_definitions_list:
            if self.is_extension_cancelled is False:
                delete_result = self.import_uac_definitions(
                    REMOVE, self.remove_uc_definitions_list, errors
                )

        unified_result = self._unify_results(
            (add_result, ADD), (update_result, MODIFY), (delete_result, REMOVE)
        )
        table_data = self.construct_result_table_data(unified_result)

        print(tabulate(table_data, headers="keys", tablefmt="rst"))

        output = {
            "definitions_selected": definitions_selected,
            "definitions_added": definitions_added,
            "definitions_modified": definitions_modified,
            "definitions_removed": definitions_removed,
            "errors": list(itertools.chain(*errors)),
        }
        return output

    def import_uac_definitions(
        self, method: str, definitions_list: Union[list, str], errors: list
    ) -> tuple:  # pragma: no cover
        uc_action_mapper = {
            ADD: self.handler.add_uc_definitions,
            MODIFY: self.handler.modify_uc_definitions,
            REMOVE: self.handler.remove_uc_definitions,
        }
        uc_action_error_prefix = {
            ADD: "Failed to add UAC definition",
            MODIFY: "Failed to modify UAC definition",
            REMOVE: "Failed to remove UAC definition",
        }
        if method == REMOVE:
            uc_definitions_selected = self.uc_definitions_from_removed_git_file_paths()
        else:
            uc_definitions_selected = self.uc_definitions_from_git_files_contents(
                self.handler,
                definitions_list,
                self.action_input_serialized.git_repository_file_format,
            )

        self.update_definitions_report(uc_definitions_selected)
        uc_action = uc_action_mapper.get(method)

        imported_definitions, add_errors = uc_action(uc_definitions_selected)
        errors.append(
            [
                f"{uc_action_error_prefix.get(method)} {key}: {value[0]}"
                for key, value in add_errors.items()
            ]
        )
        self.update_definitions_report(imported_definitions, method)

        return imported_definitions, add_errors

    def uc_definitions_from_removed_git_file_paths(self):
        """
        Construct UC definitions from files that have been deleted from Git Repository.
        Since the definition of the definition is not available,
        because the file has been deleted we construct the UC object only from the path of the file.
        """
        uc_definitions_to_be_deleted = []
        for git_file_path in self.remove_uc_definitions_list:
            # Extract the required information to construct a UC resource object
            uc_type_class = get_uc_type(git_file_path)
            definition_name, subtype = extract_name_subtype_from_filepath(git_file_path)
            if uc_type_class and definition_name:
                uc_resource = uc_type_class(name=definition_name, subtype=subtype)
                uc_definitions_to_be_deleted.append(uc_resource)
            else:
                logger.warning("%s %s.", INVALID_DEFINITION_MSG, git_file_path)

        return uc_definitions_to_be_deleted

    def get_git_filepaths(self, uc_definitions_field_input: Union[list, str]) -> list:
        """_Returns a list of constructed absolute paths, taking into account the `git_repository_path`.
        When all definitions should be provided, fetch filepaths from git.
        Otherwise, construct the absolute filepath using the definitions_list input fields._

        :param list uc_definitions_field_input: _list of git filepaths to uc definitions_
        :raises ValueError: _If the constructed filepath does not exist on Git_
        """
        git_repo_definitions = []
        absolute_filepaths = []
        git_repo_path = self.action_input_serialized.git_repository_path

        if uc_definitions_field_input == ALL_DEFINITIONS:
            absolute_filepaths = self.fetch_all_uc_files_from_git()
        else:
            git_repo_definitions = uc_definitions_field_input

            for filepath in git_repo_definitions:
                if (
                    git_repo_path
                    and filepath.startswith(git_repo_path)
                    and self.handler.git_client.filepath_exists(filepath)
                ):
                    absolute_filepaths.append(filepath)
                elif self.handler.git_client.filepath_exists(filepath):
                    absolute_filepaths.append(filepath)
                else:
                    logger.warning("%s %s.", INVALID_GIT_PATH_MSG, filepath)
                    self.invalid_path_error_list.append(
                        f"{INVALID_GIT_PATH_MSG} {filepath}."
                    )

        return absolute_filepaths

    def fetch_all_uc_files_from_git(self) -> list:
        """_Fetches all UC definition files from the provided Git repository and branch._
        :return list: _list of absolute git filepaths to uc definitions_
        """
        filepath = self.action_input_serialized.git_repository_path
        all_git_files = self.handler.git_client.get_branch_files(
            self.action_input_serialized.git_repository_branch, filepath
        )

        for file in all_git_files:
            if ".git" in file:
                all_git_files.remove(file)
            if ".md" in file:
                all_git_files.remove(file)

        return all_git_files

    @staticmethod
    def extract_files_from_bitbucket_webhook(
        handler: ClientCommunicationHandler, webhook_payload
    ) -> Tuple[List]:
        """Parse Bit Bucket webhook payload and set add/modify/remove uc definitions list."""
        diff_link_expr = parse(BITBUCKET_WEBHOOK_JSONPATH)
        diff_link = [match.value for match in diff_link_expr.find(webhook_payload)]
        if len(diff_link) == 0:
            raise ValueError(
                "Bit Bucket webhook payload is invalid. Commits diff link should exist."
            )
        diff_commits = str(diff_link[0]).split("/diff/")[1]
        all_modified_files = get_changed_files_from_bitbucket_webhook(
            handler, commit_range=diff_commits
        )
        return (
            all_modified_files.get("added"),
            all_modified_files.get("modified"),
            all_modified_files.get("removed"),
        )

    @staticmethod
    def extract_files_from_azure_webhook(
        handler: ClientCommunicationHandler, webhook_payload
    ) -> Tuple[List]:
        """
        Parse Azure DevOps webhook payload and set add/modify/remove uc definitions list.

        """

        @dataclass
        class Commit:
            """helper class"""

            commit_id: str
            repository_id: str
            changes: List[Dict]

        def extract_commits(commits: list) -> List[Commit]:
            commit_objs = []
            for commit in commits:
                commit_id = commit["newObjectId"]
                repository_id = webhook_payload["resource"]["repository"]["id"]
                # Make a GET request to the changes URL to get the actual changes for this commit
                try:
                    commit_info = handler.git_client.get_commit_changes(
                        commit_id, repository_id
                    )
                except requests.exceptions.HTTPError as err:
                    raise ValueError(
                        f"{INVALID_AZURE_WEBHOOK_PAYLOAD}. {str(err)}"
                    ) from err

                changes = commit_info["changes"]
                commit_objs.append(
                    Commit(
                        commit_id=commit_id,
                        repository_id=repository_id,
                        changes=changes,
                    )
                )
            return commit_objs

        commits = extract_commits(webhook_payload["resource"]["refUpdates"])

        for commit in commits:
            added_files = []
            updated_files = []
            removed_files = []

            for change in commit.changes:
                if change["item"]["gitObjectType"] != "blob":
                    continue
                change_type = change["changeType"]
                file_path = change["item"]["path"]

                # Check if the file was modified, added, or deleted
                if str(file_path).endswith(".yaml") or str(file_path).endswith(".json"):
                    action_list = {
                        "add": added_files,
                        "edit": updated_files,
                        "delete": removed_files,
                    }
                    action_list.get(change_type).append(file_path)

            return added_files, updated_files, removed_files

    @staticmethod
    def update_definitions_report(
        uc_definitions: list, method: Optional[str] = None
    ) -> None:
        """_Update the global counting dictionaries_

        :param list uc_definitions: _description_
        :param Optional[str] method: _description_, defaults to None
        """
        counter = {
            ADD: definitions_added,
            MODIFY: definitions_modified,
            REMOVE: definitions_removed,
            None: definitions_selected,
        }

        for uc_object in uc_definitions:
            uc_type_class = (
                "task"
                if uc_object.get_class_name() == "workflow"
                else uc_object.get_class_name()
            )
            if uc_type_class not in excluded_definitions:
                counter[method][uc_type_class] += 1

    @staticmethod
    def uc_definitions_from_git_files_contents(
        handler: ClientCommunicationHandler, git_filepaths: list, git_file_format: str
    ):
        """_Reads the contents of UC definitions from Git using the Git Client.
        And converts them to UC objects objects using the UC client._

        :param ClientCommunicationHandler handler: _The client communication handler, that performes the communication with Git and UC Client_
        :param list git_filepaths: _list of Git filepaths containing the UC definitions_
        :param str git_file_format: _the file format of the stored git files_
        :return _type_: _a list of initialized UC objects_
        """
        uc_definitions = []
        for filepath in git_filepaths:
            git_content = extract_git_file_content(handler, filepath, git_file_format)
            uc_type_class = get_uc_type(filepath)
            if not uc_type_class:
                raise ValueError(
                    f"Cannot map git filepath `{filepath}` to a valid UC type."
                )
            logger.debug(
                "UC Definition to be imported from git: %s: %s. UC type class is %s",
                filepath,
                git_content,
                uc_type_class,
            )

            uc_definition = handler.initialize_uc_resource(uc_type_class, git_content)
            uc_definitions.append(uc_definition)

        return uc_definitions

    def _unify_results(
        self,
        add: Tuple[Tuple[List, Dict], str],
        update: Tuple[Tuple[List, Dict], str],
        delete: Tuple[Tuple[List, Dict], str],
    ) -> List[Tuple[UCResource, str, Optional[str]]]:
        """
        Take the results from all operations and transform the data in a format appropriate for construct_result_table method.

        :param Tuple[Tuple[List, Dict], Tuple[List, Dict], Tuple[List, Dict]] total_result: The results (UCResource, errors) of all three operations
        :return List[Tuple[UCResource, str, Optional[str]]]: The unified result
        """
        unified_result = []
        unified_result.append(self._construct_table_rows(add))
        unified_result.append(self._construct_table_rows(update))
        unified_result.append(self._construct_table_rows(delete))

        return list(itertools.chain(*unified_result))

    def _construct_table_rows(
        self, data: Tuple[Tuple[List, Dict], str]
    ) -> List[Tuple[UCResource, str, Optional[str], str]]:
        table_row = []
        action_result = data[0]
        method = data[1]
        for item in action_result:
            if isinstance(item, list):
                for definition in item:
                    git_path = self.handler.get_git_path(definition)
                    table_row.append((definition, git_path, None, method))

            elif isinstance(item, dict):
                for key, value in item.items():
                    git_path = self.handler.get_git_path(value[1])
                    table_row.append((value[1], git_path, value[0], method))

        return table_row

    def construct_result_table_data(
        self, definitions: List[Tuple[UCResource, str, Optional[str], str]]
    ) -> List[dict]:
        """
        Create the appropriate columns for the table to be printed.
        Each element of the list is a tuple that contains the UC Resource, the git path and the error (if any).
        definition[0] = UC Resource
        definition[1] = git path
        definition[2] = error
        definition[3] = method: added/modified/removed
        :param list definitions: The list of Uc Definitions
        :return List[dict]: The table to be printed is list format
        """

        if not definitions:
            return [
                {
                    "Type": None,
                    "Subtype": None,
                    "Name": None,
                    "Git Path": None,
                    "Status": None,
                }
            ]

        data = super().construct_result_table_data([row[0] for row in definitions])

        statuses = []
        git_paths = []
        for row in definitions:
            git_path = row[1]
            error = row[2]
            method = row[-1]
            git_paths.append(git_path)

            if error:
                statuses.append("failed")
            else:
                statuses.append(method)

        extra_columns = [
            {
                "Git Path": git_paths,
                "Status": statuses,
            }
            for git_paths, statuses in zip(git_paths, statuses)
        ]

        for counter, element in enumerate(extra_columns):
            data[counter].update(element)
            counter += 1

        return data


def extract_git_file_content(
    handler: ClientCommunicationHandler, filepath: str, git_file_format: str
) -> dict:
    """_Extract the contents of a git file. Converts YAML content to Json Object._

    :param ClientCommunicationHandler handler: _The client communication handler, that performs the communication with Git and UC Client_
    :param str filepath: _The git filepath_
    :param str git_file_format: _the file format of the git file_
    :return dict: _the UC definition parsed as Json object_
    """

    file_contents = handler.git_client.get_file_contents(file_name=filepath)
    try:
        if git_file_format == GitFileFormat.YAML.value.lower():
            converted_yaml = convert_yaml_to_json(file_contents)
            json_formatted_str = json.loads(converted_yaml)
        else:
            json_formatted_str = json.loads(file_contents)
    except JSONDecodeError as err:
        raise InvalidGitContents(
            f"Git file contents `{filepath}` are not in the expected `{git_file_format}` format."
        ) from err

    return json_formatted_str


def get_changed_files_from_bitbucket_webhook(
    handler: ClientCommunicationHandler, commit_range: str
) -> dict:
    """Returns a dictionary of lists including the
    the files - full filepath - affected between two sequential parent-child
    Bit Bucket commits.

    :param str commit_range: The bit bucket diff specification
    :return dict: A dictionary of lists, with all added, updated, removed files.
    """

    def is_source_file(commit_object_version: dict) -> bool:
        return commit_object_version and commit_object_version["type"] == "commit_file"

    logger.debug("Compare differences between commits %s.", commit_range)

    diffstat_response = handler.git_client.compare_two_commits_diffstats(commit_range)
    logger.debug("Commits changes: %s", diffstat_response)
    bitbucket_diffs = {"modified": [], "added": [], "removed": []}

    for value in diffstat_response.get("values"):
        old_version = value.get("old")
        new_version = value.get("new")
        if (value["status"] in ["modified", "renamed"]) and is_source_file(new_version):
            bitbucket_diffs["modified"].append(new_version["path"])
        if value["status"] == "added" and is_source_file(new_version):
            bitbucket_diffs["added"].append(new_version["path"])
        if value["status"] == "removed" and is_source_file(old_version):
            bitbucket_diffs["removed"].append(old_version["path"])

    return bitbucket_diffs
