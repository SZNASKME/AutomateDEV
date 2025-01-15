from dataclasses import dataclass
from typing import Optional, Union

from client.uc.resources.uc_resource import UCResource


@dataclass
class Variable(UCResource):  # pragma: no cover
    endpoint: str = "resources/variable"

    @classmethod
    def get_class_name(cls):
        return "variable"

    @classmethod
    def get_endpoint(cls, method: Optional[str] = None):
        if method == "list":
            return f"{cls.endpoint}/listadv"
        else:
            return cls.endpoint

    @classmethod
    def set_filters(
        cls,
        business_service: str = None,
        scope: str = None,
        task_name: bool = None,
        trigger_name: str = None,
        variable_name: str = None,
    ) -> Union[dict, None]:
        filters = {}
        filters["businessServices"] = business_service
        filters["scope"] = scope
        filters["taskname"] = task_name
        filters["triggername"] = trigger_name
        filters["variablename"] = variable_name

        return super().set_query_params(filters)

    @classmethod
    def get_name_query_param(cls):
        return "variablename"

    def get_delete_paylaod(self) -> dict:
        return {"variablename": self.name}
