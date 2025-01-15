from dataclasses import dataclass, field
from typing import Optional, Union


@dataclass
class UCResource:
    """
    Parent class of all UC resource classes.
    """

    endpoint: str
    name: str = field(default=None)
    subtype: str = field(default=None)
    definition: dict = field(default_factory=dict)
    filters: dict = field(default_factory=dict)

    @classmethod
    def set_query_params(cls, filter_dict: dict) -> Union[dict, None]:
        """
        Contructs a query parameter that can be used in the REST call, for filtering data.
        """
        return {k: v for k, v in filter_dict.items() if v is not None}


@dataclass
class Template(UCResource):  # pragma: no cover
    @classmethod
    def get_endpoint(cls, method: Optional[str] = None):
        if method == "list":
            return f"{cls.endpoint}/list"
        return cls.endpoint

    @classmethod
    def set_filters(
        cls, template_name: str = None, template_id: str = None
    ) -> Union[dict, None]:
        filters = {}
        filters["templatename"] = template_name
        filters["templateid"] = template_id

        return super().set_query_params(filters)

    @classmethod
    def get_name_query_param(cls):
        return "templatename"

    def get_delete_paylaod(self) -> dict:
        return {"templatename": self.name}
