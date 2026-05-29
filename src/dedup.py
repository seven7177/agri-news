import hashlib
import sqlite3
from datetime import datetime


class Dedup:
    def __init__(self, db_path="archive.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS crawled_urls (
                url_hash    TEXT PRIMARY KEY,
                url         TEXT NOT NULL,
                source      TEXT NOT NULL,
                title       TEXT,
                first_seen  TEXT NOT NULL,
                last_crawled TEXT NOT NULL,
                crawl_count INTEGER DEFAULT 1,
                status      TEXT DEFAULT 'success',
                last_error  TEXT
            )
        """)
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_source ON crawled_urls(source)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_last_crawled ON crawled_urls(last_crawled)")
        self.conn.commit()

    def _hash_url(self, url):
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    def is_duplicate(self, url, source):
        url_hash = self._hash_url(url)
        cursor = self.conn.execute(
            "SELECT url_hash FROM crawled_urls WHERE url_hash = ?",
            (url_hash,)
        )
        row = cursor.fetchone()
        if row:
            return True
        # Auto-mark new URLs on first check
        now = datetime.utcnow().isoformat() + "Z"
        self.conn.execute(
            """INSERT INTO crawled_urls
               (url_hash, url, source, title, first_seen, last_crawled, status, last_error)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (url_hash, url, source, "", now, now, "success", None)
        )
        self.conn.commit()
        return False

    def mark_crawled(self, url, source, title, status="success", error=None):
        url_hash = self._hash_url(url)
        now = datetime.utcnow().isoformat() + "Z"
        existing = self.conn.execute(
            "SELECT crawl_count FROM crawled_urls WHERE url_hash = ?",
            (url_hash,)
        ).fetchone()

        if existing:
            self.conn.execute(
                """UPDATE crawled_urls
                   SET last_crawled = ?, crawl_count = crawl_count + 1,
                       status = ?, last_error = ?, title = ?
                   WHERE url_hash = ?""",
                (now, status, error, title, url_hash)
            )
        else:
            self.conn.execute(
                """INSERT INTO crawled_urls
                   (url_hash, url, source, title, first_seen, last_crawled, status, last_error)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (url_hash, url, source, title, now, now, status, error)
            )
        self.conn.commit()

    def filter_new(self, articles):
        new_articles = []
        for article in articles:
            if not self.is_duplicate(article["url"], article.get("source", "")):
                new_articles.append(article)
        return new_articles

    def get_stats(self):
        cursor = self.conn.execute("SELECT COUNT(*) FROM crawled_urls")
        total = cursor.fetchone()[0]
        return {"total_urls": total}

    def close(self):
        self.conn.close()
