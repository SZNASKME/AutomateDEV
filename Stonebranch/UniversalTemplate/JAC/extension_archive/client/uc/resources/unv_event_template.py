from dataclasses import dataclass

from client.uc.resources.uc_resource import Template


@dataclass
class UnvEventTemplate(Template):  # pragma: no cover
    endpoint: str = "resources/universaleventtemplate"

    @classmethod
    def get_class_name(cls):
        return "universaleventtemplate"
