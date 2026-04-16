from sqlalchemy.exc import IntegrityError

from app.core.exceptions import DuplicateEmail, DuplicateResource, InvalidForeignKey


def map_integrity_error(error: IntegrityError) -> Exception:
    message = str(error.orig).lower() if error.orig else str(error).lower()

    if "email" in message and ("unique" in message or "duplicate" in message):
        return DuplicateEmail("Email already exists")

    if "foreign key" in message or "violates foreign key constraint" in message:
        return InvalidForeignKey("Invalid related resource reference")

    if "unique" in message or "duplicate" in message:
        return DuplicateResource("Duplicate resource")

    return error
