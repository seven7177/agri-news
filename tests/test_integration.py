"""集成测试：端到端流程验证（不实际请求网络）"""
import tempfile
from pathlib import Path
from unittest.mock import Mock

from src.storage import Storage
from src.dedup import Dedup
from src.reporter import Reporter


def test_full_data_flow():
    """验证 存储 --> 去重 --> 报告 链路"""
    with tempfile.TemporaryDirectory() as tmp:
        storage = Storage(base_dir=tmp)
        dedup = Dedup(db_path=f"{tmp}/test.db")

        # 1. 模拟抓取数据写入
        articles = [
            {"id": "a1", "title": "夏粮丰收", "url": "https://example.com/1", "publish_time": "2026-05-29", "raw_text": "内容", "fetch_status": "success", "source": "人民日报"},
            {"id": "a2", "title": "乡村振兴", "url": "https://example.com/2", "publish_time": "2026-05-29", "raw_text": "内容", "fetch_status": "success", "source": "新华社"},
            {"id": "a1", "title": "夏粮丰收", "url": "https://example.com/1", "publish_time": "2026-05-29", "raw_text": "内容", "fetch_status": "success", "source": "人民日报"},
        ]

        # 2. 去重
        new_articles = dedup.filter_new(articles)
        assert len(new_articles) == 2  # 第3条是重复的

        # 3. 存储
        storage.save_raw("2026-05-29", "people_daily", "人民日报", [new_articles[0]])
        loaded = storage.load_json("2026-05-29", "raw/people_daily.json")
        assert loaded["total"] == 1

        # 4. 生成报告
        classified = [
            {"category": "粮食安全", "importance_score": 5, "title": "夏粮丰收", "summary": "丰收了", "source": "人民日报"},
            {"category": "乡村振兴", "importance_score": 4, "title": "乡村振兴", "summary": "振兴中", "source": "新华社"},
        ]
        category_counts = {"粮食安全": 1, "乡村振兴": 1}
        metadata = {"total_fetched": 2, "total_filtered": 2, "duration_seconds": 120, "successful_sources": 2, "failed_sources": 0, "total_sources": 2}

        overview = Reporter.generate_overview("2026-05-29", classified, category_counts, metadata)
        assert "夏粮丰收" in overview
        storage.save_brief("2026-05-29", overview)
        assert Path(tmp, "2026-05-29", "daily_brief.md").exists()

        dedup.close()


def test_config_resolves_all_sources():
    """验证配置文件包含15个源"""
    from src.config import load_config
    config = load_config("config.yaml")
    sources = config.get("sources", [])
    assert len(sources) == 15
    assert all("name" in s for s in sources)
    assert all("handler" in s for s in sources)


def test_all_handlers_importable():
    """验证15个handler都可导入"""
    from src.scrapers.handlers import (
        people_daily, xinhua, cctv_news, farmers_daily, chinanews,
        guangming_daily, economic_daily, zhejiang_daily, cztv, tide_news,
        zjol, cctv_net, cnr_news, people_net, dskb,
    )
    assert people_daily is not None
    assert dskb is not None


def test_all_modules_importable():
    """验证所有核心模块可导入"""
    from src.config import load_config
    from src.env_detector import is_local, get_run_mode
    from src.storage import Storage
    from src.dedup import Dedup
    from src.analyzer import Analyzer
    from src.reporter import Reporter
    from src.notifier import Notifier
    from src.scrapers.base import BaseScraper
    from src.scrapers.manager import ScraperManager
    from src.scrapers.sources import get_enabled_sources
    from src.scrapers.utils.http_client import HttpClient
    from src.scrapers.utils.parser_helper import clean_html, normalize_date
    from src.scrapers.utils.anti_detect import random_user_agent, build_headers
    from src.scrapers.exceptions import ScraperError, FetchError, ParseError
    print("All modules imported successfully")


def test_env_detector_consistency():
    """验证 env_detector 的一致性"""
    from src.env_detector import is_github_actions, is_local, get_run_mode
    assert is_github_actions() != is_local()
    mode = get_run_mode()
    assert mode in ("github_actions", "local")
