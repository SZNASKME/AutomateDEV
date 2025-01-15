import io
import json
from json import JSONDecodeError
from typing import Optional
from urllib.parse import quote_plus

import requests
import yaml
from jsonpath_ng.ext import parse

from client.git.exceptions import GitClientException


class URLString(str):
    _ignore = ("base_url",)

    def format(self, *args, **kwargs) -> str:
        nargs = tuple(quote_plus(str(arg)) for arg in args)
        nkwargs = {
            k: v if k in self._ignore else quote_plus(str(v)) for k, v in kwargs.items()
        }
        return super().format(*nargs, **nkwargs)


def convert_yaml_to_json(yaml_contents: str) -> str:  # pragma: no cover
    """_Converts a YAML to JSON format_

    :param str yaml_contents: _the yaml contents as string_
    :return str: _the json contents as string_
    """
    return json.dumps(yaml.load(yaml_contents, Loader=yaml.FullLoader))


def covert_json_to_yaml(json_contents: str) -> str:  # pragma: no cover
    """_Converts a JSON to YAML format_

    :param str json_contents: _the json contents as string_
    :return str: _the yaml contents as string_
    """
    try:
        import ruamel.yaml
    except ModuleNotFoundError:
        import yaml

        return yaml.dump(json.loads(json_contents), default_flow_style=False)

    yaml = ruamel.yaml.YAML()

    data = json.loads(json_contents)
    ruamel.yaml.scalarstring.walk_tree(data)
    # Create a virtual file-like object
    output_stream = io.StringIO()

    yaml.dump(data, output_stream)
    yaml_str = output_stream.getvalue()
    return yaml_str


def parse_json(data: dict, json_path: str) -> Optional[list]:
    """Use jsonpath to parse a given a response JSON data.

    :param dict data: JSON Data to be parsed
    :param str json_path: jsonpath expression
    :return Optional[list]: list with matched values
    """

    jsonpath_expr = parse(json_path)
    matched_values = [match.value for match in jsonpath_expr.find(data)]
    return matched_values


def is_status_success(status_code: int):
    """Check if response status is 200."""
    return status_code == 200


def raise_exception_if_not_success(response: requests.Response) -> None:
    """Raise exception on failed request."""
    if not is_status_success(response.status_code):
        error = response.json()
        message = error["error"]["message"]
        raise GitClientException(f"{message}")


def get_error_from_response(response: requests.Response) -> Optional[str]:
    """Return error message from failed response"""
    try:
        return response.json()["error"]["message"]
    except (JSONDecodeError, KeyError):
        return
