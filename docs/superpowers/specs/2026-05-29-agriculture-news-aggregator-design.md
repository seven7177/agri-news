# 三农新闻聚合分析系统 — 设计规格说明

> 日期：2026-05-29 | 状态：已确认

---

## 一、整体架构

```
┌──────────────────────────────────────────────────────────────────┐
│                    GitHub Actions (每天 8:00)                      │
│                                                                  │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────┐   ┌────┐ │
│  │ 爬虫模块  │──▶│ 存储层   │──▶│ AI 分析  │──▶│ 报告  │──▶│监控│ │
│  │ 串行15源 │   │storage.py│   │         │   │生成  │   │通知│ │
│  │ 随机延时  │   │ 统一读写  │   │ 第一层  │   │      │   │    │ │
│  │ 失败重试  │   │          │   │  分类+  │   │      │   │    │ │
│  └──────────┘   └──────────┘   │  过滤   │   └──────┘   └────┘ │
│       │              │         │    │     │              │      │
│       │              │         │    ▼     │              │      │
│       │              │         │ 第二层   │              │      │
│       │              │         │  综述    │              │      │
│       │              │         │ (+可选   │              │      │
│       │              │         │  深度)   │              │      │
│       │              │         └──────────┘              │      │
│       ▼              ▼                                    │      │
│  SQLite 去重    data/YYYY-MM-DD/                          │      │
│               raw/ / filtered.json / classified.json       │      │
│               / daily_brief.md / metadata.json             │      │
└──────────────────────────────────────────────────────────────────┘
```

### 技术选型

| 层级 | 技术 |
|------|------|
| 语言 | Python 3.12 |
| 爬虫 | httpx + BeautifulSoup + lxml |
| 存储 | JSON 文件 + SQLite |
| AI | DeepSeek API（可切换智谱/通义/OpenAI） |
| 调度 | GitHub Actions |
| 推送 | PushPlus 微信公众号模板消息 |
| 前端 | GitHub Pages 静态站点 |

### 项目结构

```
agri-news/
├── config.yaml                      # 默认：三农配置
├── configs/                         # 可选：其他领域配置模板
│   └── tech_news.example.yaml
├── src/
│   ├── __init__.py
│   ├── main.py                # 主流程编排 + CLI 入口
│   ├── config.py              # 读取 config.yaml + 环境变量
│   ├── env_detector.py         # 运行环境检测（本地/GitHub Actions）
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base.py            # 基类，定义标准接口
│   │   ├── manager.py         # 爬虫管理器（调度、重试、延时）
│   │   ├── sources.py         # 15 个新闻源配置清单
│   │   ├── handlers/          # 各站点具体解析器
│   │   │   ├── people_daily.py
│   │   │   ├── xinhua.py
│   │   │   ├── cctv_news.py
│   │   │   ├── farmers_daily.py
│   │   │   ├── chinanews.py
│   │   │   ├── guangming_daily.py
│   │   │   ├── economic_daily.py
│   │   │   ├── zhejiang_daily.py
│   │   │   ├── cztv.py
│   │   │   ├── tide_news.py
│   │   │   ├── zjol.py
│   │   │   ├── cctv_net.py
│   │   │   ├── cnr_news.py
│   │   │   ├── people_net.py
│   │   │   └── dskb.py
│   │   ├── utils/
│   │   │   ├── http_client.py   # 统一请求（随机UA、重试、超时）
│   │   │   ├── parser_helper.py # 通用解析（清洗、日期标准化）
│   │   │   └── anti_detect.py   # 反检测策略
│   │   └── exceptions.py
│   ├── storage.py             # 统一数据读写层
│   ├── dedup.py               # SQLite URL 去重
│   ├── analyzer.py            # AI 分析（两层）
│   ├── reporter.py            # Markdown 报告生成
│   └── notifier.py            # 微信推送 + 失败告警
├── data/                      # 按天存储
│   └── 2026-05-29/
│       ├── raw/               # 按来源拆分
│       │   ├── people_daily.json
│       │   └── ...
│       ├── filtered.json      # AI 过滤结果
│       ├── classified.json    # AI 分类 + 摘要
│       ├── daily_brief.md     # 最终日报
│       ├── errors.json        # 抓取失败记录
│       └── metadata.json      # 任务统计
├── archive.db                 # 去重 + 归档数据库
├── docs/                      # GitHub Pages 站点
│   ├── index.html
│   └── archives/
├── .github/workflows/daily.yml
├── requirements.txt
├── requirements-dev.txt             # 本地开发额外依赖
├── .env.example                     # 本地环境变量模板
├── .gitignore
└── README.md                        # 含本地部署文档
```

