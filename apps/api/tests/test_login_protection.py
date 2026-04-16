from fastapi import HTTPException

from app.core.login_protection import LoginProtection, LoginProtectionConfig


class FakeClock:
    def __init__(self):
        self.now = 1_000.0
        self.sleeps: list[float] = []

    def time(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_blocks_after_failed_attempts_and_unlocks(monkeypatch):
    clock = FakeClock()
    monkeypatch.setattr("app.core.login_protection.time.time", clock.time)
    monkeypatch.setattr("app.core.login_protection.time.sleep", clock.sleep)

    protection = LoginProtection(
        LoginProtectionConfig(
            max_failed_attempts=3,
            base_lock_seconds=30,
            max_lock_seconds=60,
            lock_window_seconds=300,
            incremental_delay_seconds=0.1,
            max_delay_seconds=1.0,
        )
    )
    ip = "203.0.113.20"
    email = "User@Example.com"

    for _ in range(3):
        protection.evaluate_and_delay(ip, email)
        protection.register_result(ip, email, success=False)

    try:
        protection.evaluate_and_delay(ip, email)
        assert False, "Expected a temporary lock after repeated failures"
    except HTTPException as exc:
        assert exc.status_code == 429
        assert "Retry" in exc.detail

    clock.advance(31)
    protection.evaluate_and_delay(ip, email)
    protection.register_result(ip, email, success=True)

    metrics = protection.get_metrics()
    assert metrics["blocked_emails_count"] == 0
    assert metrics["blocked_ips_count"] == 0


def test_incremental_delay_and_normalized_email(monkeypatch):
    clock = FakeClock()
    monkeypatch.setattr("app.core.login_protection.time.time", clock.time)
    monkeypatch.setattr("app.core.login_protection.time.sleep", clock.sleep)

    protection = LoginProtection(
        LoginProtectionConfig(
            max_failed_attempts=10,
            incremental_delay_seconds=0.5,
            max_delay_seconds=2.0,
            metrics_window_seconds=60,
            abuse_attempts_per_minute_threshold=5,
        )
    )
    ip = "198.51.100.10"

    protection.evaluate_and_delay(ip, "admin@example.com")
    protection.register_result(ip, "admin@example.com", success=False)

    protection.evaluate_and_delay(ip, "ADMIN@example.com")
    protection.register_result(ip, "ADMIN@example.com", success=False)

    protection.evaluate_and_delay(ip, "Admin@example.com")
    protection.register_result(ip, "Admin@example.com", success=False)

    assert clock.sleeps[0] == 0.5
    assert clock.sleeps[1] == 1.0

    metrics = protection.get_metrics()
    assert metrics["attempts_per_minute_by_email"]["admin@example.com"] == 3
