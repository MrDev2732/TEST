import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass

from fastapi import HTTPException, status


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LoginProtectionConfig:
    lock_window_seconds: int = 15 * 60
    max_failed_attempts: int = 5
    base_lock_seconds: int = 60
    max_lock_seconds: int = 15 * 60
    incremental_delay_seconds: float = 0.2
    max_delay_seconds: float = 2.0
    metrics_window_seconds: int = 60
    abuse_attempts_per_minute_threshold: int = 30


class LoginProtection:
    def __init__(self, config: LoginProtectionConfig | None = None):
        self.config = config or LoginProtectionConfig()
        self._lock = threading.Lock()
        self._failed_ip: dict[str, deque[float]] = defaultdict(deque)
        self._failed_email: dict[str, deque[float]] = defaultdict(deque)
        self._events_ip: dict[str, deque[tuple[float, bool]]] = defaultdict(deque)
        self._events_email: dict[str, deque[tuple[float, bool]]] = defaultdict(deque)
        self._blocked_until_ip: dict[str, float] = {}
        self._blocked_until_email: dict[str, float] = {}

    @staticmethod
    def normalize_email(email: str) -> str:
        return email.strip().lower()

    def evaluate_and_delay(self, ip: str, email: str) -> None:
        now = time.time()
        normalized_email = self.normalize_email(email)
        delay_seconds = 0.0

        with self._lock:
            self._cleanup(now, ip, normalized_email)
            blocked_until = max(
                self._blocked_until_ip.get(ip, 0.0),
                self._blocked_until_email.get(normalized_email, 0.0),
            )
            if blocked_until > now:
                retry_after = int(blocked_until - now)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many login attempts. Retry in {retry_after}s.",
                )

            recent_failures = max(
                len(self._failed_ip[ip]),
                len(self._failed_email[normalized_email]),
            )
            delay_seconds = min(
                recent_failures * self.config.incremental_delay_seconds,
                self.config.max_delay_seconds,
            )

        if delay_seconds > 0:
            time.sleep(delay_seconds)

    def register_result(self, ip: str, email: str, success: bool) -> None:
        now = time.time()
        normalized_email = self.normalize_email(email)

        with self._lock:
            self._cleanup(now, ip, normalized_email)
            self._events_ip[ip].append((now, success))
            self._events_email[normalized_email].append((now, success))
            self._emit_abuse_alerts(now, ip, normalized_email)

            if success:
                self._failed_ip[ip].clear()
                self._failed_email[normalized_email].clear()
                self._blocked_until_ip.pop(ip, None)
                self._blocked_until_email.pop(normalized_email, None)
                return

            self._failed_ip[ip].append(now)
            self._failed_email[normalized_email].append(now)
            self._apply_block_if_needed(now, ip, normalized_email)

    def get_metrics(self) -> dict:
        now = time.time()
        with self._lock:
            self._cleanup_all(now)
            ip_attempts = {
                ip: len(events)
                for ip, events in self._events_ip.items()
                if len(events) > 0
            }
            email_attempts = {
                email: len(events)
                for email, events in self._events_email.items()
                if len(events) > 0
            }
            blocked_ips = [ip for ip, until in self._blocked_until_ip.items() if until > now]
            blocked_emails = [email for email, until in self._blocked_until_email.items() if until > now]

        return {
            "attempts_per_minute_by_ip": ip_attempts,
            "attempts_per_minute_by_email": email_attempts,
            "blocked_ips_count": len(blocked_ips),
            "blocked_emails_count": len(blocked_emails),
        }

    def _emit_abuse_alerts(self, now: float, ip: str, email: str) -> None:
        threshold = self.config.abuse_attempts_per_minute_threshold
        ip_count = len(self._events_ip[ip])
        email_count = len(self._events_email[email])
        if ip_count >= threshold:
            logger.warning("Abuse alert: high login attempts for IP %s (%s/min)", ip, ip_count)
        if email_count >= threshold:
            logger.warning("Abuse alert: high login attempts for email %s (%s/min)", email, email_count)

    def _apply_block_if_needed(self, now: float, ip: str, email: str) -> None:
        max_failures = self.config.max_failed_attempts
        failure_count = max(len(self._failed_ip[ip]), len(self._failed_email[email]))
        if failure_count < max_failures:
            return

        over_limit = failure_count - max_failures + 1
        duration = min(
            self.config.base_lock_seconds * (2 ** (over_limit - 1)),
            self.config.max_lock_seconds,
        )
        blocked_until = now + duration
        self._blocked_until_ip[ip] = blocked_until
        self._blocked_until_email[email] = blocked_until

    def _cleanup(self, now: float, ip: str, email: str) -> None:
        self._trim_failures(now, self._failed_ip[ip])
        self._trim_failures(now, self._failed_email[email])
        self._trim_events(now, self._events_ip[ip])
        self._trim_events(now, self._events_email[email])
        if self._blocked_until_ip.get(ip, 0) <= now:
            self._blocked_until_ip.pop(ip, None)
        if self._blocked_until_email.get(email, 0) <= now:
            self._blocked_until_email.pop(email, None)

    def _cleanup_all(self, now: float) -> None:
        for bucket in self._failed_ip.values():
            self._trim_failures(now, bucket)
        for bucket in self._failed_email.values():
            self._trim_failures(now, bucket)
        for bucket in self._events_ip.values():
            self._trim_events(now, bucket)
        for bucket in self._events_email.values():
            self._trim_events(now, bucket)
        self._blocked_until_ip = {
            key: value for key, value in self._blocked_until_ip.items() if value > now
        }
        self._blocked_until_email = {
            key: value for key, value in self._blocked_until_email.items() if value > now
        }

    def _trim_failures(self, now: float, bucket: deque[float]) -> None:
        cutoff = now - self.config.lock_window_seconds
        while bucket and bucket[0] < cutoff:
            bucket.popleft()

    def _trim_events(self, now: float, bucket: deque[tuple[float, bool]]) -> None:
        cutoff = now - self.config.metrics_window_seconds
        while bucket and bucket[0][0] < cutoff:
            bucket.popleft()


login_protection = LoginProtection()
