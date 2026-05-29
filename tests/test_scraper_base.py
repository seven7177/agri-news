import pytest
from src.scrapers.base import BaseScraper
from src.scrapers.exceptions import FetchError, ParseError


class DummyScraper(BaseScraper):
    """测试用爬虫，不实际请求网络"""
    def __init__(self, http_client=None, config=None):
        super().__init__(http_client, config)
        self._test_html = ""
        self._test_articles = []

    def fetch_urls(self):
        if self._test_html == "fetch_error":
            raise FetchError("模拟抓取失败")
        if self._test_html == "parse_error":
            return ["https://example.com/bad"]
        return ["https://example.com/news/1", "https://example.com/news/2"]

    def parse_article(self, url):
        if url == "https://example.com/bad":
            raise ParseError("模拟解析失败")
        return {
            "id": "test1234",
            "title": f"测试标题: {url}",
            "url": url,
            "publish_time": "2026-05-29",
            "raw_text": "测试正文",
            "fetch_status": "success"
        }


def test_base_scraper_name():
    scraper = DummyScraper()
    scraper.source_name = "测试源"
    assert scraper.source_name == "测试源"


def test_fetch_urls_returns_list():
    scraper = DummyScraper()
    urls = scraper.fetch_urls()
    assert len(urls) == 2


def test_parse_article_returns_dict():
    scraper = DummyScraper()
    result = scraper.parse_article("https://example.com/news/1")
    assert result["title"] is not None
    assert result["url"] is not None
    assert result["raw_text"] is not None


def test_fetch_urls_raises_fetch_error():
    scraper = DummyScraper()
    scraper._test_html = "fetch_error"
    with pytest.raises(FetchError):
        scraper.fetch_urls()


def test_parse_article_raises_parse_error():
    scraper = DummyScraper()
    scraper._test_html = "parse_error"
    urls = scraper.fetch_urls()
    with pytest.raises(ParseError):
        scraper.parse_article(urls[0])
