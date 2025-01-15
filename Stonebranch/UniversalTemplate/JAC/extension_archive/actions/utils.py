from typing import Optional, Tuple

from client.uc import resources
from logger import logger

UAC_FILE_PREFIX = "ops_"
LEN_UAC_PREFIX = len(UAC_FILE_PREFIX)
UAC_UUID = 34
EMAIL_CONNECTION_TYPE = "Email Connection"
WORKFLOW_TYPE = "Workflow"


def extract_subtype_from_uc_definition(uc_definition: resources.UCResource) -> str:
    """
    Custom logic for extracting UC subtypes to be added to git files

    :param UCResource uc_definition: The UCResource object
    """
    # handle special cases of Tasks
    if is_integration_definition(uc_definition):
        subtype = uc_definition.definition.get("template")
    elif isinstance(uc_definition, resources.Workflow):
        subtype = WORKFLOW_TYPE
    # for email connections don't use Outgoing/Incoming as subtypes.
    elif isinstance(uc_definition, resources.EmailConnection):
        subtype = EMAIL_CONNECTION_TYPE
    else:
        subtype = uc_definition.subtype
    logger.debug(
        f"Definition with name {uc_definition.name} of {type(uc_definition)} with definition {uc_definition.definition} is {subtype}"
    )

    return subtype


def get_uc_type(filepath: str) -> Optional[resources.UCResource]:
    """_Maps the given git filepath to one on the UC resources class_

    :param str filepath: _The absolute git filepath_
    :raises ValueError: _When the given filepath does not match any of the expected folders_
    :return resources.UCResource: _UC Resource class_
    """
    if "Workflow/" in filepath:
        return FOLDERS_RESOURCE_CLASSES_MAPPER.get("Workflows/")
    for git_folder_name, uc_type_class in FOLDERS_RESOURCE_CLASSES_MAPPER.items():
        if git_folder_name in filepath:
            return uc_type_class


def extract_folder_subfolder_from_uc_resource(
    uc_definition: resources.UCResource,
) -> Tuple[str, str]:
    """
    Custom logic for extracting UC type and subtype to be added to git files

    :param UCResource uc_resource: The UCResource object
    """
    folder_name = None
    subfolder_name = None
    # handle special cases of Tasks
    if is_integration_definition(uc_definition):
        folder_name = "Integrations"
        subfolder_name = uc_definition.definition.get("template")
        return folder_name, subfolder_name

    if isinstance(uc_definition, resources.Workflow):
        folder_name = "Tasks"
        subfolder_name = WORKFLOW_TYPE
        return folder_name, subfolder_name

    # use as subfolder the Email Connection rather the Outgoing/Incoming
    if isinstance(uc_definition, resources.EmailConnection):
        subfolder_name = EMAIL_CONNECTION_TYPE
    else:
        subfolder_name = uc_definition.subtype

    folder_name = get_uc_type_class_str(uc_definition)
    return folder_name, subfolder_name


def extract_name_subtype_from_filepath(git_file_path: str) -> Tuple[str, str]:
    """_ Extract the name and subtype -if any - from a Git file Path.
    Subtype is mapped back to its original UC definition format.

    For example from the following strings:
    string1 = "Tasks/Timer/Sleep 90.yaml"
    name =  'Sleep 90'
    subtype = 'sleep'

    string2 = "Bundles/test-name.json"
    name =  'test-name.json'
    subtype = 'bundle'

    :param str git_file_path: The git file path to extract the definitions name from
    :return str: The definition name extracted.
    """
    definition_name = None
    subtype = None
    subfolder = None

    git_file_path_splitted = git_file_path.split("/")
    if not git_file_path_splitted:
        logger.warning(f"Invalid filepath: {git_file_path}")
        return definition_name, subtype

    filename = git_file_path_splitted[-1].split(".")
    if not filename:
        logger.warning(
            f"Cannot extract definition name from the given filepath: {git_file_path}"
        )
        return definition_name, subtype

    definition_name = filename[0]
    try:
        # "Tasks/Timer/Sleep 90.yaml" -> "Timer"
        # Variables/my_var.yaml -> Variables
        subfolder = git_file_path_splitted[-2]
        subfolder = (
            None
            if f"{subfolder}/" in FOLDERS_RESOURCE_CLASSES_MAPPER.keys()
            else subfolder
        )
    except IndexError:
        logger.warning(
            f"Cannot extract subfolder from the given filepath: {git_file_path}"
        )

    return definition_name, subfolder


def is_integration_definition(definition: resources.UCResource) -> bool:
    """Checks if the given UC resource object, is an Integration Task

    :param resources.UCResource definition: _The UC resource object_
    :return bool: _True is if given UC resource object is Integration task,
    and False if it is not._
    """
    if definition.subtype == "Universal" and definition.definition.get("template"):
        return True
    return False


def get_uc_type_class_str(definition: resources.UCResource) -> str:
    """Returns the str class name of the given UC resource.

    :param resources.UCResource definition: _description_
    :return str: _The UC resource string class name_
    """
    return TYPES_FOLDER_MAPPER.get(definition.get_class_name())


TYPES_FOLDER_MAPPER = {
    "task": "Tasks",
    "workflow": "Workflows",
    "trigger": "Triggers",
    "calendar": "Calendars",
    "customday": "Custom Days",
    "emailtemplate": "Email Templates",
    "script": "Scripts",
    "variable": "Variables",
    "virtualresource": "Virtual Resources",
    "bundle": "Bundles",
    "agentcluster": "Agent Clusters",
    "integrations": "Integrations",
    "databaseconnection": "Connections",
    "emailconnection": "Connections",
    "peoplesoftconnection": "Connections",
    "sapconnection": "Connections",
    "snmpmanager": "Connections",
    "businessservice": "Business Services",
}

FOLDERS_RESOURCE_CLASSES_MAPPER = {
    "Tasks/": resources.Task,
    "Workflows/": resources.Workflow,
    "Triggers/": resources.Trigger,
    "Calendars/": resources.Calendar,
    "Custom Days/": resources.CustomDay,
    "Email Templates/": resources.EmailTemplate,
    "Scripts/": resources.Script,
    "Variables/": resources.Variable,
    "Virtual Resources/": resources.VirtualResource,
    "Bundles/": resources.Bundle,
    "Unix Agent Cluster/": resources.AgentCluster,
    "Windows Agent Cluster/": resources.AgentCluster,
    "Integrations/": resources.Task,
    "Database Connection/": resources.DbConnection,
    "Email Connection/": resources.EmailConnection,
    "Peoplesoft Connection/": resources.PeopleSoftConnection,
    "Sap Connection/": resources.SapConnection,
    "SNMP Manager/": resources.SnmpManager,
    "Business Services/": resources.BusinessService,
}
