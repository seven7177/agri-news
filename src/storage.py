import json
from pathlib import Path
from datetime import datetime


class Storage:
    def __init__(self, base_dir="data"):
        self.base_dir = Path(base_dir)

    def _date_dir(self, date_str):
        return self.base_dir / date_str

    def _raw_dir(self, date_str):
        return self._date_dir(date_str) / "raw"

    def save_json(self, date_str, filename, data):
        dir_path = self._date_dir(date_str)
        if filename.startswith("raw/"):
            dir_path = self._raw_dir(date_str)
            filename = filename[4:]
        dir_path.mkdir(parents=True, exist_ok=True)
        filepath = dir_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return str(filepath)

    def load_json(self, date_str, filename):
        filepath = self._date_dir(date_str) / filename
        if not filepath.exists():
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_raw(self, date_str, source_key, source_name, articles):
        data = {
            "source": source_name,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "total": len(articles),
            "articles": articles
        }
        return self.save_json(date_str, f"raw/{source_key}.json", data)

    def save_filtered(self, date_str, total_raw, articles):
        data = {
            "date": date_str,
            "filtered_at": datetime.utcnow().isoformat() + "Z",
            "total_raw": total_raw,
            "total_filtered": len(articles),
            "articles": articles
        }
        return self.save_json(date_str, "filtered.json", data)

    def save_classified(self, date_str, articles, category_counts):
        data = {
            "date": date_str,
            "analyzed_at": datetime.utcnow().isoformat() + "Z",
            "total_filtered": len(articles),
            "category_counts": category_counts,
            "articles": sorted(articles, key=lambda x: x.get("importance_score", 0), reverse=True)
        }
        return self.save_json(date_str, "classified.json", data)

    def save_brief(self, date_str, brief_text):
        dir_path = self._date_dir(date_str)
        dir_path.mkdir(parents=True, exist_ok=True)
        filepath = dir_path / "daily_brief.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(brief_text)
        return str(filepath)

    def save_metadata(self, date_str, metadata):
        return self.save_json(date_str, "metadata.json", metadata)

    def save_errors(self, date_str, errors):
        return self.save_json(date_str, "errors.json", errors)
