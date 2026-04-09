import asyncio
import json
from pathlib import Path

from pydantic import ValidationError

from app.core.errors import DataValidationError
from app.schemas.alert import AlertRecord


class JsonAlertsRepository:
    def __init__(self, path: Path):
        self._path = path

    async def get_alerts(self) -> list[AlertRecord]:
        if not self._path.exists():
            return []
        try:
            raw_text = await asyncio.to_thread(self._path.read_text, encoding="utf-8")
            payload = json.loads(raw_text)
        except (OSError, json.JSONDecodeError) as exc:
            raise DataValidationError("Unable to read alerts fixture.") from exc

        if not isinstance(payload, list):
            raise DataValidationError("Alerts fixture must be a list.")

        result: list[AlertRecord] = []
        for item in payload:
            try:
                result.append(AlertRecord.model_validate(item))
            except ValidationError as exc:
                raise DataValidationError("Alerts fixture contains invalid record.") from exc
        return result
