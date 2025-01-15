import itertools
import json
from typing import List, Optional

from requests import Response

from client.uc.enums.enums import UcSubtypes, UcTypes
from client.uc.resources import Task, UCResource, Workflow
from client.uc.utils.mapping import (
    SUBTYPE_MAPPER,
    TYPE_CLASS_MAPPER,
    UC_DELETE_DEPENDENCY_ORDER,
)
from logger import logger

METHOD_LIST = "list"
METHOD_FILTER = "filter"


class GlobalConfig:
    _instance = None

    def __new__(cls, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        for k, v in kwargs.items():
            setattr(cls, k, v)

        return cls._instance

    def __repr__(self) -> str:
        args = ", ".join(
            f"{a}={getattr(self, a)}" for a in dir(self) if not a.startswith("_")
        )
        return f"{self.__class__.__name__}({args})"


def get_unique_classes(types_list: list) -> list:
    if Workflow in types_list and Task in types_list:
        types_list.remove(Workflow)
    return types_list


def normalize_response(response: Response) -> list:
    """
    Helper function to normalize all responses from UC as lists
    """
    json_response = json.loads(response.text)
    response = json_response if isinstance(json_response, list) else [json_response]
    return response


def initialize_uc_objects(uc_definitions: List[dict], uc_type: str) -> List[UCResource]:
    """
    Takes a list of UC definitions as dictionaries and
    creates the corresponding UCResource oject types.

    :param list uc_definitions: The list of dictionaries with UC definitions
    :return list: List of UCResources objects
    """
    uc_objects = []
    for definition in uc_definitions:
        utype, usubtype = get_type_from_definition(definition, uc_type)
        if uc_type == UcTypes.WORKFLOW.value and not is_workflow(definition):
            continue
        uc_type_class = TYPE_CLASS_MAPPER.get(utype)
        uname = get_name_from_definition(definition, utype)

        # If usubtype retrieved from definition is None, use the subtype set on the class.
        if usubtype:
            uc_object = uc_type_class(
                name=uname, subtype=usubtype, definition=definition
            )
        else:
            uc_object = uc_type_class(name=uname, definition=definition)

        # Redmine: #32265 - Map the subtype in a human readable form
        mapped_subtype = SUBTYPE_MAPPER.get(uc_object.subtype)
        uc_object.subtype = mapped_subtype if mapped_subtype else uc_object.subtype
        uc_objects.append(uc_object)

    return uc_objects


def is_workflow(definition: dict):
    """
    Identifies if a Task definition is a Workflow Task.
    Used to initialize appropriately a Workflow object.

    :param dict definition: The UC definition.
    """
    try:
        if UcTypes.WORKFLOW.value in definition.get("type").lower():
            return True
        return False
    except AttributeError:
        return False


def get_name_from_definition(definition: dict, utype: str) -> str:
    """
    Retrieves a UC object's name from the definition payload.
    """
    try:
        name = definition["name"]
    except KeyError as exception:
        if utype == UcTypes.EMAIL_TEMPLATE.value:
            name = definition["templateName"]
        elif utype == UcTypes.SCRIPT:
            name = definition["scriptName"]
        else:
            raise exception
    return name


def get_type_from_definition(definition: dict, uc_type: str = None) -> tuple:
    """
    Evaluate the type of the given UC definition and return the mapped type,subtype.
    For example: A `Universal` task is a subtype of `Task`, thus the tuple should be (task,universal).

    :param dict uc_item: The UC item's definition.
    :return tuple: The (task,subtype) of the UC item.
    """

    uc_type, uc_subtype = extract_type_subtype_from_definition(definition, uc_type)
    # Evaluate special cases
    uc_type, uc_subtype = extract_task_type(uc_type, uc_subtype, definition)
    uc_type, uc_subtype = extract_trigger_type(uc_type=uc_type, uc_subtype=uc_subtype)
    uc_type, uc_subtype = extract_email_connection_type(uc_type, uc_subtype)

    return (uc_type, uc_subtype)


def extract_email_connection_type(uc_type: str, uc_subtype: str) -> Optional[tuple]:
    """
    Helper function to set connection type from definition payload.
    """
    if uc_type in (
        UcSubtypes.OUTGOING_EMAIL_CONNECTION,
        UcSubtypes.INCOMING_EMAIL_CONNECTION,
    ):
        uc_type = UcTypes.EMAIL_CONNECTION.value
        uc_subtype = uc_type

    return uc_type, uc_subtype


def extract_task_type(
    uc_type: str, uc_subtype: str, definition: dict
) -> Optional[tuple]:
    """
    Helper function to get the task type and subtype from UC definition payload.

    Example A - definition is coming from simple definition listing:
    Input: uc_type=taskFileTransfer, uc_subtype=taskfiletransfer
    Output: uc_tupe=task, uc_subtype=filetransfer

    Example B - definition is coming from bundled definition
    Input: uc_type=task, uc_subtype=file transfer
    Output: uc_tupe=task, uc_subtype=filetransfer

    Example C - definition is workflow
    Input: uc_type=taskWorkflow, uc_subtype=taskWorkflow
    Output: uc_tupe=workflow, uc_subtype=None

    Example D - definition is universal task
    Input: uc_type=taskUniversal, uc_subtype=taskUniversal
    Output: uc_tupe=task, uc_subtype=<Universal Template Name>
    """

    if uc_type.startswith("task"):
        uc_subtype = (
            uc_subtype[4:].lower()
            # subtype from task definition payload
            if uc_subtype.startswith("task")
            # subtype from bundle definition
            else uc_subtype.replace(" ", "")
        )
        uc_type = "task"

    # handle workflows as Workflow object instead of Task object
    if uc_subtype == UcTypes.WORKFLOW.value:
        uc_type = UcTypes.WORKFLOW.value
        uc_subtype = None

    return uc_type, uc_subtype


def extract_trigger_type(uc_type: str, uc_subtype: Optional[str]) -> Optional[tuple]:
    """
    Helper function to get the trigger type and subtype from UC definition payload.

    Example A - definition if coming from a simple definition list
    Input:  uc_type=triggertm, uc_subtype=triggertm
    Output: uc_type=trigger, uc_subtype=tm

    Example B - definition if coming from bundled definition
    Input:  uc_type=trigger, uc_subtype=tm
    Output: uc_type=trigger, uc_subtype=tm

    """

    if uc_type.startswith("trigger"):
        # definitions coming from simple definition listing: "triggertm"
        uc_subtype = (
            uc_subtype[7:].lower()
            # subtype from definition listing
            if uc_subtype.startswith("trigger")
            # subtype from bundled definition
            else uc_subtype.replace(" ", "")
        )
        uc_type = "trigger"
    return uc_type, uc_subtype


def extract_type_subtype_from_definition(
    definition: dict, uc_type: str = None
) -> tuple:
    """
    When uc_type is not provided:
        Try retrieve uc object's type from definition field 'type'.
        If definition has not field 'type', retrieve the information from field `exportTable`
    When uc_type is known and provided,
        The subtype should get retreived from definition's field `type`
        This is to cover cases like bundle report: bundleTasks: {"type": "universal"}
        If no `type` exists in the definition payload, this means that the UC item has no subtype.
    """

    if not uc_type:
        try:
            uc_type = definition.get("type").lower()
        except AttributeError:
            uc_type = definition.get("exportTable")[4:].replace("_", "")
            subtype = None
    else:
        try:
            subtype = definition.get("type").lower()
        except AttributeError:
            try:
                subtype = definition.get("scriptType").lower()
            except AttributeError:
                subtype = None

    return uc_type, subtype


def flatten_list(nested_list: list) -> list:
    """
    Helper function to flatten a list of lists and also remove duplicate objects if any:
    Example:
    [[Task(), Task()], [Trigger(), Trigger()]]  ---> [Task(), Task(), Trigger(), Trigger()]
    """
    return list(itertools.chain(*nested_list))


def set_query_param_dict(uc_type: UCResource, uc_name: Optional[str]) -> dict:
    """
    Helper function to contruct a dictionary of query params, to feed in REST API.
    """
    filter_key = uc_type.get_name_query_param()
    filter_query = {filter_key: uc_name}
    return filter_query


def set_dependency_order(uc_objects: list, method: str):
    """
    Helper function to sort the given UC objects according to the dependency list,
    that should be observed during CRUD commands.
    """
    if method in ("create", "update"):
        dependency_order = list(reversed(UC_DELETE_DEPENDENCY_ORDER))
    else:
        dependency_order = UC_DELETE_DEPENDENCY_ORDER
    sorted_uc_objects = sorted(
        uc_objects, key=lambda x: dependency_order.index(x.get_class_name())
    )
    return sorted_uc_objects
