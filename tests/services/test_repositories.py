from pathlib import Path

import pytest

from app.core.errors import DataValidationError
from app.repositories.json_alerts_repository import JsonAlertsRepository


@pytest.mark.asyncio
async def test_alerts_repository_reads_valid_fixture(tmp_path: Path) -> None:
    path = tmp_path / "alerts.json"
    path.write_text(
        '[{"id":"A-1","title":"T","severity":"high","status":"active","reasoning":"R","expected_impact":"I"}]',
        encoding="utf-8",
    )
    repo = JsonAlertsRepository(path)
    items = await repo.get_alerts()
    assert len(items) == 1
    assert items[0].id == "A-1"


@pytest.mark.asyncio
async def test_alerts_repository_raises_on_malformed_json(tmp_path: Path) -> None:
    path = tmp_path / "alerts.json"
    path.write_text("{", encoding="utf-8")
    repo = JsonAlertsRepository(path)
    with pytest.raises(DataValidationError):
        await repo.get_alerts()
