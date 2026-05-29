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


def matches_keywords(title, keywords):
    if not keywords:
        return True
    title_lower = title.lower()
    return any(kw.lower() in title_lower for kw in keywords)
