import copy
import json
import re
import secrets
from typing import Optional

from client.uc.enums.enums import RESOURCE_SUPPORTS_GLOB, UCBundleKeys, UCTypeClass
from client.uc.exceptions.exceptions import (
    HTTPError,
    HttpUcClientException,
    HttpUcServerException,
    ListTaskFailed,
    UcClientException,
)
from client.uc.httpUcClient import HttpRestClient
from client.uc.resources import UCResource
from client.uc.resources.bundle import Bundle
from client.uc.utils.utils import (
    GlobalConfig,
    flatten_list,
    get_unique_classes,
    initialize_uc_objects,
    normalize_response,
    set_dependency_order,
    set_query_param_dict,
)
from logger import logger


class UCClient:

    LIST_RESOURCE = "list"
    BUNDLE_REPORT = "report"
    ALL_UC_TYPES = UCTypeClass.get_unique_members()
    cancel_request = False

    def __init__(
        self,
        url: str,
        user: str = None,
        password: str = None,
        token: str = None,
        verify: bool = True,
    ) -> None:

        self.url = url
        self.user = user
        self.password = password
        self.token = token
        self.log_level = "INFO"
        self.verify = verify

        self.http_rest_client = HttpRestClient(
            self.url,
            self.user,
            self.password,
            self.token,
            self.log_level,
            self.verify,
        )
        self.logger = self.http_rest_client.logger
        self._authenticate()

    def _authenticate(self) -> None:  # pragma: no cover
        """Authenticate provided credentials against UC"""
        try:
            self.http_rest_client.get(uc_resource="resources/status")
        except HTTPError as e:
            self._raise_uc_client_exception(e.response.status_code, e)

    def cancel_operation(self):
        """
        Serves the functionality to cancel a CRUID operation in the client.
        Can be called outside the client when an extension is cancelled.
        """
        self.cancel_request = True

    def get_definitions(
        self,
        types: Optional[list] = None,
        filter_query: Optional[dict] = None,
        name: Optional[str] = None,
        dependencies: bool = False,
    ) -> list:
        """
        List and retrieve UC Objects definitions.
        Examples:
        get_definitions()
        get_definitions(types=[Task,Calendar])
        get_definitions(types=[Task], name="task")
        get_definitions(types=[Trigger], filter_query=Trigger.set_filter(enabled=True))
        get_definitions(types=[Trigger], name="my trigger", dependencies=True)
        get_definitions(types=[Workflow], name="my wf", dependencies=True)
        get_definitions(types=[BusinessService], name="my BS", dependencies=True)
        """

        definitions = []
        if dependencies:
            definitions = self._get_definitions_with_dependencies(types[0], name)
            return definitions

        types = self.ALL_UC_TYPES if not types else get_unique_classes(copy.copy(types))
        config = GlobalConfig()
        use_list_endpoint = getattr(config, "use_list_endpoint", False)

        for uc_type_class in types:

            query_param = (
                set_query_param_dict(uc_type_class, name) if name else filter_query
            )

            endpoint = (
                uc_type_class.get_endpoint()
                if query_param and use_list_endpoint is False
                else uc_type_class.get_endpoint(method=self.LIST_RESOURCE)
            )

            try:
                # if executing the `selection_name` dynamic choice command with
                # the value of Workflow use a different endpoint (/list)
                # instead of (/listadv) to retrieve workflow names
                if getattr(config, "dynamic_choice_workflow_selection", False) is True:
                    response = self.http_rest_client.post(
                        uc_type_class.get_endpoint_list(), {}
                    )
                else:
                    res_supports_glob = uc_type_class in RESOURCE_SUPPORTS_GLOB
                    logger.debug(
                        f"Current uc_type_class={uc_type_class} (glob: {res_supports_glob})"
                    )

                    if use_list_endpoint and not res_supports_glob:
                        query_param = None

                    response = self.http_rest_client.get(endpoint, query_param)
                definitions_response = normalize_response(response)

                uc_objs = initialize_uc_objects(
                    definitions_response, uc_type_class.get_class_name()
                )

                logger.debug(f"({uc_type_class}) UC OBJECTS: {uc_objs}")

                definitions.append(uc_objs)

            except HTTPError as e:
                # [Redmine: #32982] Workaround due to API /task/listadv limitation
                if e.response.status_code == 500:
                    error_pattern = re.compile(
                        r"List task failed. Could not find [a-z]+[\s[a-z]+]* with id \w{32}"
                    )
                    if len(error_pattern.findall(e.response.text)) != 0:
                        self.logger.error(f"Listing of UC definitions failed...")
                        self.logger.error(e.response.text)
                        raise ListTaskFailed(e.response.text) from e
                    else:
                        self._raise_uc_client_exception(e.response.status_code, e)
                # catch the cases when some endpoints returning 404, when other return []
                if e.response.status_code != 404:
                    self._raise_uc_client_exception(e.response.status_code, e)
        return flatten_list(definitions)

    def create_definitions(
        self, uc_objects: list, ignore_errors: bool = False
    ) -> Optional[tuple]:
        """
        Create a list of new UC objects.

        :param list uc_serialized_items: The list of UCObjectDefinitionSerializer,
        containing valid definition that should be used as payload.

        :return list: A list with all created UC objects.
        """

        self.logger.debug("Start creating new UC objects...")
        sorted_uc_objects = set_dependency_order(uc_objects, method="create")
        created_objects = []
        errors = {}

        for uc_object in sorted_uc_objects:
            if self.cancel_request:
                return created_objects, errors
            try:
                self.http_rest_client.post(uc_object.endpoint, uc_object.definition)
                created_objects.append(uc_object)
            except HTTPError as e:
                if not ignore_errors:
                    self._raise_uc_client_exception(e.response.status_code, e)
                else:
                    errors[uc_object.name] = (e.response.text, uc_object)
        if errors:
            self.logger.warning("Creation of UC definitions completed with errors...")
            self.logger.warning(errors)
        return created_objects, errors

    def update_definitions(
        self, uc_objects: list, ignore_errors: bool = False
    ) -> Optional[tuple]:
        """
        Update a list of new UC objects.

        :param list uc_serialized_items: The list of UCObjectDefinitionSerializer,
        containing valid definition that should be used as payload.

        :return list: A list with all updated UC objects.
        """

        self.logger.debug("Start updating new UC objects...")
        sorted_uc_objects = set_dependency_order(uc_objects, method="update")
        updated_objects = []
        errors = {}

        for uc_object in sorted_uc_objects:
            try:
                if self.cancel_request:
                    return updated_objects, errors
                self.http_rest_client.put(uc_object.endpoint, uc_object.definition)
                updated_objects.append(uc_object)
            except HTTPError as e:
                if not ignore_errors:
                    self._raise_uc_client_exception(e.response.status_code, e)
                else:
                    errors[uc_object.name] = (e.response.text, uc_object)

        if errors:
            self.logger.warning("Update of UC definitions completed with errors...")
            self.logger.warning(errors)
        return updated_objects, errors

    def delete_definitions(
        self, uc_objects: list, ignore_errors: bool = False
    ) -> Optional[tuple]:
        """
        Delete a list of UC objects.

        :param list uc_serialized_items: The list of UCObjectDefinitionSerializer,
        containing valid definition that should be used as payload.

        :return list: A list with all deleted UC objects.
        """
        self.logger.debug("Start deleting existing UC objects...")
        sorted_uc_objects = set_dependency_order(uc_objects, method="delete")
        deleted_objects = []
        errors = {}

        for uc_object in sorted_uc_objects:
            try:
                if self.cancel_request:
                    return deleted_objects, errors
                self.http_rest_client.delete(
                    uc_object.endpoint, uc_object.get_delete_paylaod()
                )
                deleted_objects.append(uc_object)
            except HTTPError as e:
                if not ignore_errors:
                    self._raise_uc_client_exception(e.response.status_code, e)
                else:
                    errors[uc_object.name] = (e.response.text, uc_object)

        if errors:
            self.logger.warning("Deletion of UC definitions completed with errors...")
            self.logger.warning(errors)
        return deleted_objects, errors

    def run_report(self, bundle_name: str) -> Bundle:
        """
        Run report for the given Bundle.

        :param str bundle_name: The name of the Bundle.
        :return Bundle: A Bundle object with the report contents.
        """
        try:
            resource = Bundle.get_endpoint(method="report")
            response = self.http_rest_client.get(resource, {"bundlename": bundle_name})
            report = json.loads(response.text)
            return Bundle(name=bundle_name, definition=report)
        except HTTPError as e:
            self._raise_uc_client_exception(e.response.status_code, e)

    def get_bundle_report_contents(self, report: dict) -> list:
        """
        Returns all UC Objects from a Bundle Report.

        :param dict report: The bundle report dictionary.
        :return list: The list of UC definitions as UC Objects.
        """
        uc_definitions = []
        bundle_keys = [member.value for member in UCBundleKeys]

        for bundle_key in bundle_keys:
            bundled_items_list = report[bundle_key]
            if bundled_items_list:
                uc_type = bundle_key[6:-1].lower()
                uc_definitions.append(
                    initialize_uc_objects(bundled_items_list, uc_type)
                )
        # Flatten the uc_definitions list:
        # [[Task(), Task()], [Trigger(), Trigger()]]  ---> [Task(), Task(), Trigger(), Trigger()]
        return flatten_list(uc_definitions)

    def _get_definitions_with_dependencies(
        self,
        uc_type_class: list,
        uc_item_name: str,
    ) -> Optional[list]:
        """
        Retrieves a UC definition by name and all its dependent UC definitions.
        Example:
        - For a workflow: brings the workflow definition, and all its children definitions
        - For a business service: brings the business service definition, and all the member definitions
        - For a trigger: brings the trigger definition, and all its referenced definitions.

        :param str types: A UC type class for which to retrieve the dependencies.
        Valid values are: workflow, trigger, businessservice
        :param str uc_item_name: the name of the UC item to retrieve dependencies for.

        :return list: List of dependent UC Objects.
        """
        if not uc_item_name:
            raise UcClientException(
                "Define the name of the UC object for which to fetch dependencies."
            )
        definitions = self._get_bundled_definitions(uc_type_class, uc_item_name)
        return definitions

    def _get_bundled_definitions(
        self, bundled_item_type: UCTypeClass, bundled_item_name: str
    ) -> list:
        """
        For a given UC item, create a bundle, run the report
        and retrieve the report contents as UC Objects.

        :param str bundled_item_type: The UC type of the item to retrieve its definitions
        :param str bundled_item_name: The UC item's name, for which to retrieve definitions through a bundle
        """

        bundle = self._create_bundle(bundled_item_type, bundled_item_name)

        try:
            report = self.run_report(bundle.name)
            report_definitions = self.get_bundle_report_contents(report.definition)
            final_definitions = []
            for definition in report_definitions:
                final_definitions.append(
                    self.get_definitions(types=[type(definition)], name=definition.name)
                )

        except (HttpUcServerException, HttpUcClientException) as e:
            self.http_rest_client.delete(Bundle.endpoint, {"bundlename": bundle.name})
            self._raise_uc_client_exception(e.response.response.status_code, e)
        except AttributeError as e:
            logger.error(f"Error when constructing report definitions: {e}")

        try:
            self.http_rest_client.delete(Bundle.endpoint, {"bundlename": bundle.name})
        except HTTPError as e:
            self._raise_uc_client_exception(e.response.status_code, e)

        return flatten_list(final_definitions)

    def _create_bundle(
        self, bundled_item_type: UCTypeClass, bundled_item_name: str
    ) -> Bundle:
        """
        Helper function to create a temporary bundle.
        """
        # generate a random integer between 1 and 10000 to be set as suffix to bundle name
        random_number = secrets.randbelow(10000) + 1

        bundle = Bundle()
        bundle.set_name(
            name=f"uc_client_temp_bundle_for_{bundled_item_name}_{random_number}"
        )
        if bundled_item_type == UCTypeClass.WORKFLOW.value:
            bundle.set_bundle_task(bundled_item_name)
            bundle.set_follow_references(True)
        elif bundled_item_type == UCTypeClass.TRIGGER.value:
            bundle.set_bundle_trigger(bundled_item_name)
            bundle.set_follow_references(True)
        elif bundled_item_type == UCTypeClass.BUSINESS_SERVICE.value:
            bundle.set_promote_by_bussiness_service([bundled_item_name])
            bundle.set_visible_to(self.user)
        try:
            self.http_rest_client.post(bundle.endpoint, bundle.definition)
            return bundle
        except HTTPError as e:
            self._raise_uc_client_exception(e.response.status_code, e)

    def _raise_uc_client_exception(self, status_code: int, e: HTTPError):
        if 400 <= status_code <= 499:
            raise HttpUcClientException(status_code=status_code, response=e)
        if 500 <= status_code <= 599:
            raise HttpUcServerException(status_code=status_code, response=e)

    def _uc_object_exists(self, uc_object: UCResource):
        defs = self.get_definitions(types=[type(uc_object)], name=uc_object.name)
        return True if defs else False