### 数据流全链路

```
main.py 启动
  │
  ├─ 1. config.py → 读取 config.yaml，解析 ${ENV_VAR} 占位符
  │
  ├─ 2. manager.py → 串行遍历 sources.py 配置 → 各 handler 抓取
  │        │
  │        └─ http_client.py (随机UA、请求重试)
  │        └─ anti_detect.py (Referer 伪装、随机延时 2~5s)
  │        └─ parser_helper.py (正文清洗、日期标准化)
  │        └─ 失败 → sleep(10s) → 重试(最多2次) → 记录 errors.json
  │
  ├─ 3. dedup.py → SQLite url_hash 查重 → 过滤已抓 → 新增写入
  │
  ├─ 4. storage.py → 写入 data/日期/raw/<source>.json + metadata.json
  │
  ├─ 5. analyzer.py (第1层) → 批量送 DeepSeek
  │        │
  │        ├─ 分批 10 条/批
  │        ├─ 分类 + 相关性评分 + 重要性评分 + 摘要 + 关键词
  │        └─ 过滤不相关/低分 → 写入 filtered.json
  │
  ├─ 6. analyzer.py (第2层) → DeepSeek 生成日报综述
  │        │
  │        └─ 按分类排序 context → 生成 800-1300 字综述
  │
  ├─ 7. storage.py → 写入 classified.json + daily_brief.md + metadata.json
  │
  ├─ 8. notifier.py → PushPlus 微信推送摘要 + 成功通知
  │
  └─ 9. git commit & push → GitHub Pages 自动更新
```

---

## 二、配置文件设计 (`config.yaml`)

```yaml
# ===== 大模型配置 =====
llm:
  provider: deepseek
  api_key: ${DEEPSEEK_API_KEY}
  base_url: https://api.deepseek.com/v1
  model: deepseek-chat
  max_tokens: 4096
  temperature: 0.7

# ===== 新闻源配置 =====
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

  # ... 其余 13 个源类似配置（优先级 1-3，enabled 可关闭）

# ===== 爬虫配置 =====
scraper:
  delay_min: 2
  delay_max: 5
  retry_max: 2
  retry_delay: 10
  timeout: 15
  max_articles_per_source: 30

# ===== AI 分析配置 =====
analyzer:
  batch_size: 10           # 第1层每批处理条数
  min_relevance_score: 6   # 相关性低于6分过滤
  min_importance_score: 3  # 重要性低于3分过滤
  categories:
    - 政策法规
    - 粮食安全
    - 产业发展
    - 乡村振兴
    - 科技兴农
    - 生态环保
    - 农产品市场
    - 其他

  # Prompt 模板，支持 {domain} 等变量替换，便于切换领域
  prompts:
    domain: 三农
    layer1_system: "你是{domain}新闻资深编辑。"
    layer2_system: "你是中国{domain}日报主编。"

# ===== 通知配置 =====
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
    min_failed_sources: 3   # 至少3个源失败才推送
    include_errors: true
    max_errors: 8

# ===== GitHub Pages =====
pages:
  enabled: true
  title: 三农新闻日报
  subtitle: 农业农村政策与产业动态简报
  archive_days: 30
```

### 安全配置机制

| 环境 | 配置方式 |
|------|----------|
| config.yaml | 只写 `${ENV_VAR}` 占位符，不写真实值 |
| GitHub Actions | 通过 `secrets.*` 注入环境变量 |
| GitHub Secrets | 仓库 Settings → Secrets → Actions 中添加 |
| 本地开发 | `.env` 文件 + `python-dotenv` 加载（`.env` 加入 `.gitignore`） |

`config.py` 中读取逻辑：
```python
import os
import re
import yaml
from dotenv import load_dotenv

load_dotenv()  # 本地开发加载 .env

def load_config(path="config.yaml"):
    with open(path) as f:
        raw = f.read()
    # 替换 ${VAR_NAME} 为环境变量值
    resolved = re.sub(r'\$\{(\w+)\}', lambda m: os.getenv(m.group(1), ''), raw)
    return yaml.safe_load(resolved)
```

---

## 三、数据存储设计

