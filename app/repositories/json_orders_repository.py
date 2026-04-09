import asyncio
import json
from pathlib import Path

from pydantic import ValidationError

from app.core.errors import DataValidationError
from app.schemas.order import OrderRecord


class JsonOrdersRepository:
    def __init__(self, path: Path):
        self._path = path

    async def get_orders(self) -> list[OrderRecord]:
        if not self._path.exists():
            return []
        try:
            raw_text = await asyncio.to_thread(self._path.read_text, encoding="utf-8")
            payload = json.loads(raw_text)
        except (OSError, json.JSONDecodeError) as exc:
            raise DataValidationError("Unable to read orders fixture.") from exc

        if not isinstance(payload, list):
            raise DataValidationError("Orders fixture must be a list.")

        result: list[OrderRecord] = []
        for item in payload:
            try:
                result.append(OrderRecord.model_validate(item))
            except ValidationError as exc:
                raise DataValidationError("Orders fixture contains invalid record.") from exc
        return result
