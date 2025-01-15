from requests.exceptions import HTTPError


class HttpUcClientException(Exception):
    """HTTP Client Error"""

    def __init__(self, status_code, response, *args) -> None:
        super().__init__(*args)
        self.status_code = status_code
        self.response = response


class HttpUcServerException(Exception):
    """HTTP Client Error"""

    def __init__(self, status_code, response, *args) -> None:
        super().__init__(*args)
        self.status_code = status_code
        self.response = response


class UcClientException(Exception):
    """UC Client generic exception"""


class ListTaskFailed(Exception):
    """Custom Exception for handling advanced listing of Tasks"""

    def __init__(self, message, *args) -> None:
        super().__init__(*args)
        self.error_message = message
