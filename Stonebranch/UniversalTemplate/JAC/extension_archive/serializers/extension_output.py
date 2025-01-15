from typing import Optional

from pydantic import BaseModel, validator

from serializers.extension_input import ExtensionInputSerializer
from settings import EXTENSION_NAME, EXTENSION_VERSION


class ExtensionInputToRepresentationSerializer(ExtensionInputSerializer):
    @validator(
        "credentials_username", "credentials_password", pre=True, check_fields=False
    )
    def hide_password(cls, value: str) -> Optional[str]:
        return "****" if value else None


class InvocationSerializer(BaseModel):
    extension: str = EXTENSION_NAME
    version: str = EXTENSION_VERSION
    fields: ExtensionInputToRepresentationSerializer


class ExtensionOutputSerializer(BaseModel):
    exit_code: int = 0
    status_description: str = "..."
    status: str = "SUCCESS"
    invocation: InvocationSerializer
    result: dict


class ExtensionStatusSerializer(BaseModel):
    extension_status: str = "Finished"
