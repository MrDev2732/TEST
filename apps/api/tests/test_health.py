import pytest
from fastapi import HTTPException
from sqlalchemy.exc import OperationalError

from app.api.routes.health import health, ready


class _Bind:
    class _Dialect:
        name = "postgresql"

    dialect = _Dialect()


class _HealthySession:
    def get_bind(self):
        return _Bind()

    def execute(self, _query, _params=None):
        return 1


class _FailingSession:
    def get_bind(self):
        return _Bind()

    def execute(self, _query, _params=None):
        raise OperationalError("SELECT 1", {}, Exception("boom"))


def test_health_ok() -> None:
    assert health() == {"status": "ok"}


def test_ready_ok_with_db_query() -> None:
    response = ready(_HealthySession())
    assert response == {"status": "ready"}


def test_ready_returns_503_on_db_error() -> None:
    with pytest.raises(HTTPException) as exc_info:
        ready(_FailingSession())

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "database connection is not ready"
