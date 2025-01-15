from enum import Enum

from client.uc.resources import (
    AgentCluster,
    Bundle,
    BusinessService,
    Calendar,
    Credential,
    CustomDay,
    DbConnection,
    EmailConnection,
    EmailTemplate,
    OAuthClient,
    PeopleSoftConnection,
    SapConnection,
    Script,
    SnmpManager,
    Task,
    Trigger,
    UnvEventTemplate,
    UnvTemplate,
    Variable,
    VirtualResource,
    Workflow,
)


class UCTypeClass(Enum):
    WORKFLOW = Workflow
    TASK = Task
    TRIGGER = Trigger
    VARIABLE = Variable
    VIRTUAL = VirtualResource
    BUNDLE = Bundle
    BUSINESS_SERVICE = BusinessService
    AGENT_CLUSTER = AgentCluster
    CALENDAR = Calendar
    CUSTOM_DAYS = CustomDay
    DB_CONNECTION = DbConnection
    EMAIL_CONNECTION = EmailConnection
    EMAIL_TEMPLATE = EmailTemplate
    PEOPLESOFT_CONNECTION = PeopleSoftConnection
    SAP_CONNECTION = SapConnection
    SNMP_MANAGER = SnmpManager
    SCRIPT = Script
    CREDENTIALS = Credential
    OAUTH_CLIENT = OAuthClient
    UNV_TEMPLATE = UnvTemplate
    UNV_EVENT_TEMPLATE = UnvEventTemplate

    @classmethod
    def get_unique_members(cls):
        # Depending on the usage of this Enum, WORKFLOW type could be covered from TASK's features.
        return [
            member.value for member in UCTypeClass if member != UCTypeClass.WORKFLOW
        ]


class UcTypes(str, Enum):
    TRIGGER = "trigger"
    TASK = "task"
    VIRTUAL_RESOURCE = "virtualresource"
    VARIABLE = "variable"
    AGENT_CLUSTER = "agentcluster"
    BUSINESS_SERVICE = "businessservice"
    CALENDAR = "calendar"
    DB_CONNECTION = "databaseconnection"
    EMAIL_CONNECTION = "emailconnection"
    PEOPLESOFT_CONNECTION = "peoplesoftconnection"
    SAP_CONNECTION = "sapconnection"
    SNMP_MANAGER = "snmpmanager"
    CUSTOM_DAY = "customday"
    EMAIL_TEMPLATE = "emailtemplate"
    SCRIPT = "script"
    BUNDLE = "bundle"
    WORKFLOW = "workflow"
    CREDENTIAL = "credential"
    CREDENTIALS = "credentials"
    UNV_TEMPLATE = "universaltemplate"
    UNV_EVENT_TEMPLATE = "universaleventtemplate"
    OAUTH_CLIENT = "oauthclient"


class UcSubtypes(str, Enum):
    UNIX = "unix"
    WORKFLOW = "workflow"
    WINDOWS_AGENT_CLUSTER = "windowsagentcluster"
    UNIX_AGENT_CLUSTER = "unixagentcluster"
    OUTGOING_EMAIL_CONNECTION = "outgoing"
    INCOMING_EMAIL_CONNECTION = "incoming"


class UCBundleKeys(str, Enum):
    AGENT_CLUSTER = "bundleAgentClusters"
    APPLICATION = "bundleApplications"
    BUSINESS_SERVICE = "bundleBusinessServices"
    CALENDAR = "bundleCalendars"
    CREDENTIAL = "bundleCredentials"
    CUSTOM_DAY = "bundleCustomDays"
    DATABASE_CONNECTION = "bundleDatabaseConnections"
    EMAIL_CONNECTION = "bundleEmailConnections"
    PEOPLESOFT_CONNECTION = "bundlePeoplesoftConnections"
    SAP_CONNECTION = "bundleSapConnections"
    SCRIPTS = "bundleScripts"
    SNMP_MANAGER = "bundleSnmpManagers"
    EMAIL_TEMPLATE = "bundleEmailTemplates"
    TASK = "bundleTasks"
    TRIGGER = "bundleTriggers"
    EVENT_TEMPLATE = "bundleUniversalEventTemplates"
    UNIVERSAL_TEMPLATE = "bundleUniversalTemplates"
    VARIABLE = "bundleVariables"
    VIRTUAL_RESOURCE = "bundleVirtualResources"


RESOURCE_SUPPORTS_GLOB = {Bundle, Task, Trigger, Variable, VirtualResource, Workflow}
