from dataclasses import dataclass

from app.services.alerts_service import AlertsService
from app.services.message_sanitizer import MessageSanitizer
from app.services.rate_limiter import RateLimiter
from app.services.report_service import ReportService


@dataclass(slots=True)
class AppContainer:
    report_service: ReportService
    alerts_service: AlertsService
    rate_limiter: RateLimiter
    message_sanitizer: MessageSanitizer