### 目录结构

```
data/
└── 2026-05-29/
    ├── raw/                    # 按来源拆分
    │   ├── people_daily.json
    │   ├── xinhua.json
    │   └── ...
    ├── filtered.json           # AI 相关性过滤
    ├── classified.json         # AI 分类 + 摘要
    ├── daily_brief.md          # 最终日报
    ├── errors.json             # 抓取失败记录
    └── metadata.json           # 任务统计
```

### `raw/<source>.json`

```json
{
  "source": "人民日报",
  "fetched_at": "2026-05-29T08:05:32",
  "total": 12,
  "articles": [
    {
      "id": "a1b2c3d4",
      "title": "全国夏粮收购进度快于去年同期",
      "url": "https://...",
      "publish_time": "2026-05-29 07:45",
      "raw_text": "正文内容（已清洗）...",
      "fetch_status": "success"
    }
  ]
}
```

### `filtered.json`

```json
{
  "date": "2026-05-29",
  "filtered_at": "2026-05-29T08:10:15",
  "total_raw": 87,
  "total_filtered": 42,
  "articles": [
    {
      "id": "a1b2c3d4",
      "source": "人民日报",
      "title": "...",
      "url": "...",
      "relevance_score": 8.7,
      "importance_score": 5,
      "category": "粮食安全",
      "summary": "...",
      "keywords": ["夏粮", "收购"]
    }
  ]
}
```

### `classified.json`

```json
{
  "date": "2026-05-29",
  "analyzed_at": "2026-05-29T08:15:20",
  "total_filtered": 42,
  "category_counts": {
    "粮食安全": 15,
    "产业发展": 12,
    "乡村振兴": 8,
    "政策法规": 5,
    "科技兴农": 2,
    "生态环保": 0,
    "农产品市场": 0
  },
  "articles": [ "... 同上，按 importance_score 降序排列" ]
}
```

### `archive.db` 去重表

```sql
CREATE TABLE IF NOT EXISTS crawled_urls (
    url_hash        TEXT PRIMARY KEY,
    url             TEXT NOT NULL,
    source          TEXT NOT NULL,
    title           TEXT,
    first_seen      TEXT NOT NULL,
    last_crawled    TEXT NOT NULL,
    crawl_count     INTEGER DEFAULT 1,
    status          TEXT DEFAULT 'success',
    last_error      TEXT
);

CREATE INDEX idx_source ON crawled_urls(source);
CREATE INDEX idx_first_seen ON crawled_urls(first_seen);
CREATE INDEX idx_last_crawled ON crawled_urls(last_crawled);
```

### `metadata.json`

```json
{
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
```

---

## 四、AI 分析流程设计

### 第 1 层：分类 + 过滤（批量模式）

- 输入：`raw/<source>.json` 中所有文章
- 调用方式：每批 10 条送入 DeepSeek
- 输出：`filtered.json`

**Prompt：**

```
你是一名专业的三农新闻资深编辑。

请对以下多条新闻进行批量分析，每条新闻输出一个 JSON 对象。

要求：
1. relevance_score：0-10 分（必须与农业农村农民直接相关才给高分）
2. category：只能从以下类别中选择一个：
   ["政策法规","粮食安全","产业发展","乡村振兴","科技兴农","生态环保","农产品市场","其他"]
3. importance_score：1-5 分（5 分为极重要）
4. summary：一句话摘要（≤100 字）
5. keywords：提取 3-5 个核心关键词（数组）

请严格按照以下 JSON 数组格式输出，不要添加任何解释文字：

[
  {
    "id": "xxx",
    "title": "...",
    "relevance_score": 9,
    "category": "粮食安全",
    "importance_score": 5,
    "summary": "一句话摘要...",
    "keywords": ["夏粮", "收购", "国家政策"]
  }
]
```

**过滤逻辑**：
- `relevance_score < 6` → 丢弃（与三农无关）
- `importance_score < 3` → 丢弃（低价值）
- 最终保留约 30-50 条高质量新闻

### 第 2 层：日报综述

- 输入：`filtered.json` 中全部文章（已分类、已评分）
- 调用方式：单次调用
- 输出：日报综述文本 → 由 storage.py 写入 `daily_brief.md`

**Prompt：**

