import json
from pathlib import Path
from core.plugin_base import BasePlugin
from core.genome import ContentDNA
from typing import Dict, Any


class ExampleAnalyzer(BasePlugin):
    """示例插件：根据基因平均值判断内容热度"""
    def __init__(self):
        config_path = Path(__file__).parent / "config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        super().__init__(config)

    def validate_config(self) -> None:
        if "threshold" not in self.config:
            raise ValueError("config.json 必须包含 'threshold' 字段")

    async def analyze(self, dna: ContentDNA) -> Dict[str, Any]:
        vector = dna.to_vector()
        if len(vector) == 0:
            return {"score": 0.0, "is_hot": False, "error": "Empty gene vector"}
        
        score = float(vector.mean())
        threshold = self.config["threshold"]
        return {
            "score": score,
            "is_hot": score >= threshold,
            "threshold": threshold,
            "gene_count": len(vector)
        }

    def report(self, result: Dict[str, Any]) -> str:
        status = "🔥 爆款" if result.get("is_hot") else "📉 普通"
        return (
            f"示例分析报告\n"
            f"--------------\n"
            f"综合得分: {result['score']:.2f} (阈值 {result['threshold']})\n"
            f"状态: {status}\n"
            f"参与基因数: {result['gene_count']}"
        )