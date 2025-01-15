from dataclasses import dataclass
from typing import Optional, Union

from client.uc.resources.uc_resource import UCResource


@dataclass
class Connection(UCResource):
    @classmethod
    def get_endpoint(cls, method: Optional[str] = None):
        if method == "list":
            return f"{cls.endpoint}/list"
        return cls.endpoint

    @classmethod
    def set_filters(
        cls, connection_name: str = None, connection_id: str = None
    ) -> Union[dict, None]:
        filters = {}
        filters["connectionname"] = connection_name
        filters["connectionid"] = connection_id

        return super().set_query_params(filters)

    @classmethod
    def get_name_query_param(cls):
        return "connectionname"

    def get_delete_paylaod(self) -> dict:
        return {"connectionname": self.name}


@dataclass
class DbConnection(Connection):
    endpoint: str = "resources/databaseconnection"
    subtype: str = "databaseconnection"

    @classmethod
    def get_class_name(cls):
        return "databaseconnection"


@dataclass
class EmailConnection(Connection):
    endpoint: str = "resources/emailconnection"
    subtype: str = "emailconnection"

    @classmethod
    def get_class_name(cls):
        return "emailconnection"


@dataclass
class SapConnection(Connection):
    endpoint: str = "resources/sapconnection"
    subtype: str = "sapconnection"

    @classmethod
    def get_class_name(cls):
        return "sapconnection"


@dataclass
class PeopleSoftConnection(Connection):
    endpoint: str = "resources/peoplesoftconnection"
    subtype: str = "peoplesoftconnection"

    @classmethod
    def get_class_name(cls):
        return "peoplesoftconnection"


@dataclass
class SnmpManager(Connection):
    endpoint: str = "resources/snmpmanager"
    subtype: str = "snmpmanager"

    @classmethod
    def get_class_name(cls):
        return "snmpmanager"

    @classmethod
    def set_filters(cls, manager_name: str = None, manager_id: str = None) -> dict:
        filters = {}
        filters["managername"] = manager_name
        filters["managerid"] = manager_id

        return {k: v for k, v in filters.items() if v is not None}

    @classmethod
    def get_name_query_param(cls) -> str:
        return "managername"

    def get_delete_paylaod(self) -> dict:
        return {"managername": self.name}
