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
