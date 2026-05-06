import json
from pathlib import Path
from core.plugin_base import BasePlugin
from core.genome import ContentDNA
from typing import Dict, Any


class TrendPredictorAnalyzer(BasePlugin):
    """基于基因强度预测趋势得分"""
    def __init__(self):
        config_path = Path(__file__).parent / "config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        super().__init__(config)

    async def analyze(self, dna: ContentDNA) -> Dict[str, Any]:
        vector = dna.to_vector()
        if len(vector) == 0:
            return {"trend_score": 0.0, "warning": False}
        avg_val = vector.mean()
        momentum = 0.0
        # 模拟历史数据：如果metadata有history_values则计算动量
        history = dna.metadata.get("history_values", [])
        if history and len(history) > 1:
            momentum = history[-1] - history[0]
        trend_score = avg_val * 0.6 + momentum * 0.4
        warning = trend_score < self.config.get("warning_threshold", 0.3)
        return {"trend_score": trend_score, "warning": warning}

    def report(self, result: Dict[str, Any]) -> str:
        flag = "⚠️ 下降预警" if result["warning"] else "✅ 趋势正常"
        return f"趋势预测得分: {result['trend_score']:.2f} - {flag}"