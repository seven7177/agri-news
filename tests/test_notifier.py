import os
import pytest
from unittest.mock import Mock, patch
from src.notifier import Notifier


def make_notifier():
    config = {
        "notify": {
            "enabled": True,
            "provider": "pushplus",
            "pushplus_token": "test-token",
            "success": {"enabled": True, "brief_max_chars": 600, "include_stats": True},
            "failure": {"enabled": True, "min_failed_sources": 3, "include_errors": True, "max_errors": 8},
        },
        "pages": {"title": "三农新闻日报"},
    }
    os.environ["PUSHPLUS_TOKEN"] = "test-token"
    return Notifier(config)


def test_notifier_init_with_env_token():
    os.environ["PUSHPLUS_TOKEN"] = "env-token"
    n = Notifier({"notify": {"enabled": True}})
    assert n.token == "env-token"
    del os.environ["PUSHPLUS_TOKEN"]


def test_notifier_disabled_when_no_token():
    if "PUSHPLUS_TOKEN" in os.environ:
        del os.environ["PUSHPLUS_TOKEN"]
    n = Notifier({"notify": {"enabled": True}})
    assert n.token is None


@patch('src.notifier.httpx.Client')
def test_send_daily_brief(mock_client_class):
    mock_client = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"code": 200}
    mock_client.post.return_value = mock_response
    mock_client_class.return_value.__enter__.return_value = mock_client

    n = make_notifier()
    brief = "# 日报\n\n## 今日要点\n1. **夏粮丰收** — 产量创新高（来源：人民日报）\n\n## 分类统计\n| 粮食安全 | 15 |"
    result = n.send_daily_brief("2026-05-29", brief, "https://example.com")
    assert result is True


@patch('src.notifier.httpx.Client')
def test_send_failure_alert_skips_when_below_threshold(mock_client_class):
    n = make_notifier()
    errors = [{"source": "源1", "error": "timeout"}]
    result = n.send_failure_alert("2026-05-29", errors, {"successful_sources": 14, "failed_sources": 1})
    assert result == "skipped"
