from dataclasses import dataclass
from typing import Optional, Union

from client.uc.resources.uc_resource import UCResource


@dataclass
class BusinessService(UCResource):  # pragma: no cover
    endpoint: str = "resources/businessservice"

    @classmethod
    def get_class_name(cls):
        return "businessservice"

    @classmethod
    def get_endpoint(cls, method: Optional[str] = None):
        if method == "list":
            return f"{cls.endpoint}/list"
        return cls.endpoint

    @classmethod
    def set_filters(cls, service_name=None, service_id=None) -> Union[dict, None]:
        filters = {}
        filters["busservice_name"] = service_name
        filters["busservice_id"] = service_id

        return super().set_query_params(filters)

    def get_delete_paylaod(self) -> dict:
        return {"busservicename": self.name}

    @classmethod
    def get_name_query_param(cls):  # pragma: no cover
        return "busservicename"
