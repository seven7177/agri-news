"""
新闻源配置清单（仅 URL，关键词全局统一）。
"""
SOURCES = [
    {
        "name": "新华网",
        "handler": "xinhua",
        "topic_urls": ["https://xczx.news.cn/"],
        "home_url": "https://www.news.cn/",
        "priority": 1,
        "enabled": True,
    },
    {
        "name": "人民网",
        "handler": "people_net",
        "topic_urls": [
            "http://country.people.com.cn/",
            "http://zj.people.com.cn/",
        ],
        "home_url": "https://www.people.com.cn/",
        "priority": 1,
        "enabled": True,
    },
    {
        "name": "央视网",
        "handler": "cctv_net",
        "topic_urls": ["https://sannong.cctv.com/"],
        "home_url": "https://www.cctv.com/",
        "priority": 1,
        "enabled": True,
    },
    {
        "name": "农民日报",
        "handler": "farmers_daily",
        "topic_urls": ["https://www.farmer.com.cn/"],
        "home_url": "https://www.farmer.com.cn/",
        "priority": 1,
        "enabled": True,
    },
    {
        "name": "央广网",
        "handler": "cnr_news",
        "topic_urls": ["http://country.cnr.cn/"],
        "home_url": "https://www.cnr.cn/",
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "光明日报",
        "handler": "guangming_daily",
        "topic_urls": ["https://topics.gmw.cn/node_154048.htm"],
        "home_url": "https://www.gmw.cn/",
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "人民日报",
        "handler": "people_daily",
        "topic_urls": ["http://country.people.com.cn/", "http://zj.people.com.cn/"],
        "home_url": "https://www.people.com.cn/",
        "priority": 1,
        "enabled": True,
    },
    {
        "name": "央视新闻",
        "handler": "cctv_news",
        "topic_urls": [],
        "home_url": "https://news.cctv.com/",
        "priority": 1,
        "enabled": True,
    },
    {
        "name": "中新社",
        "handler": "chinanews",
        "topic_urls": [],
        "home_url": "https://www.chinanews.com/",
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "经济日报",
        "handler": "economic_daily",
        "topic_urls": [],
        "home_url": "https://www.ce.cn/",
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "浙江在线",
        "handler": "zjol",
        "topic_urls": ["https://www.zjol.com.cn/"],
        "home_url": "https://www.zjol.com.cn/",
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "浙江日报",
        "handler": "zhejiang_daily",
        "topic_urls": ["https://zjnews.zjol.com.cn/"],
        "home_url": "https://zjnews.zjol.com.cn/",
        "priority": 1,
        "enabled": True,
    },
    {
        "name": "中国蓝新闻",
        "handler": "cztv",
        "topic_urls": ["https://www.cztv.com/"],
        "home_url": "https://www.cztv.com/",
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "潮新闻",
        "handler": "tide_news",
        "topic_urls": ["https://tidenews.com.cn/"],
        "home_url": "https://tidenews.com.cn/",
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "都市快报",
        "handler": "dskb",
        "topic_urls": ["https://hzdaily.hangzhou.com.cn/dskb/"],
        "home_url": "https://hzdaily.hangzhou.com.cn/dskb/",
        "priority": 3,
        "enabled": True,
    },
]


def get_enabled_sources():
    return sorted(
        [s for s in SOURCES if s.get("enabled", True)],
        key=lambda s: s.get("priority", 2),
    )


def get_source_by_handler(handler_name):
    for s in SOURCES:
        if s["handler"] == handler_name:
            return s
    return None
