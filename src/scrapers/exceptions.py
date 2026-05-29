class ScraperError(Exception):
    """爬虫基础异常"""


class FetchError(ScraperError):
    """请求失败"""


class ParseError(ScraperError):
    """解析失败"""


class RateLimitError(ScraperError):
    """被限流"""
