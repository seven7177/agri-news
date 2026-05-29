import importlib
from datetime import datetime
from .utils.parser_helper import matches_keywords


class ScraperManager:
    def __init__(self, sources, http_client, config=None):
        self.sources = [s for s in sources if s.get("enabled", True)]
        self.http_client = http_client
        self.config = config or {}
        self.max_articles = self.config.get("scraper", {}).get("max_articles_per_source", 30)
        self.handler_registry = {}  # 用于测试注入

    def _load_handler(self, handler_name):
        if handler_name in self.handler_registry:
            return self.handler_registry[handler_name]
        module = importlib.import_module(f"src.scrapers.handlers.{handler_name}")
        class_name = ''.join(part.capitalize() for part in handler_name.split('_')) + "Scraper"
        return getattr(module, class_name)

    def _scrape_source(self, source):
        handler_name = source["handler"]
        keywords = source.get("keywords", [])
        HandlerClass = self._load_handler(handler_name)
        scraper = HandlerClass(self.http_client, self.config)
        scraper.source_name = source["name"]

        urls = scraper.fetch_urls()
        articles = []
        for url in urls[:self.max_articles]:
            try:
                article = scraper.parse_article(url)
                article["source"] = source["name"]
                if matches_keywords(article.get("title", ""), keywords) or not keywords:
                    articles.append(article)
            except Exception:
                continue

        return source["name"], handler_name, articles

    def run_all(self):
        all_articles = []
        errors = []

        for source in self.sources:
            try:
                name, handler_name, articles = self._scrape_source(source)
                all_articles.append({
                    "source": name,
                    "handler": handler_name,
                    "articles": articles,
                    "count": len(articles),
                })
            except Exception as e:
                errors.append({
                    "source": source["name"],
                    "handler": source.get("handler", ""),
                    "error": str(e),
                    "time": datetime.utcnow().isoformat() + "Z",
                })

            self.http_client.inter_source_delay()

        return all_articles, errors
