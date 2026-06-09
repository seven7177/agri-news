#!/usr/bin/env python3
"""浙江三农新闻 -- 主流程入口"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

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
from src.reporter import Reporter
from src.notifier import Notifier


def parse_args():
    parser = argparse.ArgumentParser(description="浙江三农新闻系统")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--date", help="指定日期 YYYY-MM-DD（默认今天）")
    parser.add_argument("--source", help="只抓取指定源名称")
    parser.add_argument("--no-push", action="store_true", help="跳过推送")
    parser.add_argument("--output-dir", default="data", help="输出目录")
    return parser.parse_args()


def main():
    args = parse_args()
    date_str = args.date or datetime.now().strftime("%Y-%m-%d")
    mode = get_run_mode()
    print(f"=== 浙江三农新闻 v0.2 | {date_str} | {mode} ===")

    # 1. 加载配置
    config = load_config(args.config)
    region = config.get("filter", {}).get("region_keywords", [])
    print(f"配置已加载: {len(config.get('sources', []))} 个源 | 地区关键词: {', '.join(region[:5])}...")

    # 2. 初始化各模块
    storage = Storage(base_dir=args.output_dir)
    dedup = Dedup()
    http_client = HttpClient(config)
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
        print(f"  {source_name}: {len(new_articles)} 条命中")

    if scrape_errors:
        storage.save_errors(date_str, scrape_errors)
        print(f"  {len(scrape_errors)} 个源失败")

    print(f"抓取完成: {total_fetched} 条命中")

    # 5. 生成列表报告
    duration = int(time.time() - start_time)
    metadata = {
        "date": date_str,
        "start_time": datetime.utcnow().isoformat() + "Z",
        "end_time": datetime.utcnow().isoformat() + "Z",
        "total_sources": len(sources),
        "successful_sources": len(sources) - len(scrape_errors),
        "failed_sources": len(scrape_errors),
        "total_fetched": total_fetched,
        "duration_seconds": duration,
        "status": "completed" if not scrape_errors else "partial",
    }
    storage.save_metadata(date_str, metadata)

    # 生成 Markdown 列表
    list_text = Reporter.generate_list(date_str, raw_results, metadata)
    storage.save_brief(date_str, list_text)
    print(f"\n{list_text}")

    # 6. 推送通知（可选）
    total_hits = sum(r["count"] for r in raw_results)
    if notifier and not args.no_push and total_hits > 0:
        notifier.send_daily_brief(date_str, list_text, config.get("pages", {}).get("url", ""))

    print(f"完成！耗时 {Reporter._format_duration(duration)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
