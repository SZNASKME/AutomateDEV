from dataclasses import dataclass
from typing import Optional, Union

from client.uc.resources.uc_resource import UCResource


@dataclass
class Credential(UCResource):
    endpoint: str = "resources/credential"

    @classmethod
    def get_class_name(cls):
        return "credentials"

    @classmethod
    def get_endpoint(cls, method: Optional[str] = None):
        if method == "list":
            return f"{cls.endpoint}/list"
        return cls.endpoint

    @classmethod
    def set_filters(
        cls, credential_name: str = None, credential_id: str = None
    ) -> Union[dict, None]:
        filters = {}
        filters["credentialname"] = credential_name
        filters["credentialid"] = credential_id

        return super().set_query_params(filters)

    @classmethod
    def get_name_query_param(cls):
        return "credentialname"

    def get_delete_paylaod(self) -> dict:
        return {"credentialname": self.name}
