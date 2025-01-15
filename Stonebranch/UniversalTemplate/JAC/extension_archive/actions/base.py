from abc import abstractmethod
from typing import List

import urllib3

from actions.utils import (
    extract_subtype_from_uc_definition,
    get_uc_type_class_str,
    is_integration_definition,
)
from client.uc.resources import Workflow
from client.uc.resources.uc_resource import UCResource
from serializers import (
    ActionOutputSerializer,
    ActionSerializer,
    ExtensionInputSerializer,
)

# Disable urllib3 warnings when making unverified requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from logger import logger


class BaseAction:
    input_adapter = None
    input_serializer = None
    output_serializer = None
    is_extension_cancelled = False

    def __init__(self, action_input: ExtensionInputSerializer):
        self.action_input = action_input
        action_input = self.input_adapter(action_input)
        self.action_input_serialized = self.input_serializer(**action_input)

    def get_result(self) -> ActionOutputSerializer:
        """
        Method to be called in order to get the result of a child Action.

        :return _type_: _description_
        """
        output_data = self.execute()
        out = self.output_serializer(**output_data)
        return out

    def get_input_data(self) -> ActionSerializer:
        """
        Return the serialized action input data

        """
        return self.action_input_serialized

    @abstractmethod
    def execute(self, input_data, output_data):
        pass

    def action_cancel(self):
        logger.info("Extension cancelled. Preparing output...")
        self.is_extension_cancelled = True

    def construct_result_table_data(self, definitions: List[UCResource]) -> List[dict]:
        """
        Create three columns. "Definition Type", "Definition Subtype" and "Definition Name".

        :param List[UCResource] definitions: The list of UC Definitions to be displayed
        :return List[dict]: The table to be printed in list format.
        """
        definition_types = []
        definition_subtypes = []
        definition_names = []

        if not definitions:
            return [
                {
                    "Type": None,
                    "Subtype": None,
                    "Name": None,
                }
            ]

        for definition in definitions:
            # handle special cases of Task types
            if isinstance(definition, Workflow):
                definition_types.append("Tasks")
            elif is_integration_definition(definition):
                definition_types.append("Tasks")
            else:
                uc_type = get_uc_type_class_str(definition)
                definition_types.append(uc_type)

            subtype = extract_subtype_from_uc_definition(definition)
            definition_subtypes.append(
                "-"
            ) if not subtype else definition_subtypes.append(subtype)
            definition_names.append(definition.name)

        data = [
            {
                "Type": definition_type,
                "Subtype": definition_subtype,
                "Name": definition_name,
            }
            for definition_type, definition_subtype, definition_name in zip(
                definition_types, definition_subtypes, definition_names
            )
        ]

        return data


def create_output_definitions() -> dict:
    """
    Return a dictionary with all available definitions that will be displayed in extension output with each
    counter set to zero.

    """
    return {
        "agentcluster": 0,
        "businessservice": 0,
        "bundle": 0,
        "calendar": 0,
        "databaseconnection": 0,
        "emailconnection": 0,
        "peoplesoftconnection": 0,
        "sapconnection": 0,
        "snmpmanager": 0,
        "customday": 0,
        "emailtemplate": 0,
        "script": 0,
        "task": 0,
        "trigger": 0,
        "variable": 0,
        "virtualresource": 0,
    }
