from dataclasses import dataclass
from typing import Optional, Union

from client.uc.resources.uc_resource import UCResource


@dataclass
class Trigger(UCResource):  # pragma: no cover
    endpoint: str = "resources/trigger"

    @classmethod
    def get_class_name(cls):
        return "trigger"

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
        description: str = None,
        enabled: bool = None,
        trigger_name: str = None,
        tasks: list = None,
        type: str = None,
    ) -> Union[dict, None]:
        filters = {}
        filters["businessServices"] = business_service
        filters["description"] = description
        filters["enabled"] = enabled
        filters["triggername"] = trigger_name
        filters["tasks"] = tasks
        filters["type"] = type

        return super().set_query_params(filters)

    @classmethod
    def get_name_query_param(cls):
        return "triggername"

    def get_delete_paylaod(self) -> dict:
        return {"triggername": self.name}
