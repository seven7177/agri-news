# 三农新闻日报系统

每日自动采集、分析并推送三农（农业、农村、农民）相关新闻的日报系统。

## 功能特性

- 多源新闻采集（政府网站、主流媒体等）
- 智能内容分析（基于 DeepSeek API）
- 每日自动推送（通过 PushPlus）
- 可配置的采集策略和推送规则

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API Key：

- `DEEPSEEK_API_KEY`：DeepSeek API 密钥，用于新闻内容分析
- `PUSHPLUS_TOKEN`：PushPlus 推送 Token，用于消息推送

### 3. 试运行

```bash
# 预览模式（仅打印，不推送）
python main.py --dry-run

# 指定配置文件
python main.py --config config.yaml

# 正常执行
python main.py
```

## 项目结构

```
├── src/
│   ├── config/         # 配置模块
│   ├── storage/        # 数据存储
│   ├── scrapers/       # 新闻采集
│   │   ├── handlers/   # 各站点采集器
│   │   └── utils/      # 采集工具函数
│   ├── analyzer/       # 内容分析
│   └── notifier/       # 消息推送
├── tests/              # 测试
├── docs/               # 设计文档
└── requirements.txt    # 依赖清单
```

## 开发

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest

# 代码格式化
black src/ tests/

# 代码检查
ruff check src/ tests/
```

## 许可证

MIT
