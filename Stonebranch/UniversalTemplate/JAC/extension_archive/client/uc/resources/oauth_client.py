from dataclasses import dataclass
from typing import Optional, Union

from client.uc.resources.uc_resource import UCResource


@dataclass
class OAuthClient(UCResource):
    endpoint: str = "resources/oauthclient"

    @classmethod
    def get_class_name(cls):
        return "oauthclient"

    @classmethod
    def get_endpoint(cls, method: Optional[str] = None):
        if method == "list":
            return f"{cls.endpoint}/list"
        return cls.endpoint

    @classmethod
    def set_filters(
        cls, client_name: str = None, client_id: str = None
    ) -> Union[dict, None]:
        filters = {}
        filters["oauthclientname"] = client_name
        filters["oauthclientid"] = client_id

        return super().set_query_params(filters)

    @classmethod
    def get_name_query_param(cls):  # pragma: no cover
        return "oauthclientname"

    def get_delete_paylaod(self) -> dict:  # pragma: no cover
        return {"oauthclientname": self.name}
