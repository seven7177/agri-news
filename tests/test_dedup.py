import tempfile
from src.dedup import Dedup


def test_is_duplicate_new_url():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = f"{tmp}/test.db"
        dedup = Dedup(db_path)
        result = dedup.is_duplicate("https://example.com/news/1", "测试")
        assert result is False
        dedup.close()


def test_is_duplicate_existing_url():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = f"{tmp}/test.db"
        dedup = Dedup(db_path)
        dedup.is_duplicate("https://example.com/news/1", "测试")
        result = dedup.is_duplicate("https://example.com/news/1", "测试")
        assert result is True
        dedup.close()


def test_mark_crawled_and_is_duplicate():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = f"{tmp}/test.db"
        dedup = Dedup(db_path)
        dedup.mark_crawled("https://example.com/news/2", "人民日报", "标题")
        assert dedup.is_duplicate("https://example.com/news/2", "人民日报") is True
        dedup.close()


def test_filter_new_urls():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = f"{tmp}/test.db"
        dedup = Dedup(db_path)
        dedup.mark_crawled("https://example.com/news/1", "人民日报", "已抓")
        urls = [
            {"url": "https://example.com/news/1", "title": "已抓"},
            {"url": "https://example.com/news/2", "title": "新新闻"},
            {"url": "https://example.com/news/3", "title": "也是新新闻"},
        ]
        new_urls = dedup.filter_new(urls)
        assert len(new_urls) == 2
        assert new_urls[0]["url"] == "https://example.com/news/2"
        dedup.close()


def test_get_stats():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = f"{tmp}/test.db"
        dedup = Dedup(db_path)
        dedup.mark_crawled("https://a.com/1", "人民日报", "A")
        dedup.mark_crawled("https://b.com/2", "新华社", "B")
        stats = dedup.get_stats()
        assert stats["total_urls"] == 2
        dedup.close()
