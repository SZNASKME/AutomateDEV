from __future__ import print_function

import platform
import re
import sys

from pydantic import BaseModel, validator
from ue_framework.exceptions.exception_catcher_deco import exceptions_catcher_wrapper
from universal_extension import ExtensionResult, UniversalExtension

from controllers.controller import Controller
from decorators.decorators import exception_handler, get_action
from enums.enums import ActionsEnum
from serializers.extension_output import ExtensionStatusSerializer
from settings import EXTENSION_NAME, EXTENSION_VERSION

_LOGGER_NAME = "UNV"


class RoutingInputSerializer(BaseModel):
    """Simply the way to route actions"""

    action: ActionsEnum

    class Config:
        use_enum_values = True

    @validator("action", pre=True)
    def retrieve_value_from_list(cls, value: list) -> str:
        return value[0] if value and value[0] else None


class BaseExtension(UniversalExtension):
    def __intro(self, extension_input: dict) -> None:
        self.log.debug(f"extension_start fields: {extension_input}")
        self.log.info(f"Extension Information: {EXTENSION_NAME}-{EXTENSION_VERSION}")
        system, node, release, version, machine, processor = platform.uname()
        self.log.info(
            f"System Information: Python Version: {sys.version}, system: {system}, "
            f"release: {release}, version: {version}, machine type: {machine}"
        )

    @exceptions_catcher_wrapper(
        callback_func=exception_handler, logger_name=_LOGGER_NAME
    )
    def extension_start(self, extension_input: dict) -> ExtensionResult:
        self.__intro(extension_input)
        self.controller = Controller()
        router = RoutingInputSerializer(**extension_input)
        extension_input = self.modify_input_when_action_trigger_by_webhook(
            extension_input
        )
        action = router.action
        self.log.debug(f"Running extension_start for action: {action}")
        try:
            method_to_run = get_action(action)
        except KeyError:
            raise NotImplementedError(f"Not implemented for action: {action}")

        return method_to_run(self, extension_input)

    def extension_cancel(self):
        while True:
            try:
                self.controller.cancel_action()
                if hasattr(self.controller, "action"):
                    break
            except AttributeError:
                continue

    def update_extension_status(self, status: ExtensionStatusSerializer) -> None:
        super().update_extension_status(status.dict())

    def modify_input_when_action_trigger_by_webhook(self, input_dict: dict) -> dict:
        """
        Check inf the action is triggered from a webhook and if so, modify the lists containing the git file paths.

        :param dict input_dict: The input as provided from the user
        :return dict: The modified, if needed extension input
        """
        import_lists_var_pattern = re.compile(r"\[(\w+):\s*(\w+)\]")
        git_choices_var_pattern = re.compile(r"\$\{(\w+)\}")

        # Resolve task instance variables provided as input when action is triggered by webhook.
        for key, value in input_dict.items():
            if (
                key
                in [
                    "add_uc_definitions_list",
                    "modify_uc_definitions_list",
                    "remove_uc_definitions_list",
                ]
                and value
            ):
                match = import_lists_var_pattern.match(value)
                if match:
                    action_variable = value.replace("]", "").split(":")[1]
                    input_dict[key] = self.uip.task_variables[
                        action_variable.replace(" ", "")
                    ]

            # [Redmine 31998]: Workaround for supporting UC variables in dynamic choice fields
            if key in ["git_repository", "git_repository_branch"] and value:
                git_choice_var = value[0]
                match = git_choices_var_pattern.match(git_choice_var)
                if match:
                    git_choice_value = git_choice_var[2:-1]
                    resolved_var = self.uip.task_variables[git_choice_value]
                    input_dict[key][0] = resolved_var
        return input_dict
