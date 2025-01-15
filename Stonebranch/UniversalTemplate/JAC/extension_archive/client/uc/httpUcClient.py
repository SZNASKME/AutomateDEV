import base64
import logging
import os
import urllib
from typing import Optional, Union

import requests

from logger import logger


def _try_convert_int(value: Union[str, int], default: int = 30) -> int:
    """
    Try to convert `value` to int, if conversion fails return `default`
    """
    try:
        n = int(value)
    except (ValueError, TypeError):
        logger.warning(
            "Failed to convert %s to integer, using default value of %d", value, default
        )
        n = default

    return n


class HttpRestClient:  # pragma: no cover
    """
    Http Client to send the REST API requests to Universal Controller.
    """

    LOGGING_MAPPER = {
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "WARNING": logging.WARNING,
    }
    HTTP_TIMEOUT = _try_convert_int(os.getenv("UE_JAC_UC_HTTP_TIMEOUT", 60))

    def __init__(
        self,
        url: str,
        user: str,
        password: Optional[str],
        token: Optional[str],
        log_level: str,
        verify: bool,
    ):
        self.url = url
        self.user = user
        self.password = password
        self.token = token
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.verify = verify

        self._set_headers(self.headers)
        self._set_logger()

    def _set_logger(self) -> None:
        """
        Set class logger.
        """
        self.logger = logger

    def _set_headers(self, headers: dict) -> None:
        """
        Set Request headers.
        """
        self.headers = headers
        if not self.token:
            self.data = str(self.user) + ":" + str(self.password)
            self.encoded_bytes = base64.b64encode(self.data.encode("utf-8"))
            self.encoded_str = str(self.encoded_bytes, "utf-8")
            self.headers["Authorization"] = "Basic " + self.encoded_str
        else:
            self.headers["Authorization"] = "Bearer " + self.token

    def get(self, uc_resource: str, query: str = None) -> requests.Response:
        """
        Send GET request.

        :param str uc_resource: The resource URI to send request.
        :param str query: The query parameter to use
        :return Response: The formatted response
        """
        if not query:
            uri = f"{self.url}/{uc_resource}"
        else:
            query_encoded = urllib.parse.urlencode(query)
            uri = f"{self.url}/{uc_resource}?{query_encoded}"

        self.logger.debug(f"Executing REST API: {uri}")
        response = requests.get(
            uri, headers=self.headers, verify=self.verify, timeout=self.HTTP_TIMEOUT
        )
        response.raise_for_status()
        return response

    def post(self, uc_resource: str, payload: dict) -> requests.Response:
        """
        Send POST request.

        :param str uc_resource: The resource URI to send request.
        :param dict payload: The request data payload
        """

        uri = f"{self.url}/{uc_resource}"
        self.logger.debug(f"Executing REST API: {uri}")
        response = requests.post(
            uri,
            headers=self.headers,
            json=payload,
            verify=self.verify,
            timeout=self.HTTP_TIMEOUT,
        )
        response.raise_for_status()
        return response

    def put(self, uc_resource: str, payload: dict) -> requests.Response:
        """
        Send PUT request.

        :param str uc_resource: The resource URI to send request.
        :param dict payload: The request data payload
        """
        uri = f"{self.url}/{uc_resource}"
        self.logger.debug(f"Executing REST API: {uri}")
        response = requests.put(
            uri,
            headers=self.headers,
            json=payload,
            verify=self.verify,
            timeout=self.HTTP_TIMEOUT,
        )
        response.raise_for_status()
        return response

    def delete(self, uc_resource: str, query: str) -> requests.Response:
        """
        Send DELETE request.

        :param str uc_resource: The resource URI to send request.
        :param str query: The query parameter to use.
        """
        query = urllib.parse.urlencode(query)
        uri = f"{self.url}/{uc_resource}?{query}"
        self.logger.debug(f"Executing REST API:{uri}")
        response = requests.delete(
            uri, headers=self.headers, verify=self.verify, timeout=self.HTTP_TIMEOUT
        )
        response.raise_for_status()
        return response
