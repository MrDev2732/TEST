class DomainError(Exception):
    """Base exception for business/domain errors."""


class DuplicateEmail(DomainError):
    """Raised when trying to use an email that already exists."""


class InvalidForeignKey(DomainError):
    """Raised when a foreign-key reference is invalid."""


class DuplicateResource(DomainError):
    """Raised when a unique value duplicates an existing record."""
