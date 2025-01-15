import fnmatch
import re
from typing import Union

from tabulate import tabulate

from actions.base import BaseAction, create_output_definitions
from adaptors.adaptors import ActionAdaptors
from client.client_communication_handler import ClientCommunicationHandler
from client.uc.enums.enums import UCTypeClass, UcTypes
from client.uc.exceptions import ListTaskFailed
from client.uc.resources import (
    Credential,
    OAuthClient,
    Task,
    UnvEventTemplate,
    UnvTemplate,
    Workflow,
)
from client.uc.utils.mapping import TYPE_CLASS_MAPPER
from client.uc.utils.utils import GlobalConfig
from enums import SelectionMethodEnum
from logger import logger
from serializers import (
    ExtensionInputSerializer,
    ListUacActionInputSerializer,
    ListUacActionOutputSerializer,
)
from serializers.extension_input import (
    ExtensionInputSerializer,
    UaCDynamicChoiceSerializer,
)


class ListUacDefinitionsAction(BaseAction):
    """
    Class responsible for executing the List UAC Definitions action.

    """

    available_definitions = create_output_definitions()

    not_supported_uc_types = [OAuthClient, UnvTemplate, UnvEventTemplate, Credential]
    input_adapter = ActionAdaptors.list_uac_definitions_input_adaptor
    input_serializer = ListUacActionInputSerializer
    output_serializer = ListUacActionOutputSerializer

    def __init__(
        self, action_input: Union[ExtensionInputSerializer, UaCDynamicChoiceSerializer]
    ):
        super().__init__(action_input)
        self.selection_method = self.action_input_serialized.selection_method
        self.selection_name = (
            self.action_input_serialized.selection_name
            if self.action_input_serialized.selection_name
            else None
        )
        self._set_included_excluded_types(
            self.action_input_serialized.selection_exclude_list
        )
        self.handler = self._init_client_communication_handler()

    def _init_client_communication_handler(self):
        client = ClientCommunicationHandler(self.action_input)
        client.set_uc_client()
        return client

    def execute(self) -> dict:

        logger.info("Listing UAC definitions.")
        try:
            definitions = self.fetch_definitions()
        except ListTaskFailed as e:
            # [Redmine: #32982] Workaround due to API /task/listadv limitation
            output_dict = {"definitions_selected": {}, "errors": [e.error_message]}
            return output_dict

        logger.info("Listing completed. Constructing result table.")

        table_data = self.construct_result_table_data(definitions)

        print(tabulate(table_data, headers="keys", tablefmt="rst"))

        result = self._count_selected_definitions(definitions)
        output_dict = {}
        output_dict["definitions_selected"] = result
        return output_dict

    def fetch_definitions(self) -> list:
        """
        Fetch definitions of type and name equal to the selected extension input

        :return list: The result of the available UC definitions with the specified parameters.
        """

        if self.selection_method == SelectionMethodEnum.DEFINITION_NAME_GLOB.value:
            name = "" if self.selection_name is None else self.selection_name

            GlobalConfig(use_list_endpoint=True)

            result = self.handler.get_uc_definitions(
                uc_definitions_types=self.included_types, name=name
            )

            result = [o for o in result if fnmatch.fnmatch(o.name, name)]

        elif self.selection_method == SelectionMethodEnum.DEFINITION_NAME.value:
            if self.selection_name == "*" or self.selection_name == ".*":
                result = self.handler.get_uc_definitions(
                    uc_definitions_types=self.included_types
                )
            else:
                total_definitions = self.handler.get_uc_definitions(
                    uc_definitions_types=self.included_types
                )
                result = self._filter_definitions_with_name_regex(
                    total_definitions, self.selection_name
                )
        elif self.selection_method == SelectionMethodEnum.BUNDLE.value:
            bundle = self.handler.uc_client.run_report(self.selection_name)
            report_contents = self.handler.uc_client.get_bundle_report_contents(
                bundle.definition
            )
            # add the actual bundle definition in the finals results
            report_contents.append(bundle)
            result = []
            for definition in report_contents:
                full_uc_definition = self.handler.get_uc_definitions(
                    uc_definitions_types=[type(definition)], name=definition.name
                )
                result += full_uc_definition

        elif self.selection_method in [
            SelectionMethodEnum.BUSINESS_SERVICE.value,
            SelectionMethodEnum.WORKFLOW.value,
            SelectionMethodEnum.TRIGGER.value,
        ]:
            definition_class = TYPE_CLASS_MAPPER.get(self.selection_method)
            result = self.handler.uc_client.get_definitions(
                types=[definition_class], name=self.selection_name, dependencies=True
            )
        result = self._filter_excluded_definitions(result)

        return result

    def fetch_definitions_by_type(self, definition_type: str) -> list:
        """
        Fetch UC definitions with a dynamically selected definition type.

        :param str definition_type: The UC definition type to be retrieved.
        :return list: The list of all available definitions included to the specified type
        """
        if definition_type != SelectionMethodEnum.DEFINITION_NAME.value:
            definition_class = TYPE_CLASS_MAPPER.get(definition_type)
            result = self.handler.get_uc_definitions(
                uc_definitions_types=[definition_class]
            )
            return result
        else:
            raise ValueError(
                "For Selection Method `Definition Name (Regex)`, provide either a UC definition name or * or .* in `Selection Name`"
            )

    @staticmethod
    def _filter_definitions_with_name_regex(
        total_definitions: list, name_regex: str
    ) -> list:
        """
        Determine which UC definitions name match a certain string.

        :param list total_definitions: The input list of definitions to be filtered.
        :param str name_regex: The name pattern to be matched
        :return list: The filtered list
        """

        pattern = re.compile(rf"{name_regex.lower()}")

        filtered_definitions = []
        for definition in total_definitions:
            if (
                pattern.match(definition.name.lower())
                or name_regex.lower() in definition.name.lower()
            ):
                filtered_definitions.append(definition)

        return filtered_definitions

    def _count_selected_definitions(self, definitions: list) -> dict:
        """
        Loop through the response list of definitions and count each UC definitions occurrence.

        :param list definitions: The response list containing the UC definitions
        :return dict: A dictionary that correlates each UC definition with the number that it was present in the response list
        """
        available_definitions = self.available_definitions.copy()
        for definition in definitions:
            uc_type_class = definition.get_class_name()
            definition_name = (
                Task.get_class_name()
                if uc_type_class == Workflow.get_class_name()
                else uc_type_class
            )
            if definition_name in list(available_definitions.keys()):
                counter = available_definitions.get(definition_name)
                counter += 1
                available_definitions[definition_name] = counter

        return available_definitions

    def _set_included_excluded_types(self, exclude_list: list) -> None:
        """
        Set a list of the UC Types to be requested from UC client. The selection is made my excluding Uc types
        that were selected in extension input.

        :param list exclude_list: The list of UC types to be excluded
        """

        available_definitions = [
            member.value
            for member in UCTypeClass
            if member.value not in self.not_supported_uc_types
        ]

        self.excluded_types = (
            [TYPE_CLASS_MAPPER.get(definition_type) for definition_type in exclude_list]
            if exclude_list is not None
            else []
        )
        if exclude_list and "task" in exclude_list:
            self.excluded_types.append(Workflow)

        self.included_types = [
            definition
            for definition in available_definitions
            if definition not in self.excluded_types
        ]

    def _filter_excluded_definitions(self, total_definitions: list) -> list:
        """
        Take a list from UC definitions and remove those that are in the excluded list.

        :return list: The filtered UC definitions
        """
        filtered_definitions = []

        for definition in total_definitions:
            if definition.subtype == "application":
                continue
            if (
                type(definition) not in self.excluded_types
                and type(definition) in self.included_types
            ):
                filtered_definitions.append(definition)

        return filtered_definitions
