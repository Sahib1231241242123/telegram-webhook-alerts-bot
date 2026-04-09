import pytest

from app.core.errors import DataValidationError
from app.schemas.callbacks import CallbackAction, CallbackPayload


def test_callback_pack_unpack_roundtrip() -> None:
    payload = CallbackPayload(action=CallbackAction.DETAILS, alert_id="AL-1")
    packed = payload.pack()
    unpacked = CallbackPayload.unpack(packed)
    assert unpacked.action == CallbackAction.DETAILS
    assert unpacked.alert_id == "AL-1"


def test_callback_rejects_invalid_data() -> None:
    with pytest.raises(DataValidationError):
        CallbackPayload.unpack("v1|unknown|AL-1")
