import pytest
from unittest.mock import Mock
from src.scrapers.manager import ScraperManager
from src.scrapers.base import BaseScraper


class FakeScraper(BaseScraper):
    def __init__(self, http_client=None, config=None):
        super().__init__(http_client, config)
        self.source_name = "Fake"

    def fetch_urls(self):
        return [
            {"url": "https://example.com/1", "title": "浙江农业现代化发展报告"},
            {"url": "https://example.com/2", "title": "全国粮食产量创新高"},
            {"url": "https://example.com/3", "title": "杭州西湖龙井茶产业升级"},
        ]

    def parse_article(self, url):
        return {
            "id": self._generate_id(url),
            "title": "文章标题",
            "url": url,
            "publish_time": "",
            "raw_text": "浙江农业部门积极推进数字化改革，杭州等地成效显著。",
            "fetch_status": "success",
        }


def test_manager_two_level_match():
    """测试两级匹配：标题命中→直接存，标题未命中→正文匹配"""
    sources = [
        {"name": "测试源", "handler": "fake_scraper", "priority": 1, "enabled": True},
    ]
    http_client = Mock()
    http_client.inter_source_delay.return_value = 0.01

    config = {
        "agri_keywords": ["农业 农村 粮食 茶叶"],
        "region_keywords": ["浙江 杭州 宁波 义乌 温州"],
    }

    manager = ScraperManager(sources, http_client, config)
    manager.handler_registry = {"fake_scraper": FakeScraper}
    results, errors = manager.run_all()

    assert len(results) == 1
    articles = results[0]["articles"]
    assert len(articles) == 2  # 1st: title has agri+region; 2nd: title agri only, body has region; 3rd: title agri, body no region

    # Article 1: title has both → direct match
    assert articles[0]["match_type"] == "title"
    # Article 2: title no region, body has region → body match
    assert articles[1]["match_type"] == "body"

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

    manager = ScraperManager(sources, http_client, {})
    manager.handler_registry = {"failing": FailingScraper}
    results, errors = manager.run_all()

    assert len(results) == 0
    assert len(errors) == 1
    assert "Connection refused" in errors[0]["error"]


def test_keyword_parsing():
    """测试 _parse_keywords 正确解析分段格式"""
    manager = ScraperManager([], None)
    kw_list = ["农业 农村 农民", "粮食 乡村振兴"]
    result = manager._parse_keywords(kw_list)
    assert "农业" in result
    assert "农村" in result
    assert "农民" in result
    assert "粮食" in result
    assert "乡村振兴" in result
