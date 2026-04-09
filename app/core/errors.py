class DomainError(Exception):
    """Base exception for domain-layer errors."""


class DataValidationError(DomainError):
    """Raised when fixture data is invalid."""


class NotFoundError(DomainError):
    """Raised when requested entity is not found."""


class RateLimitError(DomainError):
    """Raised when user exceeds request limits."""
