import pytest
from src.scrapers.utils.http_client import HttpClient
from src.scrapers.exceptions import FetchError


def test_http_client_init_with_config():
    config = {
        "scraper": {
            "timeout": 10,
            "retry_max": 1,
            "retry_delay": 1,
            "delay_min": 1,
            "delay_max": 2
        }
    }
    client = HttpClient(config)
    assert client.timeout == 10
    assert client.retry_max == 1


def test_http_client_defaults():
    client = HttpClient({})
    assert client.timeout == 15
    assert client.retry_max == 2


def test_fetch_success(httpx_mock):
    httpx_mock.add_response(url="https://example.com", text="<html>OK</html>")
    client = HttpClient({})
    result = client.fetch("https://example.com")
    assert "OK" in result


def test_fetch_http_error(httpx_mock):
    httpx_mock.add_response(url="https://example.com/404", status_code=404)
    client = HttpClient({"scraper": {"timeout": 5, "retry_max": 0, "retry_delay": 1}})
    with pytest.raises(FetchError):
        client.fetch("https://example.com/404")


def test_fetch_retries_on_500(httpx_mock):
    httpx_mock.add_response(url="https://example.com/500", status_code=500)
    httpx_mock.add_response(url="https://example.com/500", status_code=500)
    httpx_mock.add_response(url="https://example.com/500", status_code=500)
    client = HttpClient({"scraper": {"timeout": 5, "retry_max": 2, "retry_delay": 0}})
    with pytest.raises(FetchError):
        client.fetch("https://example.com/500")
