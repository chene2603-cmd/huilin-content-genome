"""插件基座 - 所有插件的统一接口"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
import os


class BasePlugin(ABC):
    """所有能力插件的基类"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.name = self.__class__.__name__
        self.version = "1.0"
    
    @abstractmethod
    async def analyze(self, dna: "ContentDNA", **kwargs) -> Dict[str, Any]:
        """核心分析方法"""
        pass
    
    @abstractmethod
    def report(self, result: Dict[str, Any]) -> str:
        """生成可读报告"""
        pass
    
    def validate_dna(self, dna: "ContentDNA") -> bool:
        """验证DNA有效性"""
        return dna.sample_size > 0
    
    def _load_config(self, path: Optional[str]) -> Dict[str, Any]:
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def get_metadata(self) -> Dict[str, Any]:
        """获得插件元数据"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.__doc__ or "",
            "capabilities": list(self.config.get("capabilities", []))
        }