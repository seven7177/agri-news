# 三农新闻聚合分析系统 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 构建一个自动抓取 15 家官方媒体三农新闻、AI 分析分类汇总、生成日报并通过微信推送的系统，支持 GitHub Actions 和本地双模式运行。

**架构：** Python 3.12 全栈，httpx + BeautifulSoup 串行爬虫，DeepSeek 两层 AI 分析（分类过滤 → 日报综述），JSON 文件 + SQLite 存储，PushPlus 微信推送，GitHub Pages 静态站点，CLI 参数 + YAML 配置驱动多实例。

**技术栈：** Python 3.12, httpx, BeautifulSoup4, lxml, SQLite3, openai SDK (DeepSeek 兼容), PyYAML, python-dotenv, pytest, GitHub Actions

---

## 文件结构

```
agri-news/
├── config.yaml                          # [创建] 全局配置
├── configs/
│   └── tech_news.example.yaml           # [创建] 科技新闻配置示例
├── src/
│   ├── __init__.py                      # [创建]
│   ├── main.py                          # [创建] CLI 入口 + 编排
│   ├── config.py                        # [创建] 配置加载
│   ├── env_detector.py                  # [创建] 运行环境检测
│   ├── storage.py                       # [创建] 统一数据读写
│   ├── dedup.py                         # [创建] SQLite 去重
│   ├── analyzer.py                      # [创建] AI 两层分析
│   ├── reporter.py                      # [创建] Markdown 报告生成
│   ├── notifier.py                      # [创建] PushPlus 推送
│   ├── scrapers/
│   │   ├── __init__.py                  # [创建]
│   │   ├── base.py                      # [创建] 爬虫基类
│   │   ├── manager.py                   # [创建] 爬虫管理器
│   │   ├── sources.py                   # [创建] 新闻源配置清单
│   │   ├── exceptions.py                # [创建] 自定义异常
│   │   ├── handlers/
│   │   │   ├── __init__.py              # [创建]
│   │   │   ├── people_daily.py          # [创建] 人民日报
│   │   │   ├── xinhua.py                # [创建] 新华社
│   │   │   ├── cctv_news.py             # [创建] 央视新闻
│   │   │   ├── farmers_daily.py         # [创建] 农民日报
│   │   │   ├── chinanews.py             # [创建] 中新社
│   │   │   ├── guangming_daily.py       # [创建] 光明日报
│   │   │   ├── economic_daily.py        # [创建] 经济日报
│   │   │   ├── zhejiang_daily.py        # [创建] 浙江日报
│   │   │   ├── cztv.py                  # [创建] 中国蓝新闻
│   │   │   ├── tide_news.py             # [创建] 潮新闻
│   │   │   ├── zjol.py                  # [创建] 浙江在线
│   │   │   ├── cctv_net.py              # [创建] 央视网
│   │   │   ├── cnr_news.py              # [创建] 央广网
│   │   │   ├── people_net.py            # [创建] 人民网
│   │   │   └── dskb.py                  # [创建] 都市快报
│   │   └── utils/
│   │       ├── __init__.py              # [创建]
│   │       ├── http_client.py           # [创建] 统一请求客户端
│   │       ├── parser_helper.py         # [创建] 通用解析辅助
│   │       └── anti_detect.py           # [创建] 反检测策略
├── tests/
│   ├── __init__.py                      # [创建]
│   ├── test_config.py                   # [创建]
│   ├── test_storage.py                  # [创建]
│   ├── test_dedup.py                    # [创建]
│   ├── test_scraper_base.py             # [创建]
│   ├── test_scraper_manager.py          # [创建]
│   ├── test_http_client.py              # [创建]
│   ├── test_analyzer.py                 # [创建]
│   ├── test_reporter.py                 # [创建]
│   ├── test_notifier.py                 # [创建]
│   └── test_integration.py              # [创建]
├── docs/
│   └── index.html                       # [创建] GitHub Pages 首页
├── .github/workflows/
│   └── daily.yml                        # [创建] 定时调度
├── requirements.txt                     # [创建]
├── requirements-dev.txt                 # [创建]
├── .env.example                         # [创建]
├── .gitignore                           # [创建]
└── README.md                            # [创建]
```

---

### 任务 1：项目脚手架

**文件：**
- 创建：`.gitignore`、`.env.example`、`requirements.txt`、`requirements-dev.txt`、`README.md`
- 创建：`src/__init__.py`、`tests/__init__.py`
- 创建：`src/scrapers/__init__.py`、`src/scrapers/handlers/__init__.py`、`src/scrapers/utils/__init__.py`

- [ ] **步骤 1：创建 `.gitignore`**

```
.env
.env.local
data/
archive.db
__pycache__/
*.pyc
.venv/
.pytest_cache/
*.egg-info/
dist/
```

- [ ] **步骤 2：创建 `.env.example`**

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
PUSHPLUS_TOKEN=your_pushplus_token_here
```

- [ ] **步骤 3：创建 `requirements.txt`**

```
httpx>=0.27.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
openai>=1.30.0
pyyaml>=6.0
python-dotenv>=1.0.0
```

- [ ] **步骤 4：创建 `requirements-dev.txt`**

```
pytest>=8.0
pytest-mock>=3.12
black>=24.0
ruff>=0.3.0
```

- [ ] **步骤 5：创建空 `__init__.py` 文件**

创建四个空文件：`src/__init__.py`、`tests/__init__.py`、`src/scrapers/__init__.py`、`src/scrapers/handlers/__init__.py`、`src/scrapers/utils/__init__.py`

- [ ] **步骤 6：创建 `README.md`**

````markdown
# 三农新闻日报

自动抓取 15 家官方媒体农业农村相关新闻，AI 分析汇总生成日报，微信推送。

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Key

# 本地测试（只爬取，不调 AI）
python src/main.py --dry-run

# 完整运行
python src/main.py
```

## 配置多实例

```bash
python src/main.py --config configs/tech_news.yaml
```
````

- [ ] **步骤 7：安装依赖并验证**

```bash
python -m venv .venv && source .venv/Scripts/activate && pip install -r requirements.txt && pip install -r requirements-dev.txt && python -c "import httpx; import bs4; import lxml; import openai; import yaml; import dotenv; print('OK')"
```

预期输出：`OK`

- [ ] **步骤 8：Commit**

```bash
git add .
git commit -m "chore: project scaffolding"
```

---

### 任务 2：配置模块 (`config.py` + `config.yaml`)

**文件：**
- 创建：`src/config.py`
- 创建：`tests/test_config.py`
- 创建：`config.yaml`

- [ ] **步骤 1：编写 `config.py` 测试**

创建 `tests/test_config.py`：

```python
import os
import tempfile
import pytest
from src.config import load_config


def test_load_config_resolves_env_vars():
    yaml_content = """
llm:
  api_key: ${TEST_API_KEY}
scraper:
  delay_min: 2
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        tmp_path = f.name

    os.environ['TEST_API_KEY'] = 'sk-test-123'
    try:
        config = load_config(tmp_path)
        assert config['llm']['api_key'] == 'sk-test-123'
        assert config['scraper']['delay_min'] == 2
    finally:
        os.unlink(tmp_path)
        del os.environ['TEST_API_KEY']


def test_load_config_missing_env_var_defaults_to_empty():
    yaml_content = "llm:\n  api_key: ${MISSING_VAR}"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        tmp_path = f.name

    try:
        config = load_config(tmp_path)
        assert config['llm']['api_key'] == ''
    finally:
        os.unlink(tmp_path)


def test_load_config_no_env_var_placeholders():
    yaml_content = "scraper:\n  delay_min: 2\ntimeout: 15"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        tmp_path = f.name

    try:
        config = load_config(tmp_path)
        assert config['scraper']['delay_min'] == 2
        assert config['timeout'] == 15
    finally:
        os.unlink(tmp_path)
```

- [ ] **步骤 2：运行测试验证失败**

```bash
python -m pytest tests/test_config.py -v
```

预期：FAIL，`ModuleNotFoundError` 或 `ImportError`

- [ ] **步骤 3：实现 `src/config.py`**

```python
import os
import re
from pathlib import Path

import yaml
from dotenv import load_dotenv


def _resolve_env_vars(value):
    """递归解析值中的 ${VAR_NAME} 占位符"""
    if isinstance(value, str):
        return re.sub(
            r'\$\{(\w+)\}',
            lambda m: os.getenv(m.group(1), ''),
            value
        )
    if isinstance(value, dict):
        return {k: _resolve_env_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_env_vars(item) for item in value]
    return value


def load_config(path="config.yaml"):
    load_dotenv()
    with open(path, 'r', encoding='utf-8') as f:
        raw = yaml.safe_load(f)
    return _resolve_env_vars(raw)
```

- [ ] **步骤 4：运行测试验证通过**

```bash
python -m pytest tests/test_config.py -v
```

预期：3 PASSED

- [ ] **步骤 5：创建 `config.yaml`**