```
你是中国农业农村日报的主编。

请基于以下已分类的高质量三农新闻，撰写一篇今日农业农村日报综述。

要求：
- 总字数控制在 800-1300 字
- 结构严格如下：
  1. 【标题】（吸引人且准确，包含日期）
  2. 【今日要点】（3-5 条，最重要新闻，编号列出）
  3. 【分类详述】（按重要性排序，每个类别 2-4 段）
  4. 【明日关注】（2-3 条建议）
- 语言风格：客观、专业、平实，适合政务人员和农业系统干部阅读
- 避免空洞口号，多用事实和数据

新闻内容如下：
[filtered.json 中按 category 分组、按 importance_score 降序排列的文章数据]
```

### 可选：深度分析

- 触发方式：手动传入 `--deep "话题"` 参数
- 输入：从 `archive.db` 检索历史相关文章
- 输出：专题深度报告 Markdown

### Token 消耗预估

| 层 | 单次用量 | 日用量（按 40 条） | 日费用 |
|----|---------|-------------------|--------|
| 第 1 层 | ~400 token/批(10条) | ~1,600 token | ¥0.002 |
| 第 2 层 | ~3,000 token/次 | ~3,000 token | ¥0.003 |
| **合计** | | **~4,600 token** | **¥0.005** |

> 基于 DeepSeek 定价：输入 ¥1/百万 token，输出 ¥2/百万 token。日均不足 1 分钱。

---

## 五、通知与推送设计

### 通知体系

```
任务开始   → (无通知)
任务成功   → 微信推送日报摘要（今日要点 + 分类统计 + 完整版链接）
任务失败   → 微信推送告警（失败源 + 错误类型，≥3 个源失败才推送）
手动深度   → 生成专题报告 + 推送
```

### 微信推送示例

```
📰 三农日报 | 2026-05-29
━━━━━━━━━━━━━━━━━━
【今日要点】
① 全国夏粮收购进度快于去年同期，主产区累计收购量同比增 3%
② 农业农村部部署新一轮高标准农田建设任务
③ 浙江发布乡村振兴十大典型案例

【分类统计】
粮食安全 15 | 产业发展 12 | 乡村振兴 8 | 政策法规 5

📎 完整日报：https://xxx.github.io/agri-news
━━━━━━━━━━━━━━━━━━
共抓取 87 条，筛选 42 条 | 耗时 18 分钟
```

### 推送服务

| 服务 | 获取方式 | 免费额度 |
|------|---------|----------|
| PushPlus | pushplus.plus 关注公众号获取 token | 200 条/天 |
| Server酱 | sct.ftqq.com 扫码绑定 | 5 条/天 |

默认使用 PushPlus，个人微信号即可接收，无需企业微信。

### `notifier.py` 接口

```python
class Notifier:
    def __init__(self):
        self.token = os.getenv("PUSHPLUS_TOKEN")
        if not self.token:
            print("警告：未找到 PUSHPLUS_TOKEN，推送已禁用")

    def send_daily_brief(self, date, classified, brief_text, pages_url) -> bool: ...
    def send_failure_alert(self, date, metadata, errors) -> bool: ...
```

---

## 六、GitHub Actions 调度设计

### `.github/workflows/daily.yml`

```yaml
name: 三农新闻日报

on:
  schedule:
    - cron: '0 0 * * *'          # UTC 0:00 = 北京时间 8:00
  workflow_dispatch:              # 手动触发
    inputs:
      deep_analysis_topic:
        description: '深度分析话题（可选）'
        required: false

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
```

### GitHub Secrets 配置

仓库 Settings → Secrets and variables → Actions → New repository secret：

| Name | Value |
|------|-------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 |
| `PUSHPLUS_TOKEN` | PushPlus 个人 token |

### 本地开发

在项目根目录创建 `.env` 文件（已在 `.gitignore` 中排除）：

```env
DEEPSEEK_API_KEY=sk-xxx
PUSHPLUS_TOKEN=xxx
```

---

## 七、双模式部署 + 多实例可复制性

### CLI 入口设计 (`main.py`)

