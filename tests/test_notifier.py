from unittest.mock import MagicMock, patch
from src.notifier import Notifier


def test_notifier_init_with_env_email(monkeypatch):
    monkeypatch.setenv("EMAIL_USERNAME", "test@qq.com")
    n = Notifier({"notify": {"enabled": True, "provider": "email"}})
    assert n.email_user == "test@qq.com"


def test_notifier_disabled_when_no_email(monkeypatch):
    monkeypatch.delenv("EMAIL_USERNAME", raising=False)
    monkeypatch.delenv("EMAIL_PASSWORD", raising=False)
    monkeypatch.delenv("EMAIL_TO", raising=False)
    n = Notifier({"notify": {"enabled": True, "provider": "email"}})
    assert n.email_user == ""
    assert n.email_pass == ""


@patch("src.notifier.smtplib.SMTP_SSL")
def test_send_daily_brief(mock_smtp_class, monkeypatch):
    mock_server = MagicMock()
    mock_smtp_class.return_value = mock_server

    monkeypatch.setenv("EMAIL_USERNAME", "test@qq.com")
    monkeypatch.setenv("EMAIL_PASSWORD", "authcode")
    monkeypatch.setenv("EMAIL_TO", "receiver@qq.com")

    n = Notifier({"notify": {"enabled": True, "provider": "email"}})
    brief = "# 浙江三农新闻 2026-05-31\n\n## 人民日报 (1条)\n\n- [标题](https://example.com)"
    result = n.send_daily_brief("2026-05-31", brief)

    assert result is True
    mock_server.login.assert_called_once()
    mock_server.sendmail.assert_called_once()


def test_send_failure_alert_skips_when_no_errors(monkeypatch):
    monkeypatch.setenv("EMAIL_USERNAME", "test@qq.com")
    monkeypatch.setenv("EMAIL_PASSWORD", "authcode")
    monkeypatch.setenv("EMAIL_TO", "receiver@qq.com")

    n = Notifier({"notify": {"enabled": True, "provider": "email"}})
    result = n.send_failure_alert("2026-05-31", [], {"total_sources": 15})
    assert result == "skipped"
