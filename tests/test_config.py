import os
import tempfile
import pytest
from src.config import load_config


def test_load_config_resolves_env_vars():
    yaml_content = """
llm:
  api_key: ${TEST_API_KEY}
scraper:
  delay_min: 2
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        tmp_path = f.name

    os.environ['TEST_API_KEY'] = 'sk-test-123'
    try:
        config = load_config(tmp_path)
        assert config['llm']['api_key'] == 'sk-test-123'
        assert config['scraper']['delay_min'] == 2
    finally:
        os.unlink(tmp_path)
        del os.environ['TEST_API_KEY']


def test_load_config_missing_env_var_defaults_to_empty():
    yaml_content = "llm:\n  api_key: ${MISSING_VAR}"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        tmp_path = f.name

    try:
        config = load_config(tmp_path)
        assert config['llm']['api_key'] == ''
    finally:
        os.unlink(tmp_path)


def test_load_config_no_env_var_placeholders():
    yaml_content = "scraper:\n  delay_min: 2\ntimeout: 15"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        tmp_path = f.name

    try:
        config = load_config(tmp_path)
        assert config['scraper']['delay_min'] == 2
        assert config['timeout'] == 15
    finally:
        os.unlink(tmp_path)
