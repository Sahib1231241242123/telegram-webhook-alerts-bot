from abc import ABC, abstractmethod

from app.schemas.alert import AlertRecord
from app.schemas.order import OrderRecord


class OrdersRepository(ABC):
    @abstractmethod
    async def get_orders(self) -> list[OrderRecord]:
        raise NotImplementedError


class AlertsRepository(ABC):
    @abstractmethod
    async def get_alerts(self) -> list[AlertRecord]:
        raise NotImplementedError