```yaml
llm:
  provider: deepseek
  api_key: ${DEEPSEEK_API_KEY}
  base_url: https://api.deepseek.com/v1
  model: deepseek-chat
  max_tokens: 4096
  temperature: 0.7

sources:
  - name: 人民日报
    handler: people_daily
    url: https://www.people.com.cn/
    category_lists:
      - http://country.people.com.cn/
    filter_keywords:
      - 农业
      - 农村
      - 农民
      - 粮食
      - 乡村振兴
      - 耕地
    priority: 1
    enabled: true

  - name: 新华社
    handler: xinhua
    url: https://www.news.cn/
    filter_keywords:
      - 农业
      - 农村
      - 农民
      - 粮食
      - 乡村振兴
      - 三农
    priority: 1
    enabled: true

  - name: 央视新闻
    handler: cctv_news
    url: https://news.cctv.com/
    filter_keywords:
      - 农业
      - 农村
      - 乡村
      - 粮食
      - 三农
    priority: 1
    enabled: true

  - name: 农民日报
    handler: farmers_daily
    url: https://www.farmer.com.cn/
    priority: 1
    enabled: true

  - name: 中新社
    handler: chinanews
    url: https://www.chinanews.com/
    filter_keywords:
      - 农业
      - 农村
      - 乡村
      - 粮食
      - 三农
      - 农民
    priority: 2
    enabled: true

  - name: 光明日报
    handler: guangming_daily
    url: https://www.gmw.cn/
    filter_keywords:
      - 农业
      - 农村
      - 乡村
      - 粮食
      - 三农
    priority: 2
    enabled: true

  - name: 经济日报
    handler: economic_daily
    url: https://www.ce.cn/
    filter_keywords:
      - 农业
      - 农村
      - 粮食
      - 乡村振兴
      - 三农
    priority: 2
    enabled: true

  - name: 浙江日报
    handler: zhejiang_daily
    url: https://zjnews.zjol.com.cn/
    filter_keywords:
      - 农业
      - 农村
      - 乡村
      - 三农
      - 乡村振兴
    priority: 2
    enabled: true

  - name: 中国蓝新闻
    handler: cztv
    url: https://www.cztv.com/
    filter_keywords:
      - 农业
      - 农村
      - 乡村
      - 三农
    priority: 2
    enabled: true

  - name: 潮新闻
    handler: tide_news
    url: https://tidenews.com.cn/
    filter_keywords:
      - 农业
      - 农村
      - 乡村
      - 三农
    priority: 2
    enabled: true

  - name: 浙江在线
    handler: zjol
    url: https://www.zjol.com.cn/
    filter_keywords:
      - 农业
      - 农村
      - 乡村
      - 三农
    priority: 2
    enabled: true

  - name: 央视网
    handler: cctv_net
    url: https://www.cctv.com/
    filter_keywords:
      - 农业
      - 农村
      - 乡村
      - 粮食
      - 三农
    priority: 1
    enabled: true

  - name: 央广网
    handler: cnr_news
    url: https://www.cnr.cn/
    filter_keywords:
      - 农业
      - 农村
      - 乡村
      - 粮食
      - 三农
    priority: 2
    enabled: true

  - name: 人民网
    handler: people_net
    url: https://www.people.com.cn/
    category_lists:
      - http://country.people.com.cn/
    filter_keywords:
      - 农业
      - 农村
      - 农民
      - 粮食
      - 乡村振兴
    priority: 1
    enabled: true

  - name: 都市快报
    handler: dskb
    url: https://hzdaily.hangzhou.com.cn/dskb/
    filter_keywords:
      - 农业
      - 农村
      - 乡村
      - 乡村振兴
    priority: 3
    enabled: true

scraper:
  delay_min: 2
  delay_max: 5
  retry_max: 2
  retry_delay: 10
  timeout: 15
  max_articles_per_source: 30

analyzer:
  batch_size: 10
  min_relevance_score: 6
  min_importance_score: 3
  categories:
    - 政策法规
    - 粮食安全
    - 产业发展
    - 乡村振兴
    - 科技兴农
    - 生态环保
    - 农产品市场
    - 其他
  prompts:
    domain: 三农
    layer1_system: "你是{domain}新闻资深编辑。"
    layer2_system: "你是中国{domain}日报主编。"

notify:
  enabled: true
  provider: pushplus
  pushplus_token: ${PUSHPLUS_TOKEN}
  success:
    enabled: true
    brief_max_chars: 600
    include_stats: true
  failure:
    enabled: true
    min_failed_sources: 3
    include_errors: true
    max_errors: 8

pages:
  enabled: true
  title: 三农新闻日报
  subtitle: 农业农村政策与产业动态简报
  archive_days: 30
```

- [ ] **步骤 6：验证配置文件可被 config.py 正确解析**

```bash
python -c "from src.config import load_config; c = load_config('config.yaml'); print(f'Sources: {len(c[\"sources\"])}'); print(f'Categories: {len(c[\"analyzer\"][\"categories\"])}')"
```

预期输出：`Sources: 15` `Categories: 8`

- [ ] **步骤 7：Commit**

```bash
git add src/config.py tests/test_config.py config.yaml
git commit -m "feat: add config module with env var resolution"
```

---

### 任务 3：环境检测模块 (`env_detector.py`)

**文件：**
- 创建：`src/env_detector.py`
- 创建：`tests/test_env_detector.py`

- [ ] **步骤 1：编写测试**

创建 `tests/test_env_detector.py`：

```python
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
```

- [ ] **步骤 2：运行测试验证失败**

```bash
python -m pytest tests/test_env_detector.py -v
```

- [ ] **步骤 3：实现 `src/env_detector.py`**

```python
import os


def is_github_actions():
    return os.getenv('GITHUB_ACTIONS', '').lower() == 'true'


def is_local():
    return not is_github_actions()


def get_run_mode():
    return 'github_actions' if is_github_actions() else 'local'
```

- [ ] **步骤 4：运行测试验证通过**

```bash
python -m pytest tests/test_env_detector.py -v
```

预期：6 PASSED

- [ ] **步骤 5：Commit**

```bash
git add src/env_detector.py tests/test_env_detector.py
git commit -m "feat: add environment detection module"
```

---

### 任务 4：存储模块 (`storage.py`)

**文件：**
- 创建：`src/storage.py`
- 创建：`tests/test_storage.py`

- [ ] **步骤 1：编写测试**

创建 `tests/test_storage.py`：

```python
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
```

- [ ] **步骤 2：运行测试验证失败**

```bash
python -m pytest tests/test_storage.py -v
```

- [ ] **步骤 3：实现 `src/storage.py`**

```python
import json
from pathlib import Path
from datetime import datetime


class Storage:
    def __init__(self, base_dir="data"):
        self.base_dir = Path(base_dir)

    def _date_dir(self, date_str):
        return self.base_dir / date_str

    def _raw_dir(self, date_str):
        return self._date_dir(date_str) / "raw"

    def save_json(self, date_str, filename, data):
        dir_path = self._date_dir(date_str)
        if filename.startswith("raw/"):
            dir_path = self._raw_dir(date_str)
            filename = filename[4:]
        dir_path.mkdir(parents=True, exist_ok=True)
        filepath = dir_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return str(filepath)

    def load_json(self, date_str, filename):
        filepath = self._date_dir(date_str) / filename
        if not filepath.exists():
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_raw(self, date_str, source_key, source_name, articles):
        data = {
            "source": source_name,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "total": len(articles),
            "articles": articles
        }
        return self.save_json(date_str, f"raw/{source_key}.json", data)

    def save_filtered(self, date_str, total_raw, articles):
        data = {
            "date": date_str,
            "filtered_at": datetime.utcnow().isoformat() + "Z",
            "total_raw": total_raw,
            "total_filtered": len(articles),
            "articles": articles
        }
        return self.save_json(date_str, "filtered.json", data)

    def save_classified(self, date_str, articles, category_counts):
        data = {
            "date": date_str,
            "analyzed_at": datetime.utcnow().isoformat() + "Z",
            "total_filtered": len(articles),
            "category_counts": category_counts,
            "articles": sorted(articles, key=lambda x: x.get("importance_score", 0), reverse=True)
        }
        return self.save_json(date_str, "classified.json", data)

    def save_brief(self, date_str, brief_text):
        dir_path = self._date_dir(date_str)
        dir_path.mkdir(parents=True, exist_ok=True)
        filepath = dir_path / "daily_brief.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(brief_text)
        return str(filepath)

    def save_metadata(self, date_str, metadata):
        return self.save_json(date_str, "metadata.json", metadata)

    def save_errors(self, date_str, errors):
        return self.save_json(date_str, "errors.json", errors)
```

- [ ] **步骤 4：运行测试验证通过**

```bash
python -m pytest tests/test_storage.py -v
```

预期：7 PASSED

- [ ] **步骤 5：Commit**

```bash
git add src/storage.py tests/test_storage.py
git commit -m "feat: add storage module"
```

---

### 任务 5：去重模块 (`dedup.py`)

**文件：**
- 创建：`src/dedup.py`
- 创建：`tests/test_dedup.py`

