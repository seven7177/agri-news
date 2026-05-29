import pytest
from unittest.mock import Mock, patch, MagicMock
from src.analyzer import Analyzer


def make_config():
    return {
        "llm": {
            "provider": "deepseek",
            "api_key": "test-key",
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
            "max_tokens": 4096,
            "temperature": 0.7,
        },
        "analyzer": {
            "batch_size": 2,
            "min_relevance_score": 6,
            "min_importance_score": 3,
            "categories": ["政策法规", "粮食安全", "产业发展"],
            "prompts": {
                "domain": "三农",
                "layer1_system": "你是{domain}新闻资深编辑。",
                "layer2_system": "你是中国{domain}日报主编。",
            }
        },
        "notify": {"enabled": False}
    }


def test_analyzer_init_sets_prompts():
    analyzer = Analyzer(make_config())
    assert "三农新闻资深编辑" in analyzer.layer1_system
    assert "中国三农日报主编" in analyzer.layer2_system


def test_build_layer1_prompt():
    analyzer = Analyzer(make_config())
    articles = [
        {"id": "abc123", "title": "夏粮丰收", "raw_text": "今年夏粮产量创新高。"},
        {"id": "def456", "title": "乡村振兴案例", "raw_text": "浙江发布典型案例。"},
    ]
    prompt = analyzer._build_layer1_prompt(articles)
    assert "夏粮丰收" in prompt
    assert "乡村振兴案例" in prompt
    assert "政策法规" in prompt


def test_parse_layer1_response():
    analyzer = Analyzer(make_config())
    response = """[
        {"id": "abc123", "title": "夏粮丰收", "relevance_score": 9, "category": "粮食安全", "importance_score": 5, "summary": "夏粮丰收。", "keywords": ["夏粮"]},
        {"id": "def456", "title": "乡村振兴案例", "relevance_score": 8, "category": "乡村振兴", "importance_score": 4, "summary": "乡村振兴。", "keywords": ["乡村振兴"]}
    ]"""
    results = analyzer._parse_layer1_response(response)
    assert len(results) == 2


def test_filter_articles():
    analyzer = Analyzer(make_config())
    articles = [
        {"relevance_score": 9, "importance_score": 5, "title": "保留1"},
        {"relevance_score": 5, "importance_score": 5, "title": "丢弃-不相关"},
        {"relevance_score": 9, "importance_score": 2, "title": "丢弃-不重要"},
        {"relevance_score": 8, "importance_score": 4, "title": "保留2"},
    ]
    filtered = analyzer._filter_articles(articles)
    assert len(filtered) == 2


def test_build_layer2_prompt():
    analyzer = Analyzer(make_config())
    articles = [
        {"category": "粮食安全", "importance_score": 5, "title": "夏粮", "summary": "丰收"},
        {"category": "政策法规", "importance_score": 4, "title": "新政策", "summary": "发布"},
    ]
    prompt = analyzer._build_layer2_prompt(articles)
    assert "粮食安全" in prompt
    assert "夏粮" in prompt


@patch('src.analyzer.OpenAI')
def test_run_layer1(mock_openai):
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = """[
        {"id": "abc", "title": "T", "relevance_score": 9, "category": "粮食安全", "importance_score": 5, "summary": "S", "keywords": ["K"]}
    ]"""
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    analyzer = Analyzer(make_config())
    articles = [{"id": "abc", "title": "T", "source": "测试", "raw_text": "内容"}]
    result = analyzer.run_layer1(articles)

    assert len(result) == 1
    assert result[0]["relevance_score"] == 9
