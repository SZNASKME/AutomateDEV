from dataclasses import dataclass

from client.uc.resources.uc_resource import Template


@dataclass
class EmailTemplate(Template):  # pragma: no cover
    endpoint: str = "resources/emailtemplate"

    @classmethod
    def get_class_name(cls):
        return "emailtemplate"
