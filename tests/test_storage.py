import json
import tempfile
from pathlib import Path
from src.storage import Storage


def test_save_and_load_json():
    with tempfile.TemporaryDirectory() as tmp:
        storage = Storage(base_dir=tmp)
        data = {"key": "value", "list": [1, 2, 3]}
        path = storage.save_json("2026-05-29", "test.json", data)
        loaded = storage.load_json("2026-05-29", "test.json")
        assert loaded == data
        assert Path(path).exists()


def test_save_raw_articles():
    with tempfile.TemporaryDirectory() as tmp:
        storage = Storage(base_dir=tmp)
        articles = [
            {
                "id": "a1b2c3d4",
                "title": "测试新闻",
                "url": "https://example.com",
                "publish_time": "2026-05-29 08:00",
                "raw_text": "新闻正文内容",
                "fetch_status": "success"
            }
        ]
        storage.save_raw("2026-05-29", "people_daily", "人民日报", articles)
        loaded = storage.load_json("2026-05-29", "raw/people_daily.json")
        assert loaded["source"] == "人民日报"
        assert len(loaded["articles"]) == 1
        assert loaded["articles"][0]["title"] == "测试新闻"


def test_save_filtered():
    with tempfile.TemporaryDirectory() as tmp:
        storage = Storage(base_dir=tmp)
        articles = [
            {
                "id": "a1b2c3d4",
                "source": "人民日报",
                "title": "测试",
                "url": "https://example.com",
                "relevance_score": 8.7,
                "importance_score": 5,
                "category": "粮食安全",
                "summary": "摘要",
                "keywords": ["夏粮", "收购"]
            }
        ]
        storage.save_filtered("2026-05-29", 87, articles)
        loaded = storage.load_json("2026-05-29", "filtered.json")
        assert loaded["total_raw"] == 87
        assert loaded["total_filtered"] == 1


def test_save_classified():
    with tempfile.TemporaryDirectory() as tmp:
        storage = Storage(base_dir=tmp)
        articles = [{"id": "a1b2c3d4", "category": "粮食安全"}]
        category_counts = {"粮食安全": 1}
        storage.save_classified("2026-05-29", articles, category_counts)
        loaded = storage.load_json("2026-05-29", "classified.json")
        assert loaded["category_counts"]["粮食安全"] == 1


def test_save_brief():
    with tempfile.TemporaryDirectory() as tmp:
        storage = Storage(base_dir=tmp)
        storage.save_brief("2026-05-29", "# 日报标题\n\n正文内容")
        path = Path(tmp) / "2026-05-29" / "daily_brief.md"
        content = path.read_text(encoding='utf-8')
        assert "# 日报标题" in content


def test_save_metadata():
    with tempfile.TemporaryDirectory() as tmp:
        storage = Storage(base_dir=tmp)
        meta = {
            "date": "2026-05-29",
            "start_time": "2026-05-29T08:00:00Z",
            "end_time": "2026-05-29T08:18:45Z",
            "total_sources": 15,
            "successful_sources": 14,
            "failed_sources": 1,
            "total_fetched": 87,
            "total_filtered": 42,
            "duration_seconds": 1125,
            "status": "completed"
        }
        storage.save_metadata("2026-05-29", meta)
        loaded = storage.load_json("2026-05-29", "metadata.json")
        assert loaded["status"] == "completed"


def test_save_errors():
    with tempfile.TemporaryDirectory() as tmp:
        storage = Storage(base_dir=tmp)
        errors = [
            {"source": "人民日报", "error": "Connection timeout", "time": "2026-05-29T08:01:00"}
        ]
        storage.save_errors("2026-05-29", errors)
        loaded = storage.load_json("2026-05-29", "errors.json")
        assert loaded[0]["source"] == "人民日报"


def test_missing_file_returns_empty():
    with tempfile.TemporaryDirectory() as tmp:
        storage = Storage(base_dir=tmp)
        result = storage.load_json("2026-05-29", "nonexistent.json")
        assert result is None
