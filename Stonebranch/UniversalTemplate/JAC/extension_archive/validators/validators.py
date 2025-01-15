import json
from urllib.parse import ParseResult, urlparse  # python3


class Format:
    @staticmethod
    def url(value) -> str:
        try:
            urlparse(value)
        except Exception as e:
            raise ValueError("Field value should be a valid URL") from e
        return value

    @staticmethod
    def json(value) -> dict:
        try:
            json.loads(value)
        except Exception as e:
            raise ValueError("Field value should be JSON") from e
        return value
