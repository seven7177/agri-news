import os
import re

import yaml
from dotenv import load_dotenv


def _resolve_env_vars(value):
    """递归解析值中的 ${VAR_NAME} 占位符"""
    if isinstance(value, str):
        return re.sub(
            r'\$\{(\w+)\}',
            lambda m: os.getenv(m.group(1), ''),
            value
        )
    if isinstance(value, dict):
        return {k: _resolve_env_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_env_vars(item) for item in value]
    return value


def load_config(path="config.yaml"):
    load_dotenv()
    with open(path, 'r', encoding='utf-8') as f:
        raw = yaml.safe_load(f)
    return _resolve_env_vars(raw)