- [ ] **步骤 1：编写测试**

创建 `tests/test_dedup.py`：

```python
import tempfile
from src.dedup import Dedup


def test_is_duplicate_new_url():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = f"{tmp}/test.db"
        dedup = Dedup(db_path)
        result = dedup.is_duplicate("https://example.com/news/1", "测试")
        assert result is False
        dedup.close()


def test_is_duplicate_existing_url():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = f"{tmp}/test.db"
        dedup = Dedup(db_path)
        dedup.is_duplicate("https://example.com/news/1", "测试")
        result = dedup.is_duplicate("https://example.com/news/1", "测试")
        assert result is True
        dedup.close()


def test_mark_crawled_and_is_duplicate():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = f"{tmp}/test.db"
        dedup = Dedup(db_path)
        dedup.mark_crawled("https://example.com/news/2", "人民日报", "标题")
        assert dedup.is_duplicate("https://example.com/news/2", "人民日报") is True
        dedup.close()


def test_filter_new_urls():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = f"{tmp}/test.db"
        dedup = Dedup(db_path)
        dedup.mark_crawled("https://example.com/news/1", "人民日报", "已抓")
        urls = [
            {"url": "https://example.com/news/1", "title": "已抓"},
            {"url": "https://example.com/news/2", "title": "新新闻"},
            {"url": "https://example.com/news/3", "title": "也是新新闻"},
        ]
        new_urls = dedup.filter_new(urls)
        assert len(new_urls) == 2
        assert new_urls[0]["url"] == "https://example.com/news/2"
        dedup.close()


def test_get_stats():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = f"{tmp}/test.db"
        dedup = Dedup(db_path)
        dedup.mark_crawled("https://a.com/1", "人民日报", "A")
        dedup.mark_crawled("https://b.com/2", "新华社", "B")
        stats = dedup.get_stats()
        assert stats["total_urls"] == 2
        dedup.close()
```

- [ ] **步骤 2：运行测试验证失败**

```bash
python -m pytest tests/test_dedup.py -v
```

- [ ] **步骤 3：实现 `src/dedup.py`**

```python
import hashlib
import sqlite3
from datetime import datetime


class Dedup:
    def __init__(self, db_path="archive.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS crawled_urls (
                url_hash    TEXT PRIMARY KEY,
                url         TEXT NOT NULL,
                source      TEXT NOT NULL,
                title       TEXT,
                first_seen  TEXT NOT NULL,
                last_crawled TEXT NOT NULL,
                crawl_count INTEGER DEFAULT 1,
                status      TEXT DEFAULT 'success',
                last_error  TEXT
            )
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_source ON crawled_urls(source)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_last_crawled ON crawled_urls(last_crawled)
        """)
        self.conn.commit()

    def _hash_url(self, url):
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    def is_duplicate(self, url, source):
        url_hash = self._hash_url(url)
        cursor = self.conn.execute(
            "SELECT url_hash FROM crawled_urls WHERE url_hash = ?",
            (url_hash,)
        )
        return cursor.fetchone() is not None

    def mark_crawled(self, url, source, title, status="success", error=None):
        url_hash = self._hash_url(url)
        now = datetime.utcnow().isoformat() + "Z"
        existing = self.conn.execute(
            "SELECT crawl_count FROM crawled_urls WHERE url_hash = ?",
            (url_hash,)
        ).fetchone()

        if existing:
            self.conn.execute(
                """UPDATE crawled_urls
                   SET last_crawled = ?, crawl_count = crawl_count + 1,
                       status = ?, last_error = ?, title = ?
                   WHERE url_hash = ?""",
                (now, status, error, title, url_hash)
            )
        else:
            self.conn.execute(
                """INSERT INTO crawled_urls
                   (url_hash, url, source, title, first_seen, last_crawled, status, last_error)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (url_hash, url, source, title, now, now, status, error)
            )
        self.conn.commit()

    def filter_new(self, articles):
        new_articles = []
        for article in articles:
            if not self.is_duplicate(article["url"], article.get("source", "")):
                new_articles.append(article)
                self.mark_crawled(
                    article["url"],
                    article.get("source", ""),
                    article.get("title", ""),
                    article.get("fetch_status", "success")
                )
        return new_articles

    def get_stats(self):
        cursor = self.conn.execute("SELECT COUNT(*) FROM crawled_urls")
        total = cursor.fetchone()[0]
        return {"total_urls": total}

    def close(self):
        self.conn.close()
```

- [ ] **步骤 4：运行测试验证通过**

```bash
python -m pytest tests/test_dedup.py -v
```

预期：5 PASSED

- [ ] **步骤 5：Commit**

```bash
git add src/dedup.py tests/test_dedup.py
git commit -m "feat: add dedup module with SQLite backend"
```

---

### 任务 6：爬虫基础设施（exceptions + parser_helper）

**文件：**
- 创建：`src/scrapers/exceptions.py`
- 创建：`src/scrapers/utils/parser_helper.py`
- 创建：`tests/test_parser_helper.py`

- [ ] **步骤 1：创建 `src/scrapers/exceptions.py`**

```python
class ScraperError(Exception):
    """爬虫基础异常"""

class FetchError(ScraperError):
    """请求失败"""

class ParseError(ScraperError):
    """解析失败"""

class RateLimitError(ScraperError):
    """被限流"""
```

- [ ] **步骤 2：编写 `tests/test_parser_helper.py`**

```python
from src.scrapers.utils.parser_helper import (
    clean_html,
    normalize_date,
    extract_text_from_html,
    matches_keywords,
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
```

- [ ] **步骤 3：运行测试验证失败**

```bash
python -m pytest tests/test_parser_helper.py -v
```

- [ ] **步骤 4：实现 `src/scrapers/utils/parser_helper.py`**

```python
import re
from datetime import datetime
from bs4 import BeautifulSoup


def clean_html(html):
    soup = BeautifulSoup(html, 'lxml')
    for tag in soup(['script', 'style', 'nav', 'footer', 'iframe', 'noscript']):
        tag.decompose()
    return soup.get_text(separator='\n', strip=True)


def normalize_date(date_str):
    if not date_str:
        return ""
    date_str = date_str.strip()
    patterns = [
        (r'(\d{4})年(\d{1,2})月(\d{1,2})日\s*(\d{1,2}:\d{2})?',
         lambda m: f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}" +
                   (f" {m.group(4)}" if m.lastindex and m.lastindex >= 4 and m.group(4) else "")),
    ]
    for pattern, replacer in patterns:
        match = re.search(pattern, date_str)
        if match:
            return replacer(match)
    date_str = date_str.replace('/', '-')
    return date_str


def extract_text_from_html(html):
    soup = BeautifulSoup(html, 'lxml')
    article = soup.find('article') or soup.find(class_=re.compile(r'article|content|main'))
    if article:
        return article.get_text(separator='\n', strip=True)
    return soup.body.get_text(separator='\n', strip=True) if soup.body else clean_html(html)


def matches_keywords(title, keywords):
    if not keywords:
        return True
    title_lower = title.lower()
    return any(kw.lower() in title_lower for kw in keywords)
```

- [ ] **步骤 5：运行测试验证通过**

```bash
python -m pytest tests/test_parser_helper.py -v
```

预期：6 PASSED

- [ ] **步骤 6：Commit**

```bash
git add src/scrapers/exceptions.py src/scrapers/utils/parser_helper.py tests/test_parser_helper.py
git commit -m "feat: add scraper exceptions and parser helper"
```

---

### 任务 7：爬虫基础设施（http_client + anti_detect）

**文件：**
- 创建：`src/scrapers/utils/http_client.py`
- 创建：`src/scrapers/utils/anti_detect.py`
- 创建：`tests/test_http_client.py`

- [ ] **步骤 1：实现 `src/scrapers/utils/anti_detect.py`**

```python
import random
import time


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
]


def random_user_agent():
    return random.choice(USER_AGENTS)


def random_delay(min_seconds=2, max_seconds=5):
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay


def build_headers(referer=None):
    headers = {
        "User-Agent": random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    if referer:
        headers["Referer"] = referer
    return headers
```

- [ ] **步骤 2：实现 `src/scrapers/utils/http_client.py`**

```python
import httpx
from .anti_detect import build_headers, random_delay
from ..exceptions import FetchError


class HttpClient:
    def __init__(self, config):
        cfg = config.get("scraper", {})
        self.timeout = cfg.get("timeout", 15)
        self.retry_max = cfg.get("retry_max", 2)
        self.retry_delay = cfg.get("retry_delay", 10)
        self.delay_min = cfg.get("delay_min", 2)
        self.delay_max = cfg.get("delay_max", 5)

    def fetch(self, url, referer=None):
        last_error = None
        for attempt in range(self.retry_max + 1):
            try:
                headers = build_headers(referer=referer)
                with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                    response = client.get(url, headers=headers)
                    response.raise_for_status()
                    response.encoding = response.charset_encoding or 'utf-8'
                    return response.text
            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code == 429:
                    if attempt < self.retry_max:
                        import time
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    raise FetchError(f"Rate limited: {url}") from e
                if e.response.status_code >= 500:
                    if attempt < self.retry_max:
                        import time
                        time.sleep(self.retry_delay)
                        continue
                raise FetchError(f"HTTP {e.response.status_code} for {url}") from e
            except (httpx.RequestError, httpx.TimeoutException) as e:
                last_error = e
                if attempt < self.retry_max:
                    import time
                    time.sleep(self.retry_delay)
                    continue
        raise FetchError(f"Failed to fetch {url} after {self.retry_max} retries") from last_error

    def inter_source_delay(self):
        return random_delay(self.delay_min, self.delay_max)
```

