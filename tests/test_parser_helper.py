from src.scrapers.utils.parser_helper import (
    clean_html,
    normalize_date,
    extract_text_from_html,
    matches_keywords,
    matches_keywords_and,
)


def test_clean_html_strips_tags():
    html = '<div class="article"><p>这是正文内容</p><script>alert("xss")</script></div>'
    result = clean_html(html)
    assert "这是正文内容" in result
    assert "script" not in result


def test_normalize_date_standard():
    assert normalize_date("2026-05-29 08:30") == "2026-05-29 08:30"
    assert normalize_date("2026/05/29") == "2026-05-29"


def test_normalize_date_chinese():
    result = normalize_date("2026年5月29日 08:30")
    assert "2026-05-29" in result


def test_extract_text_from_html():
    html = """
    <html><head><title>测试</title></head>
    <body><article><h1>标题</h1><p>正文段落1</p><p>正文段落2</p></article></body>
    </html>
    """
    text = extract_text_from_html(html)
    assert "标题" in text
    assert "正文段落1" in text
    assert "正文段落2" in text


def test_matches_keywords_match():
    keywords = ["农业", "农村", "粮食"]
    assert matches_keywords("全国农业发展报告", keywords) is True
    assert matches_keywords("农村基础设施改善", keywords) is True


def test_matches_keywords_no_match():
    keywords = ["农业", "农村", "粮食"]
    assert matches_keywords("城市发展规划", keywords) is False
    assert matches_keywords("工业产值增长", keywords) is False


def test_matches_keywords_and_both_match():
    agri_kw = ["农业", "农村", "粮食"]
    region_kw = ["浙江", "杭州", "宁波"]
    assert matches_keywords_and("浙江农业现代化发展", agri_kw, region_kw) is True
    assert matches_keywords_and("杭州粮食产量创新高", agri_kw, region_kw) is True


def test_matches_keywords_and_only_one_group():
    agri_kw = ["农业", "农村", "粮食"]
    region_kw = ["浙江", "杭州", "宁波"]
    assert matches_keywords_and("北京农业发展报告", agri_kw, region_kw) is False
    assert matches_keywords_and("浙江工业产值增长", agri_kw, region_kw) is False


def test_matches_keywords_and_both_empty():
    assert matches_keywords_and("任意标题", [], []) is True


def test_matches_keywords_and_one_empty():
    agri_kw = ["农业"]
    assert matches_keywords_and("农业发展", agri_kw, []) is True
    assert matches_keywords_and("工业发展", agri_kw, []) is False
