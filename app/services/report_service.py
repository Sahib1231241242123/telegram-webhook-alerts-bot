from collections import defaultdict
from datetime import UTC, datetime, timedelta

from app.repositories.interfaces import OrdersRepository
from app.schemas.report import FullReport, TopSkuItem, WindowReport


class ReportService:
    def __init__(self, orders_repo: OrdersRepository):
        self._orders_repo = orders_repo

    async def build_report(self) -> FullReport:
        orders = await self._orders_repo.get_orders()
        now = datetime.now(UTC)
        day_start = now - timedelta(days=1)
        week_start = now - timedelta(days=7)

        day_orders = [order for order in orders if order.created_at >= day_start]
        week_orders = [order for order in orders if order.created_at >= week_start]

        return FullReport(
            day=self._aggregate(day_orders),
            week=self._aggregate(week_orders),
        )

    @staticmethod
    def _aggregate(orders) -> WindowReport:
        sku_revenue: dict[str, float] = defaultdict(float)
        revenue = 0.0
        margin = 0.0
        for order in orders:
            revenue += order.revenue
            margin += order.margin
            sku_revenue[order.sku] += order.revenue

        sorted_sku = sorted(sku_revenue.items(), key=lambda item: item[1], reverse=True)[:3]
        top_sku = [TopSkuItem(sku=sku, revenue=value) for sku, value in sorted_sku]

        return WindowReport(
            revenue=round(revenue, 2),
            orders_count=len(orders),
            margin=round(margin, 2),
            top_sku=top_sku,
        )

    @staticmethod
    def format_report(report: FullReport, language: str = "ru") -> str:
        def sku_lines(items: list[TopSkuItem]) -> str:
            if not items:
                return "— no data" if language == "en" else "— нет данных"
            return "\n".join(
                [
                    f"{index}. {item.sku}: {item.revenue:.2f}"
                    for index, item in enumerate(items, start=1)
                ]
            )

        if language == "en":
            return (
                "📊 Report\n\n"
                "Day:\n"
                f"• Revenue: {report.day.revenue:.2f}\n"
                f"• Orders: {report.day.orders_count}\n"
                f"• Margin: {report.day.margin:.2f}\n"
                f"• Top-3 SKU:\n{sku_lines(report.day.top_sku)}\n\n"
                "Week:\n"
                f"• Revenue: {report.week.revenue:.2f}\n"
                f"• Orders: {report.week.orders_count}\n"
                f"• Margin: {report.week.margin:.2f}\n"
                f"• Top-3 SKU:\n{sku_lines(report.week.top_sku)}"
            )

        return (
            "📊 Отчет\n\n"
            "За день:\n"
            f"• Revenue: {report.day.revenue:.2f}\n"
            f"• Orders: {report.day.orders_count}\n"
            f"• Margin: {report.day.margin:.2f}\n"
            f"• Top-3 SKU:\n{sku_lines(report.day.top_sku)}\n\n"
            "За неделю:\n"
            f"• Revenue: {report.week.revenue:.2f}\n"
            f"• Orders: {report.week.orders_count}\n"
            f"• Margin: {report.week.margin:.2f}\n"
            f"• Top-3 SKU:\n{sku_lines(report.week.top_sku)}"
        )
