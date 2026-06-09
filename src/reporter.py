class Reporter:
    @staticmethod
    def generate_list(date_str, source_results, metadata):
        """生成按来源分组的链接+标题列表"""
        lines = [
            f"# 浙江三农新闻 — {date_str}",
            "",
        ]

        total = 0
        for entry in source_results:
            articles = entry.get("articles", [])
            if not articles:
                continue
            total += len(articles)
            lines.append(f"## {entry['source']} ({len(articles)}条)")
            lines.append("")
            for a in articles:
                title = a.get("title", "无标题")
                url = a.get("url", "")
                pub_time = a.get("publish_time", "")
                time_str = f" — {pub_time}" if pub_time else ""
                lines.append(f"- [{title}]({url}){time_str}")
            lines.append("")

        lines.extend([
            "---",
            f"共抓取 {metadata.get('total_sources', 0)} 个源，"
            f"命中 {total} 条",
            f"成功 {metadata.get('successful_sources', 0)}/"
            f"{metadata.get('total_sources', 0)} 个源，"
            f"耗时 {Reporter._format_duration(metadata.get('duration_seconds', 0))}",
        ])
        return "\n".join(lines)

    @staticmethod
    def generate_archive_page(dates):
        links = "\n".join(
            f'<li><a href="archives/{d}.html">{d} 浙江三农新闻</a></li>'
            for d in sorted(dates, reverse=True)
        )
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>浙江三农新闻</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
h1 {{ color: #2d5016; }}
li {{ margin: 8px 0; }}
a {{ color: #1a73e8; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<h1>浙江三农新闻</h1>
<p>浙江农业农村政策与产业动态</p>
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
