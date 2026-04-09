from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from app.core.errors import DataValidationError
from app.repositories.json_orders_repository import JsonOrdersRepository
from app.schemas.order import OrderRecord
from app.services.report_service import ReportService


class OrdersRepoStub:
    def __init__(self, orders: list[OrderRecord]):
        self._orders = orders

    async def get_orders(self) -> list[OrderRecord]:
        return self._orders


@pytest.mark.asyncio
async def test_report_service_aggregates_day_and_week() -> None:
    now = datetime.now(UTC)
    orders = [
        OrderRecord(
            order_id="1",
            sku="SKU-A",
            revenue=100.0,
            margin=20.0,
            created_at=now - timedelta(hours=3),
        ),
        OrderRecord(
            order_id="2",
            sku="SKU-A",
            revenue=50.0,
            margin=10.0,
            created_at=now - timedelta(days=3),
        ),
        OrderRecord(
            order_id="3",
            sku="SKU-B",
            revenue=200.0,
            margin=70.0,
            created_at=now - timedelta(days=10),
        ),
    ]

    service = ReportService(OrdersRepoStub(orders))
    report = await service.build_report()
    assert report.day.revenue == 100.0
    assert report.day.orders_count == 1
    assert report.week.revenue == 150.0
    assert report.week.orders_count == 2
    assert report.week.top_sku[0].sku == "SKU-A"


@pytest.mark.asyncio
async def test_report_service_handles_empty_dataset() -> None:
    service = ReportService(OrdersRepoStub([]))
    report = await service.build_report()
    assert report.day.orders_count == 0
    assert report.week.orders_count == 0
    assert report.day.top_sku == []
    assert "нет данных" in service.format_report(report)


@pytest.mark.asyncio
async def test_orders_repository_raises_for_invalid_fixture(tmp_path: Path) -> None:
    path = tmp_path / "orders.json"
    path.write_text('[{"order_id":"1"}]', encoding="utf-8")
    repo = JsonOrdersRepository(path)
    with pytest.raises(DataValidationError):
        await repo.get_orders()
