import yaml
from pathlib import Path


def _load_config(path):
    """加载YAML配置文件"""
    with open(Path(__file__).parent.parent / path, 'r') as f:
        return yaml.safe_load(f)


class ConfigLoader:
    def __init__(self, config_path="config/default.yaml"):
        self.config = _load_config(config_path)

    def get(self, key, default=None):
        return self.config.get(key, default)
