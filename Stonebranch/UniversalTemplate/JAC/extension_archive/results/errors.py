import pydantic
from requests.exceptions import ConnectionError as RequestsConnectionError
from ue_framework.results.base_custom_results import GenericFailJSONResult

from client.git.exceptions import (
    GitAuthException,
    GitBaseException,
    GitBranchNotExistException,
    GitClientException,
    GitFileNotExistError,
    GitRepoNotExistException,
)
from client.uc.exceptions import (
    HttpUcClientException,
    HttpUcServerException,
    UcClientException,
)
from exceptions import InvalidGitContents
from exceptions.exceptions import DataSyncException


class UnexpectedErrorResult(GenericFailJSONResult):
    exit_code: int = 1
    message: str = "UnexpectedError: "


class FailedErrorResult(GenericFailJSONResult):
    exit_code: 1
    message: str = "FAIL: "


class AuthenticationErrorResult(GenericFailJSONResult):
    exit_code: int = 2
    message: str = "AUTHENTICATION ERROR: "


class AuthorizationErrorResult(GenericFailJSONResult):
    exit_code: int = 3
    message: str = "AUTHORIZATION ERROR: "


class DataValidationErrorResult(GenericFailJSONResult):
    exit_code: int = 20
    message: str = "Incorrect Field Data, see STDERR for more details."


class ConnectionErrorResult(GenericFailJSONResult):
    exit_code: int = 10
    message: str = "Connection failed for API: "


class ConnectionAuthError(GenericFailJSONResult):
    exit_code: int = 11
    message: str = "Auth failed on API: "


class DataSyncError(GenericFailJSONResult):
    exit_code: int = 21
    message: str = "Some errors where produced during data synchronization process: "


EXCEPTION_TO_RESULT_MAPPER = {
    pydantic.error_wrappers.ValidationError: DataValidationErrorResult,
    ValueError: DataValidationErrorResult,
    RequestsConnectionError: ConnectionErrorResult,
    GitBaseException: FailedErrorResult,
    GitClientException: DataSyncError,
    GitFileNotExistError: DataSyncError,
    GitRepoNotExistException: ConnectionErrorResult,
    GitBranchNotExistException: ConnectionErrorResult,
    HttpUcClientException: DataSyncError,
    HttpUcServerException: DataSyncError,
    UcClientException: DataSyncError,
    InvalidGitContents: DataSyncError,
    DataSyncException: DataSyncError,
    GitAuthException: ConnectionAuthError,
}

HTTP_ERROR_CODES_MAPPER = {
    400: DataSyncError,
    401: ConnectionAuthError,
    403: ConnectionAuthError,
    408: ConnectionErrorResult,
    500: ConnectionErrorResult,
    502: ConnectionErrorResult,
    503: ConnectionErrorResult,
    504: ConnectionErrorResult,
    511: ConnectionErrorResult,
}