```
用法示例：

# 本地开发测试
python src/main.py --dry-run                      # 只爬取，不调 AI
python src/main.py --date 2026-05-28              # 补抓指定日期
python src/main.py --source 人民日报               # 只爬单个源
python src/main.py --no-push                      # 跳过微信推送

# 生产运行（GitHub Actions 或本地定时）
python src/main.py                                # 完整流程

# 深度分析
python src/main.py --deep "高标准农田建设"          # 专题深度分析

# 多实例：用不同配置文件
python src/main.py --config configs/tech_news.yaml  # 科技新闻实例
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--date YYYY-MM-DD` | 指定抓取日期 | 今天 |
| `--dry-run` | 只爬取+存储，跳过 AI 分析 | false |
| `--source NAME` | 只抓取指定源 | 全部 |
| `--deep TOPIC` | 触发深度分析模式 | 无 |
| `--config PATH` | 指定配置文件 | config.yaml |
| `--output-dir PATH` | 指定输出目录 | data/ |
| `--no-push` | 跳过微信推送 | false |

### 双模式运行机制

```
main.py 启动
    │
    ├── env_detector.py 检测运行环境
    │
    ├── os.getenv("GITHUB_ACTIONS") == "true"
    │   → GitHub Actions 模式
    │   → 使用 secrets 环境变量
    │   → 自动 git commit & push 到 GitHub Pages
    │
    └── 本地模式
        → 使用 .env 文件加载环境变量
        → 跳过 git commit & push
        → 支持 --dry-run / --source 参数
        → 结果仅保存在本地 data/ 目录
```

### 多实例可复制性

配置文件驱动一切。创建新领域日报只需：

```bash
cp config.yaml configs/tech_news.yaml   # 复制配置
# 修改 configs/tech_news.yaml 中的：sources / categories / prompts.domain
python src/main.py --config configs/tech_news.yaml
```

**切换领域需要改的配置项**：

| 配置路径 | 三农实例 | 科技实例（例） |
|---------|---------|---------------|
| `sources` | 15 家农业农村相关源 | 科技日报、36氪、虎嗅等 |
| `analyzer.categories` | 粮食安全/乡村振兴/... | 人工智能/半导体/新能源/... |
| `analyzer.prompts.domain` | 三农 | 科技 |
| `sources[].filter_keywords` | 农业/农村/农民/粮食 | AI/芯片/新能源/SaaS |
| `pages.title` | 三农新闻日报 | 科技新闻日报 |
| `pages.subtitle` | 农业农村政策与产业动态简报 | 科技产业动态与创新简报 |

### `.gitignore` 关键项

```
.env                          # 本地 Token，不提交
.env.local                    # 本地覆盖配置

# 本地测试数据（GitHub Actions 中通过 workflow 提交生产数据）
data/
archive.db

# Python
__pycache__/
*.pyc
.venv/
```

---

## 八、模块依赖关系

```
config.py          ← pyyaml, python-dotenv, os.getenv
exceptions.py      ← 无依赖
env_detector.py    ← os.getenv

http_client.py     ← config
anti_detect.py     ← config
parser_helper.py   ← 无依赖

base.py            ← exceptions, parser_helper
handlers/*         ← base, http_client, parser_helper
manager.py         ← handlers/*, sources, http_client, anti_detect

storage.py         ← 无依赖 (JSON 文件 I/O)
dedup.py           ← 无依赖 (SQLite)
analyzer.py        ← config, storage
reporter.py        ← storage
notifier.py        ← os.getenv (安全读取 token)

main.py            ← manager, dedup, storage, analyzer, reporter, notifier, config, env_detector
```

---

## 九、依赖清单

### `requirements.txt`（生产环境）

```
httpx>=0.27.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
openai>=1.30.0          # DeepSeek 兼容 OpenAI SDK
pyyaml>=6.0
python-dotenv>=1.0.0
```

### `requirements-dev.txt`（本地开发额外依赖）

```
pytest>=8.0
pytest-mock>=3.12
black>=24.0
ruff>=0.3.0
```

---

## 十、关键设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 爬虫方式 | httpx + BeautifulSoup | 15 家媒体均为服务端渲染，无需无头浏览器 |
| 调度 | GitHub Actions | 零成本，公开仓库无限免费额度 |
| 爬虫模式 | 串行 + 随机延时 | 友好爬取，降低被封风险 |
| AI 分析 | DeepSeek | 中文能力强，价格最低（约 0.005 元/天） |
| AI 分层 | 两层（分类→综述） | 先过滤低质新闻再写综述，节省 token |
| 存储 | JSON + SQLite | 零外部依赖，GitHub 直接追踪 |
| 推送 | PushPlus | 个人微信即收，无需企业微信 |
| 安全 | 环境变量 + Secrets | Token 不写入仓库，`${VAR}` 占位 |
