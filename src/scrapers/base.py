from abc import ABC, abstractmethod
import hashlib


class BaseScraper(ABC):
    def __init__(self, http_client=None, config=None):
        self.http_client = http_client
        self.config = config or {}
        self.source_name = ""

    def _generate_id(self, url):
        return hashlib.md5(url.encode()).hexdigest()[:8]

    @abstractmethod
    def fetch_urls(self):
        """获取新闻列表 URL，返回 list[str]"""

    @abstractmethod
    def parse_article(self, url):
        """解析单篇文章，返回 dict"""
