import time

import httpx

from .anti_detect import build_headers, random_delay
from ..exceptions import FetchError


class HttpClient:
    def __init__(self, config):
        cfg = config.get("scraper", {})
        self.timeout = cfg.get("timeout", 15)
        self.retry_max = cfg.get("retry_max", 2)
        self.retry_delay = cfg.get("retry_delay", 10)
        self.delay_min = cfg.get("delay_min", 2)
        self.delay_max = cfg.get("delay_max", 5)

    def fetch(self, url, referer=None):
        last_error = None
        for attempt in range(self.retry_max + 1):
            try:
                headers = build_headers(referer=referer)
                with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                    response = client.get(url, headers=headers)
                    response.raise_for_status()
                    if response.charset_encoding:
                        response.encoding = response.charset_encoding
                    else:
                        response.encoding = 'utf-8'
                    return response.text
            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code == 429:
                    if attempt < self.retry_max:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    raise FetchError(f"Rate limited: {url}") from e
                if e.response.status_code >= 500:
                    if attempt < self.retry_max:
                        time.sleep(self.retry_delay)
                        continue
                raise FetchError(f"HTTP {e.response.status_code} for {url}") from e
            except (httpx.RequestError, httpx.TimeoutException) as e:
                last_error = e
                if attempt < self.retry_max:
                    time.sleep(self.retry_delay)
                    continue
        raise FetchError(f"Failed to fetch {url} after {self.retry_max} retries") from last_error

    def inter_source_delay(self):
        return random_delay(self.delay_min, self.delay_max)
