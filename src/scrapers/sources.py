"""
新闻源配置清单。
每个 handler 的名称与 handlers/ 目录中的文件名对应。
"""

SOURCES = [
    {
        "name": "人民日报",
        "handler": "people_daily",
        "url": "https://www.people.com.cn/",
        "category_urls": ["http://country.people.com.cn/"],
        "keywords": ["农业", "农村", "农民", "粮食", "乡村振兴", "耕地"],
        "priority": 1,
        "enabled": True,
    },
    {
        "name": "新华社",
        "handler": "xinhua",
        "url": "https://www.news.cn/",
        "keywords": ["农业", "农村", "农民", "粮食", "乡村振兴", "三农"],
        "priority": 1,
        "enabled": True,
    },
    {
        "name": "央视新闻",
        "handler": "cctv_news",
        "url": "https://news.cctv.com/",
        "keywords": ["农业", "农村", "乡村", "粮食", "三农"],
        "priority": 1,
        "enabled": True,
    },
    {
        "name": "农民日报",
        "handler": "farmers_daily",
        "url": "https://www.farmer.com.cn/",
        "keywords": [],
        "priority": 1,
        "enabled": True,
    },
    {
        "name": "中新社",
        "handler": "chinanews",
        "url": "https://www.chinanews.com/",
        "keywords": ["农业", "农村", "乡村", "粮食", "三农", "农民"],
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "光明日报",
        "handler": "guangming_daily",
        "url": "https://www.gmw.cn/",
        "keywords": ["农业", "农村", "乡村", "粮食", "三农"],
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "经济日报",
        "handler": "economic_daily",
        "url": "https://www.ce.cn/",
        "keywords": ["农业", "农村", "粮食", "乡村振兴", "三农"],
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "浙江日报",
        "handler": "zhejiang_daily",
        "url": "https://zjnews.zjol.com.cn/",
        "keywords": ["农业", "农村", "乡村", "三农", "乡村振兴"],
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "中国蓝新闻",
        "handler": "cztv",
        "url": "https://www.cztv.com/",
        "keywords": ["农业", "农村", "乡村", "三农"],
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "潮新闻",
        "handler": "tide_news",
        "url": "https://tidenews.com.cn/",
        "keywords": ["农业", "农村", "乡村", "三农"],
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "浙江在线",
        "handler": "zjol",
        "url": "https://www.zjol.com.cn/",
        "keywords": ["农业", "农村", "乡村", "三农"],
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "央视网",
        "handler": "cctv_net",
        "url": "https://www.cctv.com/",
        "keywords": ["农业", "农村", "乡村", "粮食", "三农"],
        "priority": 1,
        "enabled": True,
    },
    {
        "name": "央广网",
        "handler": "cnr_news",
        "url": "https://www.cnr.cn/",
        "keywords": ["农业", "农村", "乡村", "粮食", "三农"],
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "人民网",
        "handler": "people_net",
        "url": "https://www.people.com.cn/",
        "category_urls": ["http://country.people.com.cn/"],
        "keywords": ["农业", "农村", "农民", "粮食", "乡村振兴"],
        "priority": 1,
        "enabled": True,
    },
    {
        "name": "都市快报",
        "handler": "dskb",
        "url": "https://hzdaily.hangzhou.com.cn/dskb/",
        "keywords": ["农业", "农村", "乡村", "乡村振兴"],
        "priority": 3,
        "enabled": True,
    },
]


def get_enabled_sources():
    return sorted(
        [s for s in SOURCES if s.get("enabled", True)],
        key=lambda s: s.get("priority", 2)
    )


def get_source_by_handler(handler_name):
    for s in SOURCES:
        if s["handler"] == handler_name:
            return s
    return None
