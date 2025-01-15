from ue_framework.exceptions.exception_catcher_deco import exceptions_catcher_wrapper

from actions import BaseAction
from decorators.decorators import exception_handler
from exceptions import ControllerInputException
from logger import logger
from results.success import DataSyncResult, SuccessResult
from serializers import ActionSerializer
from serializers.extension_input import ExtensionInputSerializer
from serializers.extension_output import ExtensionOutputSerializer, InvocationSerializer


class Controller:
    def __init__(self):
        self.input_serializer = ExtensionInputSerializer
        self.output_serializer = ExtensionOutputSerializer

    @exceptions_catcher_wrapper(callback_func=exception_handler, logger_name="UNV")
    def execute(self, action: BaseAction, extension_input: dict):
        if not action:
            raise ControllerInputException("No action provided")
        serialized_extension_input = self.input_serializer(**extension_input)
        logger.debug("Serialized input: " + str(serialized_extension_input.dict()))
        self.action = action(serialized_extension_input)

        actions_result = self._execute_action()

        extension_output = self._build_extension_output(extension_input, actions_result)
        logger.info("Controller: execute: done")
        serialized_extension_output = self.output_serializer(**extension_output)

        errors = serialized_extension_output.result.get("errors")
        if errors:
            result = DataSyncResult(extension_output=serialized_extension_output.dict())
        else:
            result = SuccessResult(extension_output=serialized_extension_output.dict())
        return result

    def _build_extension_output(self, extension_input, actions_result):
        # List action has no errors list on output.
        if hasattr(actions_result, "errors") and actions_result.errors:
            return {
                "exit_code": DataSyncResult.exit_code,
                "status_description": DataSyncResult.message,
                "status": "FAILED",
                "invocation": InvocationSerializer(fields=extension_input),
                "result": actions_result,
            }
        elif self.action.is_extension_cancelled:
            return {
                "exit_code": SuccessResult.exit_code,
                "status_description": "Extension Cancelled",
                "status": "CANCEL",
                "invocation": InvocationSerializer(fields=extension_input),
                "result": actions_result,
            }
        else:
            return {
                "exit_code": SuccessResult.exit_code,
                "status_description": SuccessResult.message,
                "status": "SUCCESS",
                "invocation": InvocationSerializer(fields=extension_input),
                "result": actions_result,
            }

    def _execute_action(self) -> ActionSerializer:
        """
        Method to execute the selected action

        :return ActionSerializer: The serialized output of the action
        """
        return self.action.get_result()

    def cancel_action(self):
        """
        Method to cancel the ongoing action.
        """
        action_to_cancel = self.get_action_class()
        action_to_cancel.action_cancel()

    def get_action_class(self) -> BaseAction:
        """
        Get the current action that is executed.

        :return BaseAction: The selected action.
        """
        return self.action
