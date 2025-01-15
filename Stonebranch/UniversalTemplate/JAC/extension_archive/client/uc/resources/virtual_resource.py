from dataclasses import dataclass
from typing import Optional, Union

from client.uc.resources.uc_resource import UCResource


@dataclass
class VirtualResource(UCResource):  # pragma: no cover
    endpoint: str = "resources/virtual"

    @classmethod
    def get_class_name(cls):
        return "virtualresource"

    @classmethod
    def get_endpoint(cls, method: Optional[str] = None):
        if method == "list":
            return f"{cls.endpoint}/listadv"
        else:
            return cls.endpoint

    @classmethod
    def set_filters(
        cls,
        resource_name: str = None,
        business_service: str = None,
        type: str = None,
    ) -> Union[dict, None]:
        filters = {}
        filters["resourcename"] = resource_name
        filters["businessServices"] = business_service
        filters["type"] = type

        return super().set_query_params(filters)

    @classmethod
    def get_name_query_param(cls):
        return "resourcename"

    def get_delete_paylaod(self) -> dict:
        return {"resourcename": self.name}
