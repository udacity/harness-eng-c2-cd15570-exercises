"""Timing wrapper for live Responses API clients."""

import time
from typing import Any


class TimedResponses:
    """Preserve the normal Responses API while recording elapsed call time."""

    def __init__(self, responses: Any, timings: dict[str, float]) -> None:
        self._responses = responses
        self._timings = timings

    def create(self, **kwargs: Any) -> Any:
        started = time.perf_counter()
        response = self._responses.create(**kwargs)
        self._timings[str(response.id)] = time.perf_counter() - started
        return response


class TimedClient:
    """Client adapter that adds measurements without changing loop calls."""

    def __init__(self, client: Any) -> None:
        self.response_seconds: dict[str, float] = {}
        self.responses = TimedResponses(client.responses, self.response_seconds)