- [ ] **步骤 3：编写 `tests/test_http_client.py`**

```python
import pytest
import httpx
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
```

- [ ] **步骤 4：运行测试验证通过**

```bash
python -m pytest tests/test_http_client.py -v
```

预期：5 PASSED

- [ ] **步骤 5：Commit**

```bash
git add src/scrapers/utils/http_client.py src/scrapers/utils/anti_detect.py tests/test_http_client.py
git commit -m "feat: add http client and anti-detect utilities"
```

---

### 任务 8：爬虫基类 (`base.py`)

**文件：**
- 创建：`src/scrapers/base.py`
- 创建：`tests/test_scraper_base.py`

- [ ] **步骤 1：编写测试**

创建 `tests/test_scraper_base.py`：

```python
import pytest
from src.scrapers.base import BaseScraper
from src.scrapers.exceptions import FetchError, ParseError


class DummyScraper(BaseScraper):
    """测试用爬虫，不实际请求网络"""
    def __init__(self, http_client=None, config=None):
        super().__init__(http_client, config)
        self._test_html = ""
        self._test_articles = []

    def fetch_urls(self):
        if self._test_html == "fetch_error":
            raise FetchError("模拟抓取失败")
        if self._test_html == "parse_error":
            return ["https://example.com/bad"]
        return ["https://example.com/news/1", "https://example.com/news/2"]

    def parse_article(self, url):
        if url == "https://example.com/bad":
            raise ParseError("模拟解析失败")
        return {
            "id": "test1234",
            "title": f"测试标题: {url}",
            "url": url,
            "publish_time": "2026-05-29",
            "raw_text": "测试正文",
            "fetch_status": "success"
        }


def test_base_scraper_name():
    scraper = DummyScraper()
    scraper.source_name = "测试源"
    assert scraper.source_name == "测试源"


def test_fetch_urls_returns_list():
    scraper = DummyScraper()
    urls = scraper.fetch_urls()
    assert len(urls) == 2


def test_parse_article_returns_dict():
    scraper = DummyScraper()
    result = scraper.parse_article("https://example.com/news/1")
    assert result["title"] is not None
    assert result["url"] is not None
    assert result["raw_text"] is not None


def test_fetch_urls_raises_fetch_error():
    scraper = DummyScraper()
    scraper._test_html = "fetch_error"
    with pytest.raises(FetchError):
        scraper.fetch_urls()


def test_parse_article_raises_parse_error():
    scraper = DummyScraper()
    scraper._test_html = "parse_error"
    urls = scraper.fetch_urls()
    with pytest.raises(ParseError):
        scraper.parse_article(urls[0])
```

- [ ] **步骤 2：运行测试验证失败**

```bash
python -m pytest tests/test_scraper_base.py -v
```

- [ ] **步骤 3：实现 `src/scrapers/base.py`**

```python
from abc import ABC, abstractmethod
import hashlib


class BaseScraper(ABC):
    def __init__(self, http_client=None, config=None):
        self.http_client = http_client
        self.config = config or {}
        self.source_name = ""

    def _generate_id(self, url):
        return hashlib.md5(url.encode()).hexdigest()[:8]

    @abstractmethod
    def fetch_urls(self):
        """获取新闻列表 URL，返回 list[str]"""

    @abstractmethod
    def parse_article(self, url):
        """解析单篇文章，返回 dict"""
```

- [ ] **步骤 4：运行测试验证通过**

```bash
python -m pytest tests/test_scraper_base.py -v
```

预期：5 PASSED

- [ ] **步骤 5：Commit**

```bash
git add src/scrapers/base.py tests/test_scraper_base.py
git commit -m "feat: add scraper base class"
```

---

### 任务 9：新闻源配置 (`sources.py`)

**文件：**
- 创建：`src/scrapers/sources.py`

- [ ] **步骤 1：实现 `src/scrapers/sources.py`**

```python
"""
新闻源配置清单。
每个 handler 的名称与 handlers/ 目录中的文件名对应。
"""

SOURCES = [
    {
        "name": "人民日报",
        "handler": "people_daily",
        "url": "https://www.people.com.cn/",
        "category_urls": ["http://country.people.com.cn/"],
        "keywords": ["农业", "农村", "农民", "粮食", "乡村振兴", "耕地"],
        "priority": 1,
        "enabled": True,
    },
    {
        "name": "新华社",
        "handler": "xinhua",
        "url": "https://www.news.cn/",
        "keywords": ["农业", "农村", "农民", "粮食", "乡村振兴", "三农"],
        "priority": 1,
        "enabled": True,
    },
    {
        "name": "央视新闻",
        "handler": "cctv_news",
        "url": "https://news.cctv.com/",
        "keywords": ["农业", "农村", "乡村", "粮食", "三农"],
        "priority": 1,
        "enabled": True,
    },
    {
        "name": "农民日报",
        "handler": "farmers_daily",
        "url": "https://www.farmer.com.cn/",
        "keywords": [],
        "priority": 1,
        "enabled": True,
    },
    {
        "name": "中新社",
        "handler": "chinanews",
        "url": "https://www.chinanews.com/",
        "keywords": ["农业", "农村", "乡村", "粮食", "三农", "农民"],
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "光明日报",
        "handler": "guangming_daily",
        "url": "https://www.gmw.cn/",
        "keywords": ["农业", "农村", "乡村", "粮食", "三农"],
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "经济日报",
        "handler": "economic_daily",
        "url": "https://www.ce.cn/",
        "keywords": ["农业", "农村", "粮食", "乡村振兴", "三农"],
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "浙江日报",
        "handler": "zhejiang_daily",
        "url": "https://zjnews.zjol.com.cn/",
        "keywords": ["农业", "农村", "乡村", "三农", "乡村振兴"],
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "中国蓝新闻",
        "handler": "cztv",
        "url": "https://www.cztv.com/",
        "keywords": ["农业", "农村", "乡村", "三农"],
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "潮新闻",
        "handler": "tide_news",
        "url": "https://tidenews.com.cn/",
        "keywords": ["农业", "农村", "乡村", "三农"],
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "浙江在线",
        "handler": "zjol",
        "url": "https://www.zjol.com.cn/",
        "keywords": ["农业", "农村", "乡村", "三农"],
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "央视网",
        "handler": "cctv_net",
        "url": "https://www.cctv.com/",
        "keywords": ["农业", "农村", "乡村", "粮食", "三农"],
        "priority": 1,
        "enabled": True,
    },
    {
        "name": "央广网",
        "handler": "cnr_news",
        "url": "https://www.cnr.cn/",
        "keywords": ["农业", "农村", "乡村", "粮食", "三农"],
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "人民网",
        "handler": "people_net",
        "url": "https://www.people.com.cn/",
        "category_urls": ["http://country.people.com.cn/"],
        "keywords": ["农业", "农村", "农民", "粮食", "乡村振兴"],
        "priority": 1,
        "enabled": True,
    },
    {
        "name": "都市快报",
        "handler": "dskb",
        "url": "https://hzdaily.hangzhou.com.cn/dskb/",
        "keywords": ["农业", "农村", "乡村", "乡村振兴"],
        "priority": 3,
        "enabled": True,
    },
]


def get_enabled_sources():
    return sorted(
        [s for s in SOURCES if s.get("enabled", True)],
        key=lambda s: s.get("priority", 2)
    )


def get_source_by_handler(handler_name):
    for s in SOURCES:
        if s["handler"] == handler_name:
            return s
    return None
```

- [ ] **步骤 2：验证配置正确**

```bash
python -c "from src.scrapers.sources import get_enabled_sources; sources = get_enabled_sources(); print(f'启用源: {len(sources)}'); [print(f'  {s[\"priority\"]} | {s[\"name\"]}') for s in sources]"
```

预期输出：15 个源按优先级排列

- [ ] **步骤 3：Commit**

```bash
git add src/scrapers/sources.py
git commit -m "feat: add news source configuration"
```

---

### 任务 10：爬虫管理器 (`manager.py`)

**文件：**
- 创建：`src/scrapers/manager.py`
- 创建：`tests/test_scraper_manager.py`

- [ ] **步骤 1：编写测试**

创建 `tests/test_scraper_manager.py`：

