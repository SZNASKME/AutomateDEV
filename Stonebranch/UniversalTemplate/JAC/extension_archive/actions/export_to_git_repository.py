import json
from typing import List, Optional, Tuple

from tabulate import tabulate

from actions.list_uac_definitions import ListUacDefinitionsAction
from adaptors import ActionAdaptors
from client.git.exceptions import GitClientException
from client.git.utils import covert_json_to_yaml
from client.uc.exceptions.exceptions import ListTaskFailed
from client.uc.resources.uc_resource import UCResource
from enums import GitFileFormat
from logger import logger
from serializers import (
    ExportToGitRepositoryInputSerializer,
    ExportToGitRepositoryOutputSerializer,
    ExtensionInputSerializer,
)


class ExportToGitRepositoryAction(ListUacDefinitionsAction):
    """
    Class responsible for executing the List UAC Definitions action.

    """

    input_adapter = ActionAdaptors.export_to_git_repository_adaptor
    input_serializer = ExportToGitRepositoryInputSerializer
    output_serializer = ExportToGitRepositoryOutputSerializer

    def __init__(self, action_input: ExtensionInputSerializer):
        if action_input.ff_commit_msg is False:
            action_input.git_commit_message = (
                f"[uac push]{action_input.git_commit_message }"
            )
        super().__init__(action_input)
        self.handler.set_git_client()

    def execute(self):
        logger.info("Exporting UAC definitions to Git.")
        exported_files = []
        failed_files = []

        if self.is_extension_cancelled is False:
            try:
                uc_definitions = self._get_definitions_from_uc()
                exported_files, failed_files = self._upload_uc_definitions_to_git(
                    uc_definitions
                )
            except ListTaskFailed as e:
                # [Redmine: #32982] Workaround due to API /task/listadv limitation
                output_dict = {
                    "definitions_selected": {},
                    "definitions_exported": {},
                    "errors": [e.error_message],
                }
                return output_dict

        logger.info("Export completed. Constructing result table.")

        result_table = self.construct_result_table_data(exported_files + failed_files)
        print(tabulate(result_table, headers="keys", tablefmt="rst"))

        output_dict = self._set_up_output_dict(
            uc_definitions, exported_files, failed_files
        )
        return output_dict

    def _get_definitions_from_uc(self) -> list:
        """
        Fetch the selected definitions from UC.
        """
        return self.fetch_definitions()

    def _upload_uc_definitions_to_git(self, uc_definitions: list) -> Tuple[list, list]:
        """
        Upload the definitions as fetched from UC to git one-by-one. If an upload fails,
        the object and the reason of failure is appended to a list that is returned.

        :param list uc_definitions: The UC definitions
        :return Tuple[list, list]: A tuple with the lists of exported and failed definitions.
        """
        exported_definitions = []
        failed_definitions = []
        filepath_contents = {}
        filepath_definition = {}

        for definition in uc_definitions:
            git_path = self.handler.get_git_path(definition)
            logger.debug(
                f"UC Definition {definition.name} will be exported to {git_path}"
            )
            file_content_converted = self.convert_file_contents(definition.definition)
            filepath_contents[git_path] = file_content_converted
            filepath_definition[git_path] = definition

        logger.info(
            "Start export of definitions on %s using commit message: %s.",
            self.action_input.git_service_provider,
            self.action_input.git_commit_message,
        )

        try:
            self.handler.batch_add_files_to_git(files=filepath_contents)
            exported_definitions = [
                (definition, git_path, None)
                for git_path, definition in filepath_definition.items()
            ]
        except GitClientException as err:
            failed_definitions = [
                (definition, git_path, err)
                for git_path, definition in filepath_definition.items()
            ]

        return exported_definitions, failed_definitions

    def convert_file_contents(self, definition: dict) -> str:
        """_Convert file contents according to the provided File Format_

        :param dict definition: _The raw UC definition_
        :return str: _The converted file contents_
        """
        file_format = self.action_input_serialized.git_repository_file_format
        file_content = json.dumps(definition, indent=4)

        if file_format == GitFileFormat.YAML.value.lower():
            file_content = covert_json_to_yaml(file_content)

        return file_content

    def _set_up_output_dict(
        self,
        listed_uc_definitions: list,
        exported_definitions: list,
        failed_definitions: list,
    ) -> dict:
        """
        Set up the output dict of the action depending on the results

        :param list listed_uc_definitions: The definitions listed from UC.
        :param list failed_files: The definitions that failed to be uploaded.
        The list contains tuples of three elements:
        failed_definition[0] = the actual definition class
        failed_definition[1] = the git path this definitions were to be saved,
        failed_definition[2] = the reason of failure
        """
        uc_result = self._count_selected_definitions(listed_uc_definitions)
        git_result = self._count_selected_definitions(
            [definition[0] for definition in exported_definitions]
        )
        output_dict = {}
        output_dict["definitions_selected"] = uc_result
        output_dict["errors"] = []
        if not failed_definitions:
            output_dict["definitions_exported"] = git_result
        else:
            uc_copy = uc_result.copy()
            for failed_definition in failed_definitions:
                definition_name = failed_definition[0].get_class_name()
                if definition_name in list(uc_copy.keys()):
                    counter = uc_copy.get(definition_name)
                    counter -= 1
                    uc_copy[definition_name] = counter

                    output_dict["errors"].append(
                        f"Failed to create git object for definition '{failed_definition[0].name}'"
                        f"(Git path: {failed_definition[1]}. {failed_definition[2]}."
                    )

            output_dict["definitions_exported"] = uc_copy

        return output_dict

    def construct_result_table_data(
        self, definitions: List[Tuple[UCResource, str, Optional[str]]]
    ) -> List[dict]:
        """
        Create the appropriate columns for the table to be printed.
        Each element of the list is a tuple that contains the UC Resource, the git path and the error (if any).
        definition[0] = UC Resource
        definition[1] = git path
        definition[2] = error
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

        data = super().construct_result_table_data(
            [definition[0] for definition in definitions]
        )

        statuses = []
        git_paths = []
        for definition in definitions:
            git_path = definition[1]
            error = definition[2]
            git_paths.append(git_path)

            if error:
                statuses.append("failed")
            else:
                statuses.append("exported")

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
