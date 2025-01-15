from dataclasses import dataclass
from typing import Optional, Union

from client.uc.resources.uc_resource import UCResource


@dataclass
class Script(UCResource):
    endpoint: str = "resources/script"

    @classmethod
    def get_class_name(cls):
        return "script"

    @classmethod
    def get_endpoint(cls, method: Optional[str] = None):
        if method == "list":
            return f"{cls.endpoint}/list"
        return cls.endpoint

    @classmethod
    def set_filters(
        cls, script_name: str = None, script_id: str = None
    ) -> Union[dict, None]:
        filters = {}
        filters["scriptname"] = script_name
        filters["scriptid"] = script_id

        return super().set_query_params(filters)

    @classmethod
    def get_name_query_param(cls):
        return "scriptname"

    def get_delete_paylaod(self) -> dict:
        return {"scriptname": self.name}