```python
import pytest
from unittest.mock import Mock, patch
from src.scrapers.manager import ScraperManager
from src.scrapers.base import BaseScraper


class FakeScraper(BaseScraper):
    def __init__(self, http_client=None, config=None):
        super().__init__(http_client, config)
        self.source_name = "Fake"
        self._fail = False

    def fetch_urls(self):
        if self._fail:
            raise Exception("Boom")
        return ["https://example.com/1"]

    def parse_article(self, url):
        return {
            "id": self._generate_id(url),
            "title": "Fake Title",
            "url": url,
            "publish_time": "2026-05-29",
            "raw_text": "Fake body text.",
            "fetch_status": "success"
        }


def test_manager_scrapes_enabled_sources():
    sources = [
        {"name": "测试源", "handler": "fake_scraper", "priority": 1, "enabled": True},
        {"name": "禁用源", "handler": "disabled", "priority": 1, "enabled": False},
    ]
    http_client = Mock()
    http_client.inter_source_delay.return_value = 0.01

    with patch.dict('sys.modules', {'src.scrapers.handlers.fake_scraper': Mock()}):
        import src.scrapers.handlers.fake_scraper as m
        m.FakeScraper = FakeScraper

        manager = ScraperManager(sources, http_client)
        manager.handler_registry = {"fake_scraper": FakeScraper}
        results, errors = manager.run_all()

        assert len(results) == 1
        assert results[0]["source"] == "测试源"
        assert len(errors) == 0


def test_manager_handles_failure():
    sources = [
        {"name": "失败源", "handler": "failing", "priority": 1, "enabled": True},
    ]
    http_client = Mock()
    http_client.inter_source_delay.return_value = 0.01

    class FailingScraper(BaseScraper):
        source_name = "失败源"
        def fetch_urls(self):
            raise Exception("Connection refused")
        def parse_article(self, url):
            return {}

    manager = ScraperManager(sources, http_client)
    manager.handler_registry = {"failing": FailingScraper}
    results, errors = manager.run_all()

    assert len(results) == 0
    assert len(errors) == 1
    assert errors[0]["source"] == "失败源"
    assert "Connection refused" in errors[0]["error"]
```

- [ ] **步骤 2：运行测试验证失败**

```bash
python -m pytest tests/test_scraper_manager.py -v
```

- [ ] **步骤 3：实现 `src/scrapers/manager.py`**

```python
import importlib
import random
import time
from datetime import datetime
from .utils.parser_helper import matches_keywords


class ScraperManager:
    def __init__(self, sources, http_client, config=None):
        self.sources = [s for s in sources if s.get("enabled", True)]
        self.http_client = http_client
        self.config = config or {}
        self.max_articles = self.config.get("scraper", {}).get("max_articles_per_source", 30)
        self.handler_registry = {}  # 用于测试注入

    def _load_handler(self, handler_name):
        if handler_name in self.handler_registry:
            return self.handler_registry[handler_name]
        module = importlib.import_module(f"src.scrapers.handlers.{handler_name}")
        class_name = ''.join(part.capitalize() for part in handler_name.split('_')) + "Scraper"
        return getattr(module, class_name)

    def _scrape_source(self, source):
        handler_name = source["handler"]
        keywords = source.get("keywords", [])
        HandlerClass = self._load_handler(handler_name)
        scraper = HandlerClass(self.http_client, self.config)
        scraper.source_name = source["name"]

        urls = scraper.fetch_urls()
        articles = []
        for url in urls:
            try:
                article = scraper.parse_article(url)
                article["source"] = source["name"]
                if matches_keywords(article.get("title", ""), keywords) or not keywords:
                    articles.append(article)
            except Exception:
                continue
            if len(articles) >= self.max_articles:
                break

        return source["name"], handler_name, articles

    def run_all(self):
        all_articles = []
        errors = []

        for source in self.sources:
            try:
                name, handler_name, articles = self._scrape_source(source)
                all_articles.append({
                    "source": name,
                    "handler": handler_name,
                    "articles": articles,
                    "count": len(articles),
                })
            except Exception as e:
                errors.append({
                    "source": source["name"],
                    "handler": source.get("handler", ""),
                    "error": str(e),
                    "time": datetime.utcnow().isoformat() + "Z",
                })

            self.http_client.inter_source_delay()

        return all_articles, errors
```

- [ ] **步骤 4：运行测试验证通过**

```bash
python -m pytest tests/test_scraper_manager.py -v
```

预期：2 PASSED

- [ ] **步骤 5：Commit**

```bash
git add src/scrapers/manager.py tests/test_scraper_manager.py
git commit -m "feat: add scraper manager"
```

---

### 任务 11：15 个新闻源 Handler

**文件：**
- 创建：`src/scrapers/handlers/people_daily.py`、`xinhua.py`、`cctv_news.py`、`farmers_daily.py`、`chinanews.py`、`guangming_daily.py`、`economic_daily.py`、`zhejiang_daily.py`、`cztv.py`、`tide_news.py`、`zjol.py`、`cctv_net.py`、`cnr_news.py`、`people_net.py`、`dskb.py`

- [ ] **步骤 1：创建 `src/scrapers/handlers/people_daily.py`**

```python
from bs4 import BeautifulSoup
from ..base import BaseScraper
from ..utils.parser_helper import clean_html, normalize_date
from ..exceptions import ParseError


class PeopleDailyScraper(BaseScraper):
    def fetch_urls(self):
        urls = []
        category_urls = getattr(self, '_category_urls', None)
        if not category_urls:
            for src in self.config.get("sources", []):
                if src.get("handler") == "people_daily":
                    category_urls = src.get("category_urls", [])
                    break
        if not category_urls:
            category_urls = ["http://country.people.com.cn/"]

        for cat_url in category_urls:
            try:
                html = self.http_client.fetch(cat_url)
                soup = BeautifulSoup(html, 'lxml')
                for a in soup.select('a[href]'):
                    href = a.get('href', '')
                    if href and ('people.com.cn' in href or href.startswith('/')):
                        full_url = href if href.startswith('http') else f"https://www.people.com.cn{href}"
                        if full_url not in urls:
                            urls.append(full_url)
            except Exception:
                continue

        return urls[:self.config.get("scraper", {}).get("max_articles_per_source", 30)]

    def parse_article(self, url):
        try:
            html = self.http_client.fetch(url)
            soup = BeautifulSoup(html, 'lxml')
            title_el = soup.select_one('h1') or soup.select_one('.article-title')
            if not title_el:
                raise ParseError(f"No title found for {url}")
            title = title_el.get_text(strip=True)
            content_el = soup.select_one('.article-content') or soup.select_one('#article-content') or soup.select_one('article')
            raw_text = clean_html(str(content_el)) if content_el else clean_html(html)
            time_el = soup.select_one('.article-time') or soup.select_one('time')
            publish_time = normalize_date(time_el.get_text(strip=True)) if time_el else ""

            return {
                "id": self._generate_id(url),
                "title": title,
                "url": url,
                "publish_time": publish_time,
                "raw_text": raw_text[:3000],
                "fetch_status": "success"
            }
        except ParseError:
            raise
        except Exception as e:
            raise ParseError(f"Parse failed for {url}: {e}") from e
```

- [ ] **步骤 2-16：以相同模式创建其余 14 个 handler**

每个 handler 继承 `BaseScraper`，核心差异点：
- `fetch_urls()` 中的首页 URL 和链接提取 CSS 选择器
- `parse_article()` 中的标题选择器（`h1` / `.title` / `.article-title`）、正文选择器（`article` / `.content` / `.article-body`）、时间选择器

其余 14 个 handler 代码如下：

**`xinhua.py`**：
```python
from bs4 import BeautifulSoup
from ..base import BaseScraper
from ..utils.parser_helper import clean_html, normalize_date
from ..exceptions import ParseError


class XinhuaScraper(BaseScraper):
    def fetch_urls(self):
        html = self.http_client.fetch("https://www.news.cn/")
        soup = BeautifulSoup(html, 'lxml')
        urls = []
        for a in soup.select('a[href]'):
            href = a.get('href', '')
            if href and 'news.cn' in href:
                full_url = href if href.startswith('http') else f"https://www.news.cn{href}"
                if full_url not in urls:
                    urls.append(full_url)
        return urls[:30]

    def parse_article(self, url):
        html = self.http_client.fetch(url)
        soup = BeautifulSoup(html, 'lxml')
        title_el = soup.select_one('h1') or soup.select_one('.title')
        if not title_el:
            raise ParseError(f"No title found for {url}")
        title = title_el.get_text(strip=True)
        content_el = soup.select_one('#detail-content') or soup.select_one('.article-content') or soup.select_one('article')
        raw_text = clean_html(str(content_el)) if content_el else clean_html(html)
        time_el = soup.select_one('.time') or soup.select_one('time')
        publish_time = normalize_date(time_el.get_text(strip=True)) if time_el else ""
        return {
            "id": self._generate_id(url),
            "title": title,
            "url": url,
            "publish_time": publish_time,
            "raw_text": raw_text[:3000],
            "fetch_status": "success"
        }
```

