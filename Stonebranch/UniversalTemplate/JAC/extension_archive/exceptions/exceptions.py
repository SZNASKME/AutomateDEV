from typing import Optional, Type

from ue_framework.results.base_custom_results import GenericFailJSONResult

EXCEPTIONS_MAPPER = {}


class UnexpectedErrorResult(GenericFailJSONResult):
    exit_code: int = 1
    message: str = "FAIL: "


class ControllerInputException(Exception):
    pass


class InvalidGitContents(Exception):
    pass


class DataSyncException(Exception):
    pass
