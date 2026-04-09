from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.core.errors import DataValidationError

MAX_CALLBACK_DATA_LEN = 64


class CallbackAction(StrEnum):
    CONFIRM = "confirm"
    REJECT = "reject"
    DETAILS = "details"
    BACK = "back"
    SET_LANG = "setlang"


class CallbackPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str = Field(default="v1", pattern=r"^v1$")
    action: CallbackAction
    alert_id: str = Field(min_length=1, max_length=40)

    def pack(self) -> str:
        data = f"{self.version}|{self.action.value}|{self.alert_id}"
        if len(data) > MAX_CALLBACK_DATA_LEN:
            raise DataValidationError("callback_data exceeds Telegram limit.")
        return data

    @classmethod
    def unpack(cls, raw: str) -> "CallbackPayload":
        if not raw or len(raw) > MAX_CALLBACK_DATA_LEN:
            raise DataValidationError("callback_data has invalid length.")
        parts = raw.split("|")
        if len(parts) != 3:
            raise DataValidationError("callback_data has invalid format.")
        try:
            return cls(version=parts[0], action=parts[1], alert_id=parts[2])
        except ValidationError as exc:
            raise DataValidationError("callback_data failed validation.") from exc
