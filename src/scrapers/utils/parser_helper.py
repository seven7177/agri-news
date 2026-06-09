import re
from bs4 import BeautifulSoup


def clean_html(html):
    soup = BeautifulSoup(html, 'lxml')
    for tag in soup(['script', 'style', 'nav', 'footer', 'iframe', 'noscript']):
        tag.decompose()
    return soup.get_text(separator='\n', strip=True)


def normalize_date(date_str):
    if not date_str:
        return ""
    date_str = date_str.strip()
    patterns = [
        (r'(\d{4})年(\d{1,2})月(\d{1,2})日\s*(\d{1,2}:\d{2})?',
         lambda m: f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}" +
                   (f" {m.group(4)}" if m.lastindex and m.lastindex >= 4 and m.group(4) else "")),
    ]
    for pattern, replacer in patterns:
        match = re.search(pattern, date_str)
        if match:
            return replacer(match)
    date_str = date_str.replace('/', '-')
    return date_str


def extract_text_from_html(html):
    soup = BeautifulSoup(html, 'lxml')
    article = soup.find('article') or soup.find(class_=re.compile(r'article|content|main'))
    if article:
        return article.get_text(separator='\n', strip=True)
    return soup.body.get_text(separator='\n', strip=True) if soup.body else clean_html(html)


def extract_article_body(html):
    """提取页面全部文本，仅剔除明显的噪声标签和行"""
    soup = BeautifulSoup(html, 'lxml')

    # 剔除噪声标签
    for tag_name in ['script', 'style', 'nav', 'footer', 'iframe', 'noscript']:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # 获取页面全部文本
    raw = soup.get_text(separator='\n', strip=True)

    # 按行过滤噪声
    lines = raw.split('\n')
    clean_lines = []
    for line in lines:
        line = line.strip()
        if not line or len(line) < 4:
            continue
        lower = line.lower()
        if any(w in lower for w in ['copyright', '©', '版权所有', '推荐阅读', '相关文章',
                                       '友情链接', '网站地图', '上一篇', '下一篇', '设为首页']):
            continue
        clean_lines.append(line)

    return '\n'.join(clean_lines)


def matches_keywords(title, keywords):
    if not keywords:
        return True
    title_lower = title.lower()
    return any(kw.lower() in title_lower for kw in keywords)


def matches_keywords_and(title, group_a, group_b):
    """标题必须同时命中 group_a 和 group_b 各至少一个关键词（AND 逻辑）"""
    if not group_a and not group_b:
        return True
    title_lower = title.lower()
    hit_a = not group_a or any(kw.lower() in title_lower for kw in group_a)
    hit_b = not group_b or any(kw.lower() in title_lower for kw in group_b)
    return hit_a and hit_b


# 导航链接黑名单（标题包含以下任一关键词则跳过）
NAV_BLACKLIST = [
    "首页", "导航", "地图", "友情链接", "网站地图", "登录", "注册",
    "返回", "上一页", "下一页", "上一篇", "下一篇", "更多", "全部",
    "设为首页", "加入收藏", "联系我们", "关于我们", "版权声明",
    "报系", "矩阵", "English", "手机版", "客户端", "APP",
]


def is_article_link(a_tag):
    """判断一个 <a> 标签是否为新闻链接（排除导航、菜单、页脚链接）"""
    text = a_tag.get_text(strip=True)
    href = a_tag.get("href", "")

    # 文本太短或太长通常是导航
    if len(text) < 5:
        return False
    if len(text) > 200:
        return False

    # 导航黑名单
    for kw in NAV_BLACKLIST:
        if kw in text:
            return False

    # URL 不能太短（新闻链接通常很长）
    if len(href) < 20:
        return False

    # 排除纯锚点链接
    if href.startswith("#") or href.startswith("javascript:"):
        return False

    # 排除非中文版链接
    href_lower = href.lower()
    non_cn = ["spanish.", "french.", "russian.", "german.", "arabic.", "japanese.", "korean.", "/en/"]
    for nc in non_cn:
        if nc in href_lower:
            return False

    # 排除 index 页面
    if href_lower.endswith("index.html") or href_lower.endswith("index.htm"):
        return False

    # 排除栏目列表页
    list_patterns = ["/list.", "/list_", "list.shtml", "/paperindex", "bkdy/", "paperindex"]
    for lp in list_patterns:
        if lp in href_lower:
            return False

    # 排除纯栏目首页（路径太短，如 /finance/、/society/）
    path = href.split("//")[-1].split("/", 1)[-1] if "//" in href else href
    parts = [p for p in path.split("/") if p]
    if len(parts) <= 2:
        # 没有 .html 结尾且无数字，大概率是栏目首页
        if not any(ext in path for ext in [".html", ".htm"]):
            return False

    return True
