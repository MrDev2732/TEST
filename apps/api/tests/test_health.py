import asyncio

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import OperationalError

from app.api.routes.health import health, ready


class _HealthySession:
    def execute(self, _query):
        return 1


class _FailingSession:
    def execute(self, _query):
        raise OperationalError("SELECT 1", {}, Exception("boom"))


def test_health_ok() -> None:
    assert health() == {"status": "ok"}


def test_ready_ok_with_db_query() -> None:
    response = asyncio.run(ready(_HealthySession()))
    assert response == {"status": "ready"}


def test_ready_returns_503_on_db_error() -> None:
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(ready(_FailingSession()))

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "database connection is not ready"
