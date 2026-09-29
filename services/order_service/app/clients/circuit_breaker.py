import asyncio
import time


class CircuitOpenError(Exception):
    pass


class AsyncCircuitBreaker:
    def __init__(self, *, failure_threshold: int = 5, reset_timeout: float = 15.0):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self._state = "closed"
        self._failure_count = 0
        self._opened_at = 0.0
        self._probe_in_progress = False
        self._lock = asyncio.Lock()

    async def allow_request(self) -> bool:
        async with self._lock:
            if self._state == "closed":
                return True
            if self._state == "open":
                if time.monotonic() - self._opened_at < self.reset_timeout:
                    return False
                self._state = "half_open"
            if self._state == "half_open" and not self._probe_in_progress:
                self._probe_in_progress = True
                return True
            return False

    async def record_success(self) -> None:
        async with self._lock:
            self._failure_count = 0
            self._state = "closed"
            self._probe_in_progress = False

    async def record_failure(self) -> None:
        async with self._lock:
            self._probe_in_progress = False
            self._failure_count += 1
            if self._state == "half_open" or self._failure_count >= self.failure_threshold:
                self._state = "open"
                self._opened_at = time.monotonic()

    @property
    def state(self) -> str:
        return self._state
