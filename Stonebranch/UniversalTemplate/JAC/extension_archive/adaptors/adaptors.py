from typing import Union

from serializers import ExtensionInputSerializer, UaCDynamicChoiceSerializer


class ActionAdaptors:
    @staticmethod
    def list_uac_definitions_input_adaptor(
        self,
        serialized_input_data: Union[
            ExtensionInputSerializer, UaCDynamicChoiceSerializer
        ],
    ) -> dict:
        """
        Adaptor responsible for transforming extension input data and pass them as ListUacAction input

        :param ExtensionInputSerializer input_data: The extension input serialized data.
        """
        return serialized_input_data.dict()

    @staticmethod
    def export_to_git_repository_adaptor(
        self, serialized_input_data: ExtensionInputSerializer
    ) -> dict:
        """
        Adaptor responsible for transforming extension input data and pass them as ExportToGitRepositoryAction input

        :param ExtensionInputSerializer input_data: The extension input serialized data.
        """
        return serialized_input_data.dict()

    @staticmethod
    def import_uac_definitions_input_adaptor(
        self,
        serialized_input_data: ExtensionInputSerializer,
    ) -> dict:
        """
        Adaptor responsible for transforming extension input data and pass them as ImportUacAction input

        :param ExtensionInputSerializer input_data: The extension input serialized data.
        """
        return serialized_input_data.dict()
