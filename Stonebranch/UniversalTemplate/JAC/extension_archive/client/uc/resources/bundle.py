from dataclasses import dataclass, field
from typing import Optional, Union

from client.uc.resources.uc_resource import UCResource


@dataclass
class Bundle(UCResource):  # pragma: no cover
    endpoint: str = "resources/bundle"
    definition = {}
    report: bool = False
    promoteByBusinessServices: Optional[list] = None
    promoteBundleDefinition: bool = False
    opswiseGroups: Optional[list] = field(default_factory=list)
    excludeOnExistence: Optional[str] = None
    defaultPromotionTarget: Optional[str] = None
    bundleVirtualResources: Optional[str] = None
    followReferences: bool = False
    bundle_variables: Optional[list] = field(default_factory=list)
    bundle_universal_templates: Optional[list] = field(default_factory=list)
    bundle_tasks: Optional[list] = field(default_factory=list)
    bundle_triggers: Optional[list] = field(default_factory=list)
    bundle_snmp_managers: Optional[list] = field(default_factory=list)
    bundle_scripts: Optional[list] = field(default_factory=list)
    bundle_sap_connections: Optional[list] = field(default_factory=list)
    bundle_peoplesoft_connections: Optional[list] = field(default_factory=list)
    bundle_email_templates: Optional[list] = field(default_factory=list)
    bundle_email_connections: Optional[list] = field(default_factory=list)
    bundle_database_connections: Optional[list] = field(default_factory=list)
    bundle_custom_days: Optional[list] = field(default_factory=list)
    bundle_credentials: Optional[list] = field(default_factory=list)
    bundle_calendars: Optional[list] = field(default_factory=list)
    bundle_business_services: Optional[list] = field(default_factory=list)
    bundle_applications: Optional[list] = field(default_factory=list)
    bundle_agent_clusters: Optional[list] = field(default_factory=list)
    visibleTo: Optional[str] = field(default=None)

    @classmethod
    def get_class_name(cls):
        return "bundle"

    @classmethod
    def get_endpoint(cls, method: Optional[str] = None):
        if method == "list":
            return f"{cls.endpoint}/list"
        elif method == "report":
            return f"{cls.endpoint}/report"
        else:
            return cls.endpoint

    def set_name(self, name: str) -> None:
        self.name = name
        self.definition["name"] = self.name

    def set_bundle_task(self, bundle_task_name: str) -> None:
        self.bundle_tasks.append({"name": bundle_task_name})
        self.definition["bundleTasks"] = self.bundle_tasks

    def set_bundle_trigger(self, bundle_trigger_name: str) -> None:
        self.bundle_triggers.append({"name": bundle_trigger_name})
        self.definition["bundleTriggers"] = self.bundle_triggers

    def set_follow_references(self, follow_ref: bool) -> None:
        self.followReferences = follow_ref
        self.definition["followReferences"] = self.followReferences

    def set_promote_by_bussiness_service(self, promote_bus_ser: list) -> None:
        self.promoteByBusinessServices = promote_bus_ser
        self.definition["promoteByBusinessServices"] = self.promoteByBusinessServices

    def set_visible_to(self, user: str) -> None:
        self.definition["visibleTo"] = user

    @classmethod
    def set_filters(
        cls, bundle_name=None, business_services=None, default_promotion_target=None
    ) -> Union[dict, None]:
        filters = {}
        filters["bundlename"] = bundle_name
        filters["businessServices"] = business_services
        filters["defaultPromotionTarget"] = default_promotion_target

        return super().set_query_params(filters)

    @classmethod
    def get_name_query_param(cls):
        return "bundlename"

    def get_delete_paylaod(self) -> dict:
        return {"bundlename": self.name}
