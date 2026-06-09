from bs4 import BeautifulSoup
from ..base import BaseScraper
from ..utils.parser_helper import is_article_link, extract_article_body, normalize_date
from ..exceptions import ParseError


class EconomicDailyScraper(BaseScraper):
    HANDLER_NAME = "economic_daily"

    def fetch_urls(self):
        from ..sources import get_source_by_handler
        src_cfg = get_source_by_handler(self.HANDLER_NAME)
        if not src_cfg:
            return []

        urls = []
        all_urls = list(src_cfg.get("topic_urls", []))
        if src_cfg.get("home_url"):
            all_urls.append(src_cfg["home_url"])

        for page_url in all_urls:
            try:
                html = self.http_client.fetch(page_url)
                soup = BeautifulSoup(html, 'lxml')
                for a in soup.select('a[href]'):
                    href = a.get('href', '')
                    if not is_article_link(a):
                        continue
                    title = a.get_text(strip=True)
                    if href and ('ce.cn' in href or href.startswith('/')):
                        full_url = href if href.startswith('http') else ('https:' + href if '.com' in href or '.cn' in href else 'https://ce.cn' + href)
                        if full_url not in [u['url'] for u in urls]:
                            urls.append({'url': full_url, 'title': title})
            except Exception:
                pass

        return urls

    def parse_article(self, url):
        html = self.http_client.fetch(url)
        soup = BeautifulSoup(html, 'lxml')

        title_el = soup.select_one('h1')
        if not title_el:
            title_el = soup.select_one('.title') or soup.select_one('.article-title')
        title = title_el.get_text(strip=True) if title_el else ""

        time_el = soup.select_one('time') or soup.select_one('.time') or soup.select_one('.article-time')
        publish_time = normalize_date(time_el.get_text(strip=True)) if time_el else ""

        body_text = extract_article_body(html)

        return {
            "id": self._generate_id(url),
            "title": title,
            "url": url,
            "publish_time": publish_time,
            "raw_text": body_text[:3000],
            "fetch_status": "success"
        }
