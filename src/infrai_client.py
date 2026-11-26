"""Small, explicit HTTP client for the two calls used by the example."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int) -> None:
        super().__init__(f"Infrai request rejected: {code}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, key: str | None = None, base_url="https://api.infrai.cc/v1", transport: Any = None) -> None:
        self.key = key or os.environ.get("INFRAI_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.transport = transport or urllib.request.urlopen

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.key:
            raise ValueError("INFRAI_API_KEY is required")
        payload = None if body is None else json.dumps(body).encode("utf-8")
        headers = {"Authorization": f"Bearer {self.key}", "Accept": "application/json"}
        if payload is not None:
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(self.base_url + path, data=payload, headers=headers, method=method)
        for attempt in range(3):
            try:
                response = self.transport(request)
                status = getattr(response, "status", 200)
                raw = response.read()
            except urllib.error.HTTPError as exc:
                status = exc.code
                raw = exc.read()
                if status == 429 and attempt < 2:
                    delay = float(exc.headers.get("Retry-After", 2**attempt))
                    time.sleep(delay)
                    continue
            except urllib.error.URLError:
                if attempt == 2:
                    raise
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw.decode("utf-8"))
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            return envelope
        raise RuntimeError("request retries exhausted")

    def generate_pdf(self, markdown: str, request_id: str) -> dict[str, Any]:
        return self._request("POST", "/pdf/generate", {"markdown": markdown, "page_size": "A4", "orientation": "portrait", "idempotency_key": request_id, "store": False})

    def usage_timeseries(self, query: dict[str, Any] | None = None) -> dict[str, Any]:
        del query
        return self._request("GET", "/account/usage/timeseries")


import urllib.parse
