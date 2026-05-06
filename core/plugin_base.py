from abc import ABC, abstractmethod
from typing import Any, Dict
from core.genome import ContentDNA


class BasePlugin(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.validate_config()

    @abstractmethod
    async def analyze(self, dna: ContentDNA) -> Dict[str, Any]:
        ...

    @abstractmethod
    def report(self, analysis_result: Dict[str, Any]) -> str:
        ...

    def validate_config(self) -> None:
        pass