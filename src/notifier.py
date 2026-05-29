import os
import httpx


class Notifier:
    def __init__(self, config):
        notify_cfg = config.get("notify", {})
        self.enabled = notify_cfg.get("enabled", True)
        self.token = os.getenv("PUSHPLUS_TOKEN")
        if not self.token:
            self.token = notify_cfg.get("pushplus_token", "")
            if not self.token or self.token.startswith("${"):
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
            with httpx.Client() as client:
                resp = client.post(
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
        content = f"# {self.title} | {date_str}\n\n{summary}\n\n[完整日报]({pages_url})"
        content = content[:self.success_cfg.get("brief_max_chars", 600)]
        return self._push(f"{self.title} | {date_str}", content)

    def send_failure_alert(self, date_str, errors, metadata):
        if not self.failure_cfg.get("enabled", True):
            return "disabled"
        min_failed = self.failure_cfg.get("min_failed_sources", 3)
        if len(errors) < min_failed:
            return "skipped"
        error_lines = [
            f"- {e['source']}: {e['error']}"
            for e in errors[:self.failure_cfg.get("max_errors", 8)]
        ]
        content = (
            f"# 抓取异常 | {date_str}\n\n"
            f"失败 {len(errors)} 个源：\n\n"
            + "\n".join(error_lines)
        )
        return self._push(f"抓取异常 | {date_str}", content)
