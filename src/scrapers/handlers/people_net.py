from bs4 import BeautifulSoup
from ..base import BaseScraper
from ..utils.parser_helper import clean_html, normalize_date
from ..exceptions import ParseError


class PeopleNetScraper(BaseScraper):
    HANDLER_NAME = "people_net"

    def fetch_urls(self):
        from ..sources import get_source_by_handler
        config = get_source_by_handler(self.HANDLER_NAME)
        if not config:
            return []
        base_url = config["url"]
        html = self.http_client.fetch(base_url)
        soup = BeautifulSoup(html, 'lxml')
        urls = []
        for a in soup.select('a[href]'):
            href = a.get('href', '')
            if href and 'people.com.cn' in href:
                full_url = href if href.startswith('http') else f"https://people.com.cn{href}"
                if full_url not in urls:
                    urls.append(full_url)
        # Also fetch category pages if configured
        for cat_url in config.get("category_urls", []):
            try:
                cat_html = self.http_client.fetch(cat_url)
                cat_soup = BeautifulSoup(cat_html, 'lxml')
                for a in cat_soup.select('a[href]'):
                    href = a.get('href', '')
                    if href and 'people.com.cn' in href:
                        full_url = href if href.startswith('http') else f"https://people.com.cn{href}"
                        if full_url not in urls:
                            urls.append(full_url)
            except Exception:
                continue
        return urls[:30]

    def parse_article(self, url):
        html = self.http_client.fetch(url)
        soup = BeautifulSoup(html, 'lxml')
        title_el = soup.select_one('h1')
        if not title_el:
            raise ParseError(f"No title found for {url}")
        title = title_el.get_text(strip=True)
        content_el = soup.select_one('.article-content, article')
        raw_text = clean_html(str(content_el)) if content_el else clean_html(html)
        time_el = soup.select_one('.time, time')
        publish_time = normalize_date(time_el.get_text(strip=True)) if time_el else ""
        return {
            "id": self._generate_id(url),
            "title": title,
            "url": url,
            "publish_time": publish_time,
            "raw_text": raw_text[:3000],
            "fetch_status": "success"
        }
