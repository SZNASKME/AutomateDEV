from dataclasses import dataclass
from typing import Optional, Union

from client.uc.resources.uc_resource import UCResource


@dataclass
class CustomDay(UCResource):
    endpoint: str = "resources/customday"

    @classmethod
    def get_class_name(cls):
        return "customday"

    @classmethod
    def get_endpoint(cls, method: Optional[str] = None):
        if method == "list":
            return f"{cls.endpoint}/list"
        return cls.endpoint

    @classmethod
    def set_filters(
        cls, custom_day_name: str = None, custom_day_id: str = None
    ) -> Union[dict, None]:
        filters = {}
        filters["customdayname"] = custom_day_name
        filters["customdayid"] = custom_day_id

        return super().set_query_params(filters)

    @classmethod
    def get_name_query_param(cls):
        return "customdayname"

    def get_delete_paylaod(self) -> dict:
        return {"customdayname": self.name}
