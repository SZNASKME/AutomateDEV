from dataclasses import dataclass
from typing import Optional, Union

from client.uc.resources.uc_resource import UCResource


@dataclass
class Task(UCResource):  # pragma: no cover
    endpoint: str = "resources/task"
    description: Optional[str] = None

    @classmethod
    def get_class_name(cls):
        return "task"

    @classmethod
    def get_endpoint(cls, method: Optional[str] = None):
        if method == "list":
            return f"{cls.endpoint}/listadv"
        else:
            return cls.endpoint

    @classmethod
    def set_filters(
        cls,
        task_name: str = None,
        agent_name: str = None,
        business_service: str = None,
        name: str = None,
        template_id: str = None,
        template_name: str = None,
        type: str = None,
        updated_time: str = None,
        updated_time_type: str = None,
        workflow_id: str = None,
        workflow_name: str = None,
    ) -> Union[dict, None]:
        filters = {}
        filters["taskname"] = task_name
        filters["agentName"] = agent_name
        filters["businessServices"] = business_service
        filters["name"] = name
        filters["templateId"] = template_id
        filters["templateName"] = template_name
        filters["type"] = type
        filters["updatedTime"] = updated_time
        filters["updatedTimeType"] = updated_time_type
        filters["workflowid"] = workflow_id
        filters["workflowname"] = workflow_name

        return super().set_query_params(filter_dict=filters)

    @classmethod
    def get_name_query_param(cls):
        return "taskname"

    def get_delete_paylaod(self) -> dict:
        return {"taskname": self.name}


@dataclass
class Workflow(Task):
    subtype = "workflow"

    @classmethod
    def get_class_name(cls):
        return "workflow"

    @classmethod
    def get_endpoint_list(cls):
        return f"{cls.endpoint}/list"
