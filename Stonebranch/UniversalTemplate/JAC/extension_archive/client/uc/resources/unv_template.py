from dataclasses import dataclass

from client.uc.resources.uc_resource import Template


@dataclass
class UnvTemplate(Template):  # pragma: no cover
    endpoint: str = "resources/universaltemplate"

    @classmethod
    def get_class_name(cls):
        return "universaltemplate"
