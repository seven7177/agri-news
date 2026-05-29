from src.reporter import Reporter


def test_generate_overview():
    classified_articles = [
        {"category": "粮食安全", "importance_score": 5, "title": "夏粮丰收", "summary": "产量创新高", "source": "人民日报"},
        {"category": "政策法规", "importance_score": 4, "title": "新政策", "summary": "农业农村部发布", "source": "新华社"},
        {"category": "粮食安全", "importance_score": 3, "title": "收购进度", "summary": "进度快", "source": "农民日报"},
    ]
    category_counts = {"粮食安全": 2, "政策法规": 1, "产业发展": 0}
    metadata = {
        "total_fetched": 87,
        "total_filtered": 42,
        "duration_seconds": 1125,
        "successful_sources": 14,
        "failed_sources": 1,
        "total_sources": 15,
    }

    overview = Reporter.generate_overview("2026-05-29", classified_articles, category_counts, metadata)
    assert "2026-05-29" in overview
    assert "粮食安全" in overview
    assert "夏粮丰收" in overview
    assert "87" in overview


def test_generate_archive_page():
    dates = ["2026-05-27", "2026-05-28", "2026-05-29"]
    html = Reporter.generate_archive_page(dates)
    assert "2026-05-29" in html
    assert "2026-05-27" in html


def test_format_duration():
    assert Reporter._format_duration(3661) == "61分1秒"
    assert Reporter._format_duration(65) == "1分5秒"
    assert Reporter._format_duration(30) == "30秒"