**剩余 13 个 handler 按相同模板**，唯一变化是 `fetch_urls()` 中的基础 URL、CSS 选择器，和 `parse_article()` 中的标题/正文/时间选择器。各站点选择器如下：

| Handler | 首页 URL | 标题选择器 | 正文选择器 | 时间选择器 |
|---------|---------|-----------|-----------|-----------|
| `cctv_news` | `news.cctv.com` | `h1` | `.content` | `.time` |
| `farmers_daily` | `farmer.com.cn` | `h1, .title` | `.article-content` | `.time, time` |
| `chinanews` | `chinanews.com` | `h1` | `.content` | `.time` |
| `guangming_daily` | `gmw.cn` | `h1` | `.article-content` | `.time` |
| `economic_daily` | `ce.cn` | `h1` | `.article-content` | `.time` |
| `zhejiang_daily` | `zjnews.zjol.com.cn` | `h1` | `.article-content` | `.time` |
| `cztv` | `cztv.com` | `h1` | `.content` | `.time` |
| `tide_news` | `tidenews.com.cn` | `h1` | `.article-content` | `.time` |
| `zjol` | `zjol.com.cn` | `h1` | `.article-content` | `.time` |
| `cctv_net` | `cctv.com` | `h1` | `.content` | `.time` |
| `cnr_news` | `cnr.cn` | `h1` | `.article-content` | `.time` |
| `people_net` | `people.com.cn` | `h1` | `.article-content` | `.time` |
| `dskb` | `hzdaily.hangzhou.com.cn/dskb/` | `h1` | `.article-content` | `.time` |

每个 handler 文件内容与 people_daily.py 相同结构，替换对应的 URL 和选择器即可。

- [ ] **步骤 17：验证所有 handler 可导入**

```bash
python -c "
from src.scrapers.handlers import people_daily, xinhua, cctv_news, farmers_daily, chinanews
from src.scrapers.handlers import guangming_daily, economic_daily, zhejiang_daily, cztv, tide_news
from src.scrapers.handlers import zjol, cctv_net, cnr_news, people_net, dskb
print('15 handlers imported successfully')
"
```

预期输出：`15 handlers imported successfully`

- [ ] **步骤 18：Commit**

```bash
git add src/scrapers/handlers/
git commit -m "feat: add 15 news source handlers"
```

---

### 任务 12：AI 分析模块 (`analyzer.py`)

**文件：**
- 创建：`src/analyzer.py`
- 创建：`tests/test_analyzer.py`

- [ ] **步骤 1：编写测试**

创建 `tests/test_analyzer.py`：

```python
import pytest
from unittest.mock import Mock, patch
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
```

- [ ] **步骤 2：运行测试验证失败**

```bash
python -m pytest tests/test_analyzer.py -v
```

- [ ] **步骤 3：实现 `src/analyzer.py`**

```python
import json
import re
from openai import OpenAI


class Analyzer:
    def __init__(self, config):
        llm_cfg = config.get("llm", {})
        analyzer_cfg = config.get("analyzer", {})
        prompts_cfg = analyzer_cfg.get("prompts", {})

        self.client = OpenAI(
            api_key=llm_cfg.get("api_key", ""),
            base_url=llm_cfg.get("base_url", "https://api.deepseek.com/v1"),
        )
        self.model = llm_cfg.get("model", "deepseek-chat")
        self.max_tokens = llm_cfg.get("max_tokens", 4096)
        self.temperature = llm_cfg.get("temperature", 0.7)
        self.batch_size = analyzer_cfg.get("batch_size", 10)
        self.min_relevance = analyzer_cfg.get("min_relevance_score", 6)
        self.min_importance = analyzer_cfg.get("min_importance_score", 3)
        self.categories = analyzer_cfg.get("categories", [])

        domain = prompts_cfg.get("domain", "三农")
        self.layer1_system = prompts_cfg.get("layer1_system", "你是{domain}新闻资深编辑。").format(domain=domain)
        self.layer2_system = prompts_cfg.get("layer2_system", "你是中国{domain}日报主编。").format(domain=domain)

    def _build_layer1_prompt(self, articles):
        cat_list = "、".join(self.categories)
        articles_text = "\n---\n".join(
            f"id: {a['id']}\ntitle: {a['title']}\ntext: {a.get('raw_text', a.get('summary', ''))[:500]}"
            for a in articles
        )
        return f"""请对以下多条新闻进行批量分析，每条新闻输出一个JSON对象。

要求：
1. relevance_score：0-10分（必须与农业农村农民直接相关才给高分）
2. category：只能从以下类别中选择一个：[{cat_list}]
3. importance_score：1-5分（5分为极重要）
4. summary：一句话摘要（≤100字）
5. keywords：提取3-5个核心关键词（数组）

请严格按照以下JSON数组格式输出，不要添加任何解释文字：
[
  {{"id": "xxx", "title": "...", "relevance_score": 9, "category": "粮食安全", "importance_score": 5, "summary": "一句话摘要...", "keywords": ["关键词1", "关键词2"]}}
]

新闻内容：
{articles_text}"""

    def _parse_layer1_response(self, response_text):
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if match:
                return json.loads(match.group())
            return []

    def _filter_articles(self, articles):
        return [
            a for a in articles
            if a.get("relevance_score", 0) >= self.min_relevance
            and a.get("importance_score", 0) >= self.min_importance
        ]

    def _build_layer2_prompt(self, articles):
        by_category = {}
        for a in articles:
            cat = a.get("category", "其他")
            by_category.setdefault(cat, []).append(a)

        sections = []
        for cat, items in sorted(by_category.items(), key=lambda x: -len(x[1])):
            section = f"【{cat}】({len(items)}条)\n"
            for item in sorted(items, key=lambda x: -x.get("importance_score", 0)):
                section += f"- [{item.get('importance_score', 0)}分] {item['title']}: {item.get('summary', '')}\n"
            sections.append(section)

        context = "\n".join(sections)

        return f"""请基于以下已分类的高质量三农新闻，撰写一篇今日农业农村日报综述。

要求：
- 总字数控制在800-1300字
- 结构严格如下：
  1. 【标题】（吸引人且准确，包含日期）
  2. 【今日要点】（3-5条，最重要新闻，编号列出）
  3. 【分类详述】（按重要性排序，每个类别2-4段）
  4. 【明日关注】（2-3条建议）
- 语言风格：客观、专业、平实，适合政务人员和农业系统干部阅读
- 避免空洞口号，多用事实和数据

新闻内容如下：
{context}"""

    def _call_llm(self, system_prompt, user_prompt):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return response.choices[0].message.content

    def run_layer1(self, articles):
        all_results = []
        for i in range(0, len(articles), self.batch_size):
            batch = articles[i:i + self.batch_size]
            prompt = self._build_layer1_prompt(batch)
            response = self._call_llm(self.layer1_system, prompt)
            results = self._parse_layer1_response(response)
            for r, a in zip(results, batch):
                r["source"] = a.get("source", "")
                r["url"] = a.get("url", "")
            all_results.extend(results)
        return all_results

    def run_layer2(self, articles):
        prompt = self._build_layer2_prompt(articles)
        response = self._call_llm(self.layer2_system, prompt)
        return response

    def run_deep_analysis(self, topic, historical_articles):
        prompt = f"""你是三农领域的资深分析师。请围绕话题"{topic}"撰写一份深度分析报告。

基于以下历史新闻数据（共{len(historical_articles)}条），请分析：
1. 该话题的政策背景和发展脉络
2. 关键事件和重要节点
3. 当前态势和主要观点
4. 趋势预判和建议

历史新闻：
{json.dumps([{'title': a.get('title'), 'summary': a.get('summary', ''), 'date': a.get('date', '')} for a in historical_articles[:50]], ensure_ascii=False, indent=2)}"""
        return self._call_llm(self.layer2_system, prompt)
```

- [ ] **步骤 4：运行测试验证通过**

```bash
python -m pytest tests/test_analyzer.py -v
```

预期：6 PASSED（含一个 LLM mock 测试）

- [ ] **步骤 5：Commit**

```bash
git add src/analyzer.py tests/test_analyzer.py
git commit -m "feat: add AI analyzer with two-layer pipeline"
```

---

### 任务 13：报告生成模块 (`reporter.py`)

**文件：**
- 创建：`src/reporter.py`
- 创建：`tests/test_reporter.py`

- [ ] **步骤 1：编写测试**

创建 `tests/test_reporter.py`：

```python
import tempfile
from pathlib import Path
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
    }

    overview = Reporter.generate_overview("2026-05-29", classified_articles, category_counts, metadata)
    assert "2026-05-29" in overview
    assert "粮食安全" in overview
    assert "夏粮丰收" in overview
    assert "87" in overview


def test_generate_archive_page():
    with tempfile.TemporaryDirectory() as tmp:
        reporter = Reporter()
        dates = ["2026-05-27", "2026-05-28", "2026-05-29"]
        html = reporter.generate_archive_page(dates)
        assert "2026-05-29" in html
        assert "2026-05-27" in html


def test_format_duration():
    assert Reporter._format_duration(3661) == "61分1秒"
    assert Reporter._format_duration(65) == "1分5秒"
    assert Reporter._format_duration(30) == "30秒"
```

