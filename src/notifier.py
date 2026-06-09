import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


class Notifier:
    def __init__(self, config):
        notify_cfg = config.get("notify", {})
        self.enabled = notify_cfg.get("enabled", True)
        self.provider = notify_cfg.get("provider", "email")
        self.title = config.get("pages", {}).get("title", "浙江三农新闻")

        # 邮件配置
        email_cfg = notify_cfg.get("email", {})
        self.smtp_server = email_cfg.get("smtp_server", "smtp.qq.com")
        self.smtp_port = email_cfg.get("smtp_port", 465)
        self.use_ssl = email_cfg.get("use_ssl", True)
        self.email_user = os.getenv("EMAIL_USERNAME") or email_cfg.get("username", "")
        self.email_pass = os.getenv("EMAIL_PASSWORD") or email_cfg.get("password", "")
        raw_to = os.getenv("EMAIL_TO") or email_cfg.get("to", "")
        self.email_to = [t.strip() for t in raw_to.split(",") if t.strip()]
        self.subject_tpl = email_cfg.get("subject_template", "浙江三农新闻 {date}")

        # 清理未解析的占位符
        if self.email_user.startswith("${"):
            self.email_user = ""
        if self.email_pass.startswith("${"):
            self.email_pass = ""

        if not self.email_user or not self.email_pass:
            print("警告：邮件配置不完整，发送功能已禁用")

    def _send_email(self, subject, html_body):
        if not self.email_user or not self.email_pass or not self.email_to:
            print("邮件配置不完整，跳过发送")
            return False
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = Header(subject, "utf-8")
            msg["From"] = self.email_user
            msg["To"] = ", ".join(self.email_to)
            msg.attach(MIMEText(html_body, "html", "utf-8"))

            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=15)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=15)
                server.starttls()

            server.login(self.email_user, self.email_pass)
            server.sendmail(self.email_user, self.email_to, msg.as_string())
            server.quit()
            print(f"邮件已发送至 {', '.join(self.email_to)}")
            return True
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False

    def _format_list_as_html(self, markdown_text):
        """将 Markdown 链接列表转为 HTML 邮件格式"""
        lines = markdown_text.strip().split("\n")
        html_lines = ['<html><body style="font-family: sans-serif; max-width: 700px;">']
        in_list = False
        for line in lines:
            if line.startswith("# "):
                html_lines.append(f'<h2 style="color:#2d5016;">{line[2:]}</h2>')
            elif line.startswith("## "):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f'<h3 style="color:#4a7c2e;">{line[3:]}</h3>')
            elif line.startswith("- [") and "](" in line:
                if not in_list:
                    html_lines.append('<ul style="line-height:1.8;">')
                    in_list = True
                import re
                match = re.match(r'- \[(.*?)\]\((.*?)\)(.*)', line)
                if match:
                    title, url, suffix = match.groups()
                    html_lines.append(f'<li><a href="{url}" style="color:#1a73e8;">{title}</a>{suffix}</li>')
            elif line.startswith("---"):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append("<hr>")
            elif line.startswith(">"):
                html_lines.append(f'<p style="color:#888;font-size:14px;">{line[1:].strip()}</p>')
        if in_list:
            html_lines.append("</ul>")
        html_lines.append("</body></html>")
        return "\n".join(html_lines)

    def send_daily_brief(self, date_str, brief_text, pages_url=""):
        subject = self.subject_tpl.format(date=date_str)
        html_body = self._format_list_as_html(brief_text)
        if pages_url:
            html_body = html_body.replace("</body>",
                f'<p style="margin-top:20px;"><a href="{pages_url}" style="color:#1a73e8;">查看完整日报</a></p></body>')
        return self._send_email(subject, html_body)

    def send_failure_alert(self, date_str, errors, metadata):
        if len(errors) == 0:
            return "skipped"
        error_lines = "<br>".join(f"{e['source']}: {e['error']}" for e in errors)
        html = f"""<html><body style="font-family:sans-serif;">
<h3 style="color:red;">抓取异常 | {date_str}</h3>
<p>失败 {len(errors)}/{metadata.get('total_sources','?')} 个源：</p>
<p>{error_lines}</p>
</body></html>"""
        return self._send_email(f"⚠️ 抓取异常 | {date_str}", html)


if __name__ == "__main__":
    import sys
    from src.config import load_config
    config = load_config()
    notifier = Notifier(config)
    if "--failure" in sys.argv:
        notifier._send_email(
            "三农日报任务失败",
            f"<p>时间：{__import__('datetime').datetime.now().isoformat()}</p><p>请检查 GitHub Actions 日志。</p>"
        )
