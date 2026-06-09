import datetime
import importlib


class ScraperManager:
    def __init__(self, sources, http_client, config=None):
        self.sources = [s for s in sources if s.get("enabled", True)]
        self.http_client = http_client
        self.config = config or {}
        self.handler_registry = {}

        # 从 config 读取全局关键词
        self.agri_keywords = self._parse_keywords(self.config.get("agri_keywords", []))
        self.region_keywords = self._parse_keywords(self.config.get("region_keywords", []))

    def _parse_keywords(self, kw_list):
        """解析关键词列表，支持分段格式如 '农业 农村 农民'"""
        result = []
        for item in kw_list:
            if isinstance(item, str):
                for w in item.split():
                    w = w.strip()
                    if len(w) >= 2:  # 过滤单字符（如分隔符）
                        result.append(w)
            else:
                w = str(item).strip()
                if len(w) >= 2:
                    result.append(w)
        return result

    # 地名后缀：匹配到短地名时，附近需出现这些词才确认为地名
    LOCATION_SUFFIX = ['市', '县', '区', '省', '镇', '乡', '村', '街道', '社区']

    def _matches_place(self, text, keyword):
        """判断关键词是否作为地名出现在文本中"""
        text_lower = text.lower()
        kw_lower = keyword.lower()
        idx = text_lower.find(kw_lower)
        if idx < 0:
            return False

        # 3字及以上 → 默认真地名（够具体）
        if len(keyword) >= 3:
            return True

        # 2字 → 需要上下文验证
        # 检查关键词前后20字内是否有地名后缀
        ctx_start = max(0, idx - 5)
        ctx_end = min(len(text), idx + len(keyword) + 20)
        ctx = text[ctx_start:ctx_end]
        for suffix in self.LOCATION_SUFFIX:
            if suffix in ctx:
                return True
        # 也接受 "浙江XX" 这种省级+地名的组合
        if '浙江' in text[max(0,idx-10):idx+len(keyword)+10]:
            return True
        return False

    def _is_this_year(self, publish_time):
        """检查发布日期是否为今年"""
        if not publish_time:
            return True
        this_year = str(datetime.datetime.now().year)
        return this_year in publish_time

    def _matches_any(self, text, keywords):
        """文本是否匹配任一关键词（无上下文验证）"""
        if not keywords:
            return True
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in keywords)

    def _matches_any_place(self, text, keywords):
        """文本是否匹配任一地名关键词（带上下文验证）"""
        if not keywords:
            return False
        return any(self._matches_place(text, kw) for kw in keywords)

    def _load_handler(self, handler_name):
        if handler_name in self.handler_registry:
            return self.handler_registry[handler_name]
        module = importlib.import_module(f"src.scrapers.handlers.{handler_name}")
        class_name = ''.join(part.capitalize() for part in handler_name.split('_')) + "Scraper"
        return getattr(module, class_name)

    def _scrape_source(self, source):
        handler_name = source["handler"]
        HandlerClass = self._load_handler(handler_name)
        scraper = HandlerClass(self.http_client, self.config)
        scraper.source_name = source["name"]

        items = scraper.fetch_urls()  # [{url, title}, ...]
        articles = []
        body_checked = 0

        for item in items:
            title = item.get("title", "")
            url = item.get("url", "")

            # 第1关：标题必须含农业关键词
            if not self._matches_any(title, self.agri_keywords):
                continue

            # 第2关：标题含地域关键词（上下文验证）→ 直接存入
            if self._matches_any_place(title, self.region_keywords):
                pub_time = item.get("publish_time", "")
                if self._is_this_year(pub_time):
                    articles.append({
                        "id": scraper._generate_id(url),
                        "title": title,
                        "url": url,
                        "publish_time": pub_time,
                        "source": source["name"],
                        "match_type": "title",
                        "fetch_status": "success",
                    })
                continue

            # 第3关：标题无地域 → 进详情页查正文
            try:
                detail = scraper.parse_article(url)
                body_checked += 1
                body_text = detail.get("raw_text", "")
                body_title = detail.get("title", "") or title
                publish_time = detail.get("publish_time", "") or item.get("publish_time", "")

                if self._matches_any_place(body_text, self.region_keywords) or self._matches_any_place(body_title, self.region_keywords):
                    if self._is_this_year(publish_time):
                        articles.append({
                            "id": scraper._generate_id(url),
                            "title": body_title,
                            "url": url,
                            "publish_time": publish_time,
                            "source": source["name"],
                            "match_type": "body",
                            "fetch_status": "success",
                        })
            except Exception:
                pass

        print(f"  {source['name']}: {len(items)} links, {len(articles)} hits (body-checked: {body_checked})")
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
                    "time": datetime.datetime.utcnow().isoformat() + "Z",
                })

            self.http_client.inter_source_delay()

        return all_articles, errors