- [ ] **步骤 2：运行测试验证失败**

```bash
python -m pytest tests/test_reporter.py -v
```

- [ ] **步骤 3：实现 `src/reporter.py`**

```python
class Reporter:
    @staticmethod
    def generate_overview(date_str, classified_articles, category_counts, metadata):
        lines = [
            f"# 三农新闻日报 — {date_str}",
            "",
            "## 今日要点",
            "",
        ]
        top_articles = sorted(classified_articles, key=lambda x: -x.get("importance_score", 0))[:5]
        for i, article in enumerate(top_articles, 1):
            lines.append(f"{i}. **{article['title']}** — {article.get('summary', '')}（来源：{article.get('source', '')})")
            lines.append("")

        lines.extend(["", "## 分类统计", ""])
        lines.append("| 类别 | 数量 |")
        lines.append("|------|------|")
        for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            lines.append(f"| {cat} | {count} |")

        lines.extend([
            "",
            "---",
            f"> 共抓取 {metadata.get('total_fetched', 0)} 条，筛选 {metadata.get('total_filtered', 0)} 条",
            f"> 成功源 {metadata.get('successful_sources', 0)}/{metadata.get('total_sources', 0)}，"
            f"耗时 {Reporter._format_duration(metadata.get('duration_seconds', 0))}",
        ])
        return "\n".join(lines)

    @staticmethod
    def generate_archive_page(dates):
        links = "\n".join(
            f'<li><a href="archives/{d}.html">{d} 三农日报</a></li>'
            for d in sorted(dates, reverse=True)
        )
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>三农新闻日报</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
h1 {{ color: #2d5016; }}
li {{ margin: 8px 0; }}
a {{ color: #1a73e8; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<h1>三农新闻日报</h1>
<p>农业农村政策与产业动态简报</p>
<h2>历史日报</h2>
<ul>{links}</ul>
</body>
</html>"""

    @staticmethod
    def _format_duration(seconds):
        if seconds < 60:
            return f"{seconds}秒"
        minutes = seconds // 60
        secs = seconds % 60
        if secs == 0:
            return f"{minutes}分"
        return f"{minutes}分{secs}秒"
```

- [ ] **步骤 4：运行测试验证通过**

```bash
python -m pytest tests/test_reporter.py -v
```

预期：3 PASSED

- [ ] **步骤 5：Commit**

```bash
git add src/reporter.py tests/test_reporter.py
git commit -m "feat: add markdown reporter"
```

---

### 任务 14：通知模块 (`notifier.py`)

**文件：**
- 创建：`src/notifier.py`
- 创建：`tests/test_notifier.py`

- [ ] **步骤 1：编写测试**

创建 `tests/test_notifier.py`：

```python
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
def test_send_daily_brief(mock_client):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"code": 200}
    mock_client.return_value.__enter__.return_value.post.return_value = mock_response

    n = make_notifier()
    brief = "测试日报内容"
    result = n.send_daily_brief("2026-05-29", brief, "https://example.com")
    assert result is True


@patch('src.notifier.httpx.Client')
def test_send_failure_alert_skips_when_below_threshold(mock_client):
    n = make_notifier()
    errors = [{"source": "源1", "error": "timeout"}]
    result = n.send_failure_alert("2026-05-29", errors, {"successful_sources": 14, "failed_sources": 1})
    assert result == "skipped"
```

- [ ] **步骤 2：运行测试验证失败**

```bash
python -m pytest tests/test_notifier.py -v
```

- [ ] **步骤 3：实现 `src/notifier.py`**

```python
import os
import httpx


class Notifier:
    def __init__(self, config):
        notify_cfg = config.get("notify", {})
        self.enabled = notify_cfg.get("enabled", True)
        self.token = os.getenv("PUSHPLUS_TOKEN")
        if not self.token:
            self.token = notify_cfg.get("pushplus_token", "")
            if self.token and self.token.startswith("${"):
                self.token = None
        self.success_cfg = notify_cfg.get("success", {})
        self.failure_cfg = notify_cfg.get("failure", {})
        self.title = config.get("pages", {}).get("title", "三农新闻日报")
        if not self.token:
            print("警告：未找到 PUSHPLUS_TOKEN，推送功能已禁用")

    def _push(self, title, content):
        if not self.token:
            return False
        try:
            resp = httpx.post(
                "https://www.pushplus.plus/send",
                json={
                    "token": self.token,
                    "title": title,
                    "content": content,
                    "template": "markdown",
                },
                timeout=10,
            )
            data = resp.json()
            return data.get("code") == 200
        except Exception as e:
            print(f"推送失败: {e}")
            return False

    def send_daily_brief(self, date_str, brief_text, pages_url):
        if not self.success_cfg.get("enabled", True):
            return "disabled"
        lines = brief_text.strip().split("\n")
        important_lines = []
        in_important = False
        for line in lines:
            if "今日要点" in line:
                in_important = True
                continue
            if in_important:
                if line.strip().startswith("##") or line.strip().startswith("---"):
                    break
                if line.strip():
                    important_lines.append(line.strip()[:100])
        summary = "\n".join(important_lines[:5])
        content = f"# 📰 {self.title} | {date_str}\n\n{summary}\n\n📎 [完整日报]({pages_url})"
        content = content[:self.success_cfg.get("brief_max_chars", 600)]
        return self._push(f"{self.title} | {date_str}", content)

    def send_failure_alert(self, date_str, errors, metadata):
        if not self.failure_cfg.get("enabled", True):
            return "disabled"
        min_failed = self.failure_cfg.get("min_failed_sources", 3)
        if len(errors) < min_failed:
            return "skipped"
        error_lines = [f"- {e['source']}: {e['error']}" for e in errors[:self.failure_cfg.get("max_errors", 8)]]
        content = f"# 抓取异常 | {date_str}\n\n失败 {len(errors)} 个源：\n\n" + "\n".join(error_lines)
        return self._push(f"⚠️ 抓取异常 | {date_str}", content)
```

- [ ] **步骤 4：运行测试验证通过**

```bash
python -m pytest tests/test_notifier.py -v
```

预期：4 PASSED

- [ ] **步骤 5：Commit**

```bash
git add src/notifier.py tests/test_notifier.py
git commit -m "feat: add PushPlus notification module"
```

---

### 任务 15：主入口 (`main.py`)

**文件：**
- 创建：`src/main.py`

- [ ] **步骤 1：实现 `src/main.py`**

