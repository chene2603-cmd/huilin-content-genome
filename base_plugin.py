# core/base_plugin.py
from abc import ABC, abstractmethod
from typing import Dict, Any
import json
import os


class BasePlugin(ABC):
    """所有积木的抽象基类。定义标准接口，不实现任何业务逻辑。"""

    def __init__(self, config_path: str = ""):
        self.config = self._load_config(config_path)

    @abstractmethod
    def analyze(self, dna: "ContentDNA") -> Dict[str, Any]:
        """接收DNA，返回结构化分析结果"""
        ...

    @abstractmethod
    def report(self, result: Dict[str, Any]) -> str:
        """接收分析结果，返回Markdown格式报告"""
        ...

    def _load_config(self, path: str) -> Dict[str, Any]:
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}