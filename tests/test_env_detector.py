import os
from src.env_detector import is_github_actions, is_local, get_run_mode


def test_is_github_actions_true(monkeypatch):
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    assert is_github_actions() is True


def test_is_github_actions_false():
    if 'GITHUB_ACTIONS' in os.environ:
        del os.environ['GITHUB_ACTIONS']
    assert is_github_actions() is False


def test_is_local_true():
    if 'GITHUB_ACTIONS' in os.environ:
        del os.environ['GITHUB_ACTIONS']
    assert is_local() is True


def test_is_local_false(monkeypatch):
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    assert is_local() is False


def test_get_run_mode_ci(monkeypatch):
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    assert get_run_mode() == 'github_actions'


def test_get_run_mode_local():
    if 'GITHUB_ACTIONS' in os.environ:
        del os.environ['GITHUB_ACTIONS']
    assert get_run_mode() == 'local'