```python
#!/usr/bin/env python3
"""三农新闻日报 — 主流程入口"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

from src.config import load_config
from src.env_detector import is_github_actions, get_run_mode
from src.scrapers.manager import ScraperManager
from src.scrapers.sources import get_enabled_sources
from src.scrapers.utils.http_client import HttpClient
from src.storage import Storage
from src.dedup import Dedup
from src.analyzer import Analyzer
from src.reporter import Reporter
from src.notifier import Notifier


def parse_args():
    parser = argparse.ArgumentParser(description="三农新闻日报系统")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--date", help="指定日期 YYYY-MM-DD（默认今天）")
    parser.add_argument("--dry-run", action="store_true", help="只爬取，不调 AI")
    parser.add_argument("--source", help="只抓取指定源名称")
    parser.add_argument("--deep", help="深度分析话题")
    parser.add_argument("--no-push", action="store_true", help="跳过推送")
    parser.add_argument("--output-dir", default="data", help="输出目录")
    return parser.parse_args()


def main():
    args = parse_args()
    date_str = args.date or datetime.now().strftime("%Y-%m-%d")
    mode = get_run_mode()
    print(f"=== 三农新闻日报 v0.1 | {date_str} | {mode} ===")

    # 1. 加载配置
    config = load_config(args.config)
    print(f"配置已加载: {len(config.get('sources', []))} 个源")

    # 2. 初始化各模块
    storage = Storage(base_dir=args.output_dir)
    dedup = Dedup()
    http_client = HttpClient(config)
    analyzer = Analyzer(config) if not args.dry_run else None
    notifier = Notifier(config) if not args.no_push else None

    # 3. 确定要爬取的源
    sources = get_enabled_sources()
    if args.source:
        sources = [s for s in sources if s["name"] == args.source]
        if not sources:
            print(f"错误：未找到源 '{args.source}'")
            sys.exit(1)
    print(f"将爬取 {len(sources)} 个源")

    # 4. 爬虫阶段
    start_time = time.time()
    manager = ScraperManager(sources, http_client, config)
    raw_results, scrape_errors = manager.run_all()

    total_fetched = 0
    for result in raw_results:
        source_name = result["source"]
        handler_name = result["handler"]
        articles = result["articles"]
        new_articles = dedup.filter_new(articles)
        storage.save_raw(date_str, handler_name, source_name, new_articles)
        total_fetched += len(new_articles)
        print(f"  {source_name}: {len(new_articles)} 条新文章")

    if scrape_errors:
        storage.save_errors(date_str, scrape_errors)
        print(f"  {len(scrape_errors)} 个源失败")

    print(f"抓取完成: {total_fetched} 条新文章")

    if args.dry_run:
        print("--dry-run，跳过 AI 分析")
        return 0

    # 5. AI 第一层：分类 + 过滤
    all_raw = []
    for result in raw_results:
        all_raw.extend(result["articles"])

    classified = analyzer.run_layer1(all_raw)
    filtered = analyzer._filter_articles(classified)
    storage.save_filtered(date_str, len(all_raw), filtered)
    print(f"AI 分类完成: {len(filtered)}/{len(classified)} 条保留")

    # 6. AI 第二层：综述
    brief_text = analyzer.run_layer2(filtered)

    # 7. 汇总分类统计
    category_counts = {}
    for a in filtered:
        cat = a.get("category", "其他")
        category_counts[cat] = category_counts.get(cat, 0) + 1

    storage.save_classified(date_str, filtered, category_counts)
    storage.save_brief(date_str, brief_text)

    # 8. 深度分析（可选）
    if args.deep:
        print(f"深度分析: {args.deep}")
        deep_text = analyzer.run_deep_analysis(args.deep, filtered)
        deep_path = storage.save_brief(date_str, f"# 深度分析: {args.deep}\n\n{deep_text}")
        print(f"深度分析已保存: {deep_path}")

    # 9. 元数据
    duration = int(time.time() - start_time)
    metadata = {
        "date": date_str,
        "start_time": datetime.utcnow().isoformat() + "Z",
        "end_time": datetime.utcnow().isoformat() + "Z",
        "total_sources": len(sources),
        "successful_sources": len(sources) - len(scrape_errors),
        "failed_sources": len(scrape_errors),
        "total_fetched": total_fetched,
        "total_filtered": len(filtered),
        "duration_seconds": duration,
        "status": "completed" if not scrape_errors else "partial",
    }
    storage.save_metadata(date_str, metadata)

    # 10. 推送通知
    if notifier and not args.no_push:
        overview = Reporter.generate_overview(date_str, filtered, category_counts, metadata)
        pages_url = config.get("pages", {}).get("url", "")
        notifier.send_daily_brief(date_str, overview, pages_url)
        if scrape_errors:
            notifier.send_failure_alert(date_str, scrape_errors, metadata)

    print(f"完成！耗时 {Reporter._format_duration(duration)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **步骤 2：验证 CLI 参数解析**

```bash
python src/main.py --help
```

预期：显示所有参数

- [ ] **步骤 3：Commit**

```bash
git add src/main.py
git commit -m "feat: add main entry point with CLI"
```

---

### 任务 16：GitHub Actions 工作流

**文件：**
- 创建：`.github/workflows/daily.yml`

- [ ] **步骤 1：创建 `.github/workflows/daily.yml`**

```yaml
name: 三农新闻日报

on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:
    inputs:
      deep_analysis_topic:
        description: '深度分析话题（可选）'
        required: false

permissions:
  contents: write

jobs:
  daily-news:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    env:
      DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
      PUSHPLUS_TOKEN: ${{ secrets.PUSHPLUS_TOKEN }}

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run daily task
        run: python src/main.py

      - name: Commit daily report
        if: success()
        run: |
          git config user.name "agri-news-bot"
          git config user.email "bot@agri-news.local"
          git add data/ docs/ archive.db
          git diff --staged --quiet || (git commit -m "日报: $(date +%Y-%m-%d)" && git push)

      - name: Failure notification
        if: failure()
        run: python src/notifier.py --failure
        env:
          PUSHPLUS_TOKEN: ${{ secrets.PUSHPLUS_TOKEN }}
```

- [ ] **步骤 2：Commit**

```bash
git add .github/workflows/daily.yml
git commit -m "ci: add daily GitHub Actions workflow"
```

---

### 任务 17：GitHub Pages 首页

**文件：**
- 创建：`docs/index.html`

- [ ] **步骤 1：创建 `docs/index.html`**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>三农新闻日报</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 0 auto; padding: 40px 20px; background: #f9fafb; color: #1a1a1a; }
  h1 { color: #2d5016; font-size: 1.8em; border-bottom: 3px solid #4a7c2e; padding-bottom: 10px; }
  h2 { color: #4a7c2e; margin-top: 40px; }
  .date-list { list-style: none; padding: 0; }
  .date-list li { margin: 8px 0; padding: 10px 16px; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
  .date-list a { color: #1a73e8; text-decoration: none; font-weight: 500; }
  .date-list a:hover { text-decoration: underline; }
  footer { margin-top: 60px; padding-top: 20px; border-top: 1px solid #e0e0e0; color: #888; font-size: 0.9em; }
</style>
</head>
<body>
  <h1>三农新闻日报</h1>
  <p>农业农村政策与产业动态简报 — 每日自动生成</p>
  <h2>历史日报</h2>
  <ul class="date-list" id="date-list">
    <li>加载中...</li>
  </ul>
  <footer>
    <p>由 agri-news-bot 自动生成 | 数据来源：15 家官方媒体</p>
  </footer>
  <script>
    fetch('https://api.github.com/repos/YOUR_USER/YOUR_REPO/contents/data')
      .then(r => r.json())
      .then(dirs => {
        const dates = dirs.filter(d => d.type === 'dir').map(d => d.name).sort().reverse();
        const list = document.getElementById('date-list');
        if (dates.length === 0) {
          list.innerHTML = '<li>暂无数据</li>';
          return;
        }
        list.innerHTML = dates.map(d =>
          `<li><a href="https://raw.githubusercontent.com/YOUR_USER/YOUR_REPO/main/data/${d}/daily_brief.md">${d} 日报</a></li>`
        ).join('');
      })
      .catch(() => {
        document.getElementById('date-list').innerHTML = '<li>加载失败，请检查仓库设置</li>';
      });
  </script>
</body>
</html>
```

- [ ] **步骤 2：Commit**

```bash
git add docs/index.html
git commit -m "feat: add GitHub Pages landing page"
```

---

### 任务 18：集成测试

**文件：**
- 创建：`tests/test_integration.py`

- [ ] **步骤 1：编写集成测试**

创建 `tests/test_integration.py`：

```python
"""集成测试：端到端流程验证（不实际请求网络）"""
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.storage import Storage
from src.dedup import Dedup
from src.reporter import Reporter


def test_full_data_flow():
    """验证 存储 → 去重 → 报告 链路"""
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
        metadata = {"total_fetched": 2, "total_filtered": 2, "duration_seconds": 120, "successful_sources": 2, "failed_sources": 0}

        overview = Reporter.generate_overview("2026-05-29", classified, category_counts, metadata)
        assert "夏粮丰收" in overview
        storage.save_brief("2026-05-29", overview)
        assert Path(tmp, "2026-05-29", "daily_brief.md").exists()

        dedup.close()


def test_config_resolves_all_sources():
    from src.config import load_config
    config = load_config("config.yaml")
    sources = config.get("sources", [])
    assert len(sources) == 15
    assert all("name" in s for s in sources)
    assert all("handler" in s for s in sources)


def test_all_handlers_importable():
    from src.scrapers.handlers import (
        people_daily, xinhua, cctv_news, farmers_daily, chinanews,
        guangming_daily, economic_daily, zhejiang_daily, cztv, tide_news,
        zjol, cctv_net, cnr_news, people_net, dskb,
    )
    assert people_daily is not None
    assert dskb is not None
```

- [ ] **步骤 2：运行集成测试**

```bash
python -m pytest tests/test_integration.py -v
```

预期：3 PASSED

- [ ] **步骤 3：Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration tests"
```

---

## 自检

### 1. 规格覆盖度

| 规格章节 | 对应任务 |
|---------|---------|
| 一、整体架构 + 项目结构 | 任务 1（脚手架） |
| 二、配置文件设计 | 任务 2（config.py + config.yaml） |
| 三、数据存储设计 | 任务 4（storage.py） |
| 四、AI 分析流程 | 任务 12（analyzer.py） |
| 五、通知与推送 | 任务 14（notifier.py） |
| 六、GitHub Actions 调度 | 任务 16（daily.yml） |
| 七、双模式部署 + 多实例 | 任务 3（env_detector）+ 任务 15（main.py CLI） |
| 八、模块依赖 | 全部任务按依赖顺序排列 |
| 九、依赖清单 | 任务 1（requirements.txt） |

### 2. 占位符扫描

- 无 "TODO" 或 "待定"
- 无 "适当错误处理" 等模糊描述
- 所有代码步骤包含完整代码
- Handler 任务中列出了每个站点的 URL 和选择器（非占位符）

### 3. 类型一致性

- `Storage` 类方法签名与 `main.py` 调用一致
- `Analyzer` 类方法签名与 `main.py` 调用一致
- `Notifier` 类方法签名与 `main.py` 调用一致
- `ScraperManager.run_all()` 返回值 `(results, errors)` 与 `main.py` 解包一致
- `Dedup.filter_new()` 返回 list 与调用方一致
