from enum import Enum

from client.uc.resources import Credential, OAuthClient, UnvEventTemplate, UnvTemplate


class ActionsEnum(Enum):
    LIST_UAC_DEFINITIONS = "List UAC Definitions"
    EXPORT_GIT = "Export to Git Repository"
    IMPORT_UAC_DEFINITIONS = "Import from Git Repository"


class SelectionMethodEnum(Enum):
    BUNDLE = "bundle"
    DEFINITION_NAME = "definition_name"
    DEFINITION_NAME_GLOB = "definition_name_glob"
    BUSINESS_SERVICE = "businessservice"
    WORKFLOW = "workflow"
    TRIGGER = "trigger"


class GitServiceProviderEnum(str, Enum):
    GITLAB = "GitLab"
    GITHUB = "GitHub"
    BITBUCKET = "BitBucket"
    AZURE = "Azure DevOps"


class GitFileFormat(str, Enum):
    YAML = "Yaml"
    JSON = "Json"


class ProxyTypeEnum(str, Enum):
    NONE = "-- None --"
    HTTP = "HTTP"
    HTTPS = "HTTPS"
    HTTPS_CREDENTIALS = "HTTPS With Credentials"


class ExcludedDefinitions(str, Enum):
    CREDENTIAL = Credential.get_class_name()
    OAUTH_CLIENT = OAuthClient.get_class_name()
    UNV_TEMPLATE = UnvTemplate.get_class_name()
    UNV_EVENT_TEMPLATE = UnvEventTemplate.get_class_name()
    # application is a task subtype
    APPLICATION = "application"


class FeatureFlags(str, Enum):
    FF_DISABLE_COMMIT_PREFIX = "UE_FF_DISABLE_DEFAULT_COMMIT_PREFIX"
