from dataclasses import dataclass
from typing import Optional, Union

from client.uc.resources.uc_resource import UCResource


@dataclass
class Calendar(UCResource):
    endpoint: str = "resources/calendar"

    @classmethod
    def get_class_name(cls):
        return "calendar"

    @classmethod
    def get_endpoint(cls, method: Optional[str] = None):
        if method == "list":
            return f"{cls.endpoint}/list"
        return cls.endpoint

    @classmethod
    def set_filters(
        cls, calendar_name: str = None, calendar_id: str = None
    ) -> Union[dict, None]:
        filters = {}
        filters["calendarname"] = calendar_name
        filters["calendarid"] = calendar_id

        return super().set_query_params(filters)

    @classmethod
    def get_name_query_param(cls):
        return "calendarname"

    def get_delete_paylaod(self) -> dict:
        return {"calendarname": self.name}
