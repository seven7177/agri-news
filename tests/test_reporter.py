from src.reporter import Reporter


def test_generate_list():
    source_results = [
        {
            "source": "人民日报",
            "handler": "people_daily",
            "articles": [
                {"title": "浙江夏粮丰收", "url": "https://example.com/1", "publish_time": "2026-05-31"},
                {"title": "杭州乡村振兴", "url": "https://example.com/2", "publish_time": "2026-05-31"},
            ],
        },
        {
            "source": "新华社",
            "handler": "xinhua",
            "articles": [
                {"title": "浙江省农业农村政策", "url": "https://example.com/3", "publish_time": ""},
            ],
        },
        {
            "source": "央视新闻",
            "handler": "cctv_news",
            "articles": [],
        },
    ]
    metadata = {
        "total_sources": 15,
        "successful_sources": 14,
        "failed_sources": 1,
        "duration_seconds": 120,
    }

    result = Reporter.generate_list("2026-05-31", source_results, metadata)
    assert "浙江夏粮丰收" in result
    assert "杭州乡村振兴" in result
    assert "https://example.com/1" in result
    assert "人民日报 (2条)" in result
    assert "新华社 (1条)" in result
    assert "央视新闻" not in result  # 空的源不显示
    assert "15 个源" in result
    assert "命中 3 条" in result


def test_generate_archive_page():
    dates = ["2026-05-27", "2026-05-28", "2026-05-29"]
    html = Reporter.generate_archive_page(dates)
    assert "2026-05-29" in html
    assert "2026-05-27" in html
    assert "浙江三农新闻" in html


def test_format_duration():
    assert Reporter._format_duration(3661) == "61分1秒"
    assert Reporter._format_duration(65) == "1分5秒"
    assert Reporter._format_duration(30) == "30秒"
