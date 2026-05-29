#!/usr/bin/env python3
"""三农新闻日报 -- 主流程入口"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

# 确保项目根目录在 sys.path 中，支持直接运行 python src/main.py
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.config import load_config
from src.env_detector import get_run_mode
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
    source_count = len(config.get("sources", []))
    print(f"配置已加载: {source_count} 个源")

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

    if not all_raw:
        print("无文章可分析")
        return 0

    classified = analyzer.run_layer1(all_raw)
    filtered = analyzer._filter_articles(classified)
    storage.save_filtered(date_str, len(all_raw), filtered)
    print(f"AI 分类完成: {len(filtered)}/{len(classified)} 条保留")

    # 6. AI 第二层：综述
    if filtered:
        brief_text = analyzer.run_layer2(filtered)
    else:
        brief_text = f"# 三农新闻日报 — {date_str}\n\n今日无符合条件的农业农村相关新闻。"
    storage.save_brief(date_str, brief_text)

    # 7. 汇总分类统计
    category_counts = {}
    for a in filtered:
        cat = a.get("category", "其他")
        category_counts[cat] = category_counts.get(cat, 0) + 1

    storage.save_classified(date_str, filtered, category_counts)

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
