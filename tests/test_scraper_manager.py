import pytest
from unittest.mock import Mock, patch
from src.scrapers.manager import ScraperManager
from src.scrapers.base import BaseScraper


class FakeScraper(BaseScraper):
    def __init__(self, http_client=None, config=None):
        super().__init__(http_client, config)
        self.source_name = "Fake"
        self._fail = False

    def fetch_urls(self):
        if self._fail:
            raise Exception("Boom")
        return ["https://example.com/1"]

    def parse_article(self, url):
        return {
            "id": self._generate_id(url),
            "title": "Fake Title",
            "url": url,
            "publish_time": "2026-05-29",
            "raw_text": "Fake body text.",
            "fetch_status": "success"
        }


def test_manager_scrapes_enabled_sources():
    sources = [
        {"name": "测试源", "handler": "fake_scraper", "priority": 1, "enabled": True},
        {"name": "禁用源", "handler": "disabled", "priority": 1, "enabled": False},
    ]
    http_client = Mock()
    http_client.inter_source_delay.return_value = 0.01

    manager = ScraperManager(sources, http_client)
    manager.handler_registry = {"fake_scraper": FakeScraper}
    results, errors = manager.run_all()

    assert len(results) == 1
    assert results[0]["source"] == "测试源"
    assert len(results[0]["articles"]) == 1
    assert len(errors) == 0


def test_manager_handles_failure():
    sources = [
        {"name": "失败源", "handler": "failing", "priority": 1, "enabled": True},
    ]
    http_client = Mock()
    http_client.inter_source_delay.return_value = 0.01

    class FailingScraper(BaseScraper):
        source_name = "失败源"
        def fetch_urls(self):
            raise Exception("Connection refused")
        def parse_article(self, url):
            return {}

    manager = ScraperManager(sources, http_client)
    manager.handler_registry = {"failing": FailingScraper}
    results, errors = manager.run_all()

    assert len(results) == 0
    assert len(errors) == 1
    assert errors[0]["source"] == "失败源"
    assert "Connection refused" in errors[0]["error"]
