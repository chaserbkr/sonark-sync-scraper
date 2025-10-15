from __future__ import annotations
import time, random
from typing import Optional, Dict
import requests
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Rotate a few very common desktop UAs to avoid easy blocks
UA_LIST = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
]

DEFAULT_HEADERS = {
    "User-Agent": random.choice(UA_LIST),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Reuse one session to keep cookies and connection alive
_session = requests.Session()
_session.headers.update(DEFAULT_HEADERS)

class RateLimiter:
    def __init__(self, min_interval: float = 1.2):
        self.min_interval = min_interval
        self._last = 0.0
    def wait(self):
        delta = time.time() - self._last
        if delta < self.min_interval:
            time.sleep(self.min_interval - delta + random.uniform(0, 0.3))
        self._last = time.time()

@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type((requests.RequestException,))
)
def get(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 25) -> requests.Response:
    # small jitter + occasional UA rotate if we just got blocked
    hdrs = _session.headers.copy()
    if headers:
        hdrs.update(headers)
    logger.debug(f"GET {url}")
    resp = _session.get(url, headers=hdrs, timeout=timeout)
    if resp.status_code == 403:
        # rotate UA and retry once immediately
        _session.headers["User-Agent"] = random.choice(UA_LIST)
        time.sleep(random.uniform(1.0, 2.0))
        resp = _session.get(url, headers=hdrs, timeout=timeout)
    resp.raise_for_status()
    return resp
