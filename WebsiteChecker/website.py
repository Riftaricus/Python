import requests
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional


@dataclass
class PingResult:
    status_code: Optional[int]
    reason: str
    elapsed: Optional[timedelta]
    ok: bool
    error: Optional[str] = None

    @property
    def failed(self) -> bool:
        return self.error is not None


class Website:
    def __init__(self, url: str, timeout: int = 10):
        if not (url.startswith("https://") or url.startswith("http://")):
            url = f"https://{url}"
        self.url = url
        self.timeout = timeout
        self._last_result: Optional[PingResult] = None

    @property
    def status_code(self) -> Optional[int]:
        return self._last_result.status_code if self._last_result else None

    @property
    def speed(self) -> Optional[timedelta]:
        return self._last_result.elapsed if self._last_result else None

    @property
    def reason(self) -> Optional[str]:
        return self._last_result.reason if self._last_result else None

    @property
    def is_up(self) -> Optional[bool]:
        return self._last_result.ok if self._last_result else None

    def ping(self) -> PingResult:
        """Ping the website. Returns a PingResult — never raises."""
        try:
            response = requests.get(self.url, timeout=self.timeout)
            self._last_result = PingResult(
                status_code=response.status_code,
                reason=response.reason,
                elapsed=response.elapsed,
                ok=response.ok,
            )
        except requests.exceptions.ConnectionError:
            self._last_result = PingResult(
                status_code=None,
                reason="Connection failed",
                elapsed=None,
                ok=False,
                error="Could not connect (DNS failure or refused)",
            )
        except requests.exceptions.Timeout:
            self._last_result = PingResult(
                status_code=None,
                reason="Timed out",
                elapsed=None,
                ok=False,
                error=f"No response within {self.timeout}s",
            )
        except requests.exceptions.RequestException as e:
            self._last_result = PingResult(
                status_code=None,
                reason="Request failed",
                elapsed=None,
                ok=False,
                error=str(e),
            )
        return self._last_result

    def ping_average(self, n: int = 3) -> Optional[timedelta]:
        """Ping n times and return the average response time, or None if all failed."""
        results = [self.ping() for _ in range(n)]
        times = [r.elapsed for r in results if r.elapsed is not None]
        return sum(times, timedelta()) / len(times) if times else None

    def __repr__(self) -> str:
        return f"Website(url={self.url!r}, status={self.status_code}, up={self.is_up})"