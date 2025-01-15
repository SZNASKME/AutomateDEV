from typing import Optional

from ue_framework.results import ChoiceFieldResult
from ue_framework.results.base_custom_results import GenericFailJSONResult

from results.errors import (
    EXCEPTION_TO_RESULT_MAPPER,
    HTTP_ERROR_CODES_MAPPER,
    UnexpectedErrorResult,
)

_action_commands = dict()


def get_action(action):
    return _action_commands[action]


def action_command(action_name):
    def decorator_action_command(func):
        _action_commands[action_name] = func

    return decorator_action_command


def exc_callback_handler_dynamic_choice(
    e: Exception, logger
) -> Optional[ChoiceFieldResult]:
    result = exception_handler(e, logger)
    choice_result = ChoiceFieldResult(
        exit_code=result.exit_code, message=f"{str(result.message)}", values=[]
    )
    return choice_result


def exception_handler(e: Exception, logger) -> Optional[GenericFailJSONResult]:
    error_class = UnexpectedErrorResult
    if hasattr(e, "status_code"):
        logger.debug(e.response)
        error_class = HTTP_ERROR_CODES_MAPPER.get(e.status_code)
        return error_class(extension_output={}, exc=e.response)
    else:
        logger.debug(e)
        for exception, result_class in EXCEPTION_TO_RESULT_MAPPER.items():
            if e and issubclass(type(e), exception):
                error_class = result_class
        return error_class(extension_output={}, exc=e)
