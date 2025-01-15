from ue_framework.exceptions.exception_catcher_deco import exceptions_catcher_wrapper
from ue_framework.results import ChoiceFieldResult
from universal_extension import ExtensionResult
from universal_extension.deco.choice import dynamic_choice_command

from actions import (
    ExportToGitRepositoryAction,
    ImportUacDefinitionsAction,
    ListUacDefinitionsAction,
)
from client.client_communication_handler import ClientCommunicationHandler
from client.uc.utils.utils import GlobalConfig
from decorators.decorators import action_command, exc_callback_handler_dynamic_choice
from enums.enums import ActionsEnum, SelectionMethodEnum
from extension_base import BaseExtension
from serializers.extension_input import (
    GitDynamicChoiceSerializer,
    UaCDynamicChoiceSerializer,
)
from serializers.extension_output import ExtensionStatusSerializer


class Extension(BaseExtension):
    @dynamic_choice_command("selection_name")
    @exceptions_catcher_wrapper(
        callback_func=exc_callback_handler_dynamic_choice, logger_name="UNV"
    )
    def get_selection_name_choice(self, choice_field_input: dict) -> ChoiceFieldResult:
        """
        Handle the execution of "selection_name" dynamic choice field. Fetch all definitions
        of the selected type and provide their names in a list format to the user

        :param dict choice_field_input: The input dict of the dynamic choice command
        :return ChoiceFieldResult: The result class of the dynamic choice command.
        """

        serialized_input = UaCDynamicChoiceSerializer(**choice_field_input)

        # set `dynamic_choice_workflow_selection` to `True` in the global
        # config object to indicate that the `selection_name` dynanic choice
        # command was executed with the value of Workflow
        _ = GlobalConfig(
            dynamic_choice_workflow_selection=serialized_input.selection_method
            == SelectionMethodEnum.WORKFLOW.value
        )

        action = ListUacDefinitionsAction(serialized_input)
        definitions = action.fetch_definitions_by_type(
            serialized_input.selection_method
        )

        choice_list = []

        for definition in definitions:
            choice_list.append(definition.name)

        return ChoiceFieldResult(exit_code=0, message="Success", values=choice_list)

    @dynamic_choice_command("git_repository")
    @exceptions_catcher_wrapper(
        callback_func=exc_callback_handler_dynamic_choice, logger_name="UNV"
    )
    def git_repository(self, dependent_fields: dict) -> ChoiceFieldResult:
        """
        Handle the execution of "git_repository" dynamic choice field.
        Fetch all available repositories for the given credentials.

        :param dict dependent_fields: The input dict of the dynamic choice command
        :return ChoiceFieldResult: The result class of the dynamic choice command.
        """
        serialized_input = GitDynamicChoiceSerializer(**dependent_fields)
        handler = ClientCommunicationHandler(serialized_input)
        handler.set_git_client()
        git_client = handler.get_git_client()
        repositories = git_client.get_repos_list()
        return ChoiceFieldResult(exit_code=0, message="Success", values=repositories)

    @dynamic_choice_command("git_repository_branch")
    @exceptions_catcher_wrapper(
        callback_func=exc_callback_handler_dynamic_choice, logger_name="UNV"
    )
    def git_repository_branch(self, dependent_fields: dict) -> list:
        """
        Handle the execution of "git_repository_branch" dynamic choice field.
        Fetch all available branches for the given repository.

        :param dict dependent_fields: The input dict of the dynamic choice command
        :return ChoiceFieldResult: The result class of the dynamic choice command.
        """
        dynamic_choice_input = self.modify_input_when_action_trigger_by_webhook(
            dependent_fields
        )
        serialized_input = GitDynamicChoiceSerializer(**dynamic_choice_input)
        handler = ClientCommunicationHandler(serialized_input)
        handler.set_git_client()
        git_client = handler.get_git_client()
        branches = git_client.get_repo_branches(
            repo_path=serialized_input.git_repository
        )
        return ChoiceFieldResult(exit_code=0, message="Success", values=branches)

    @action_command(ActionsEnum.LIST_UAC_DEFINITIONS.value)
    def action_list_uac_definitions(self, extension_input: dict) -> ExtensionResult:
        self.set_extension_status(status="Querying UAC Definitions")
        action_result = self.controller.execute(
            ListUacDefinitionsAction, extension_input
        )
        self.set_extension_status(exit_code=action_result.exit_code)
        return action_result

    @action_command(ActionsEnum.EXPORT_GIT.value)
    def action_export_definitions_to_git(
        self, extension_input: dict
    ) -> ExtensionResult:
        self.set_extension_status(status="Exporting UAC Definitions")
        action_result = self.controller.execute(
            ExportToGitRepositoryAction, extension_input
        )
        self.set_extension_status(exit_code=action_result.exit_code)
        return action_result

    @action_command(ActionsEnum.IMPORT_UAC_DEFINITIONS.value)
    def action_import_uac_definitions(self, extension_input: dict) -> ExtensionResult:
        self.set_extension_status(status="Importing UAC Definitions")
        action_result = self.controller.execute(
            ImportUacDefinitionsAction,
            extension_input,
        )
        self.set_extension_status(exit_code=action_result.exit_code)
        return action_result

    def set_extension_status(self, status: str = None, exit_code: int = None) -> None:
        final_status = None
        if exit_code is not None:
            final_status = "Finished" if exit_code == 0 else "Finished with errors"
        status = final_status if final_status else status

        extension_status_serializer = ExtensionStatusSerializer(extension_status=status)
        self.update_extension_status(extension_status_serializer)
