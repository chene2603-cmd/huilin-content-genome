# core/plugin_base.py
from abc import ABC, abstractmethod
from typing import Any, Dict
from core.genome import ContentDNA


class BasePlugin(ABC):
    """所有插件的抽象基类，禁止修改"""
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.validate_config()

    @abstractmethod
    async def analyze(self, dna: ContentDNA) -> Dict[str, Any]:
        """分析内容DNA，返回结构化结果"""
        ...

    @abstractmethod
    def report(self, analysis_result: Dict[str, Any]) -> str:
        """将分析结果转换为可读报告"""
        ...

    def validate_config(self) -> None:
        """插件自身配置校验，可覆盖"""
        pass