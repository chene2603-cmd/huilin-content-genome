# plugins/example_analyzer/analyzer.py
import json
from pathlib import Path
from core.plugin_base import BasePlugin
from core.genome import ContentDNA
from typing import Any, Dict


class ExampleAnalyzer(BasePlugin):
    def __init__(self):
        config_path = Path(__file__).parent / "config.json"
        with open(config_path, "r") as f:
            config = json.load(f)
        super().__init__(config)

    async def analyze(self, dna: ContentDNA) -> Dict[str, Any]:
        # 示例：根据配置阈值判断是否热门
        threshold = self.config.get("threshold", 0.7)
        score = dna.to_vector().mean()
        is_hot = score > threshold
        return {
            "score": float(score),
            "is_hot": is_hot,
            "threshold": threshold
        }

    def report(self, result: Dict[str, Any]) -> str:
        status = "🔥 爆款" if result["is_hot"] else "📉 普通"
        return f"示例分析结果: 得分 {result['score']:.2f} - {status}"