from dataclasses import dataclass, field
from typing import Optional, Union

from client.uc.resources.uc_resource import UCResource


@dataclass
class AgentCluster(UCResource):
    endpoint: str = "resources/agentcluster"
    description: Optional[str] = None
    distribution: Optional[str] = "Any"
    ignoreInactiveAgents: Optional[bool] = False
    ignoreSuspendedAgents: Optional[bool] = False
    limitType: Optional[str] = "Unlimited"
    limitAmount: Optional[int] = None
    networkAlias: Optional[str] = None
    networkAliasPort: Optional[str] = None
    opswiseGroups: Optional[list] = field(default_factory=list)
    retainSysIds: Optional[bool] = True

    @classmethod
    def get_class_name(cls):  # pragma: no cover
        return "agentcluster"

    @classmethod
    def get_endpoint(cls, method: Optional[str] = None):
        if method == "list":
            return f"{cls.endpoint}/listadv"
        else:
            return cls.endpoint

    @classmethod
    def set_filters(
        cls, agent_cluster_name=None, business_services=None, cluster_type=None
    ) -> Union[dict, None]:
        filters = {}
        filters["agentclustername"] = agent_cluster_name
        filters["businessServices"] = business_services
        filters["type"] = cluster_type

        return super().set_query_params(filters)

    @classmethod
    def get_name_query_param(cls):
        return "agentclustername"

    def get_delete_paylaod(self) -> dict:
        return {"agentclustername": self.name}


@dataclass
class WindowsAgentCluster(AgentCluster):
    type: str = "windowsAgentCluster"

    @classmethod
    def get_class_name(cls):  # pragma: no cover
        return "windowsAgentCluster"


@dataclass
class UnixAgentCluster(AgentCluster):  # pragma: no cover
    type: str = "unixAgentCluster"

    @classmethod
    def get_class_name(cls):
        return "unixAgentCluster"
