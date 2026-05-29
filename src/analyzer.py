import json
import re
from openai import OpenAI


class Analyzer:
    def __init__(self, config):
        llm_cfg = config.get("llm", {})
        analyzer_cfg = config.get("analyzer", {})
        prompts_cfg = analyzer_cfg.get("prompts", {})

        self.client = OpenAI(
            api_key=llm_cfg.get("api_key", ""),
            base_url=llm_cfg.get("base_url", "https://api.deepseek.com/v1"),
        )
        self.model = llm_cfg.get("model", "deepseek-chat")
        self.max_tokens = llm_cfg.get("max_tokens", 4096)
        self.temperature = llm_cfg.get("temperature", 0.7)
        self.batch_size = analyzer_cfg.get("batch_size", 10)
        self.min_relevance = analyzer_cfg.get("min_relevance_score", 6)
        self.min_importance = analyzer_cfg.get("min_importance_score", 3)
        self.categories = analyzer_cfg.get("categories", [])

        domain = prompts_cfg.get("domain", "三农")
        self.layer1_system = prompts_cfg.get("layer1_system", "你是{domain}新闻资深编辑。").format(domain=domain)
        self.layer2_system = prompts_cfg.get("layer2_system", "你是中国{domain}日报主编。").format(domain=domain)

    def _build_layer1_prompt(self, articles):
        cat_list = "、".join(self.categories)
        articles_text = "\n---\n".join(
            f"id: {a['id']}\ntitle: {a['title']}\ntext: {a.get('raw_text', a.get('summary', ''))[:500]}"
            for a in articles
        )
        return f"""请对以下多条新闻进行批量分析，每条新闻输出一个JSON对象。

要求：
1. relevance_score：0-10分（必须与农业农村农民直接相关才给高分）
2. category：只能从以下类别中选择一个：[{cat_list}]
3. importance_score：1-5分（5分为极重要）
4. summary：一句话摘要（≤100字）
5. keywords：提取3-5个核心关键词（数组）

请严格按照以下JSON数组格式输出，不要添加任何解释文字：
[
  {{"id": "xxx", "title": "...", "relevance_score": 9, "category": "粮食安全", "importance_score": 5, "summary": "一句话摘要...", "keywords": ["关键词1", "关键词2"]}}
]

新闻内容：
{articles_text}"""

    def _parse_layer1_response(self, response_text):
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if match:
                return json.loads(match.group())
            return []

    def _filter_articles(self, articles):
        return [
            a for a in articles
            if a.get("relevance_score", 0) >= self.min_relevance
            and a.get("importance_score", 0) >= self.min_importance
        ]

    def _build_layer2_prompt(self, articles):
        by_category = {}
        for a in articles:
            cat = a.get("category", "其他")
            by_category.setdefault(cat, []).append(a)

        sections = []
        for cat, items in sorted(by_category.items(), key=lambda x: -len(x[1])):
            section = f"【{cat}】({len(items)}条)\n"
            for item in sorted(items, key=lambda x: -x.get("importance_score", 0)):
                section += f"- [{item.get('importance_score', 0)}分] {item['title']}: {item.get('summary', '')}\n"
            sections.append(section)

        context = "\n".join(sections)

        return f"""请基于以下已分类的高质量三农新闻，撰写一篇今日农业农村日报综述。

要求：
- 总字数控制在800-1300字
- 结构严格如下：
  1. 【标题】（吸引人且准确，包含日期）
  2. 【今日要点】（3-5条，最重要新闻，编号列出）
  3. 【分类详述】（按重要性排序，每个类别2-4段）
  4. 【明日关注】（2-3条建议）
- 语言风格：客观、专业、平实，适合政务人员和农业系统干部阅读
- 避免空洞口号，多用事实和数据

新闻内容如下：
{context}"""

    def _call_llm(self, system_prompt, user_prompt):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return response.choices[0].message.content

    def run_layer1(self, articles):
        all_results = []
        for i in range(0, len(articles), self.batch_size):
            batch = articles[i:i + self.batch_size]
            prompt = self._build_layer1_prompt(batch)
            response = self._call_llm(self.layer1_system, prompt)
            results = self._parse_layer1_response(response)
            for r in results:
                # 从批量原文中补充 source 和 url
                for a in batch:
                    if a['id'] == r.get('id'):
                        r["source"] = a.get("source", "")
                        r["url"] = a.get("url", "")
                        break
            all_results.extend(results)
        return all_results

    def run_layer2(self, articles):
        prompt = self._build_layer2_prompt(articles)
        response = self._call_llm(self.layer2_system, prompt)
        return response

    def run_deep_analysis(self, topic, historical_articles):
        prompt = f"""你是三农领域的资深分析师。请围绕话题"{topic}"撰写一份深度分析报告。

基于以下历史新闻数据（共{len(historical_articles)}条），请分析：
1. 该话题的政策背景和发展脉络
2. 关键事件和重要节点
3. 当前态势和主要观点
4. 趋势预判和建议

历史新闻：
{json.dumps([{'title': a.get('title'), 'summary': a.get('summary', ''), 'date': a.get('date', '')} for a in historical_articles[:50]], ensure_ascii=False, indent=2)}"""
        return self._call_llm(self.layer2_system, prompt)
