import json
from pathlib import Path
from core.plugin_base import BasePlugin
from core.genome import ContentDNA
from typing import Dict, Any


class ContentExtractorAnalyzer(BasePlugin):
    """基于关键词字典提取内容基因"""
    def __init__(self):
        config_path = Path(__file__).parent / "config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        super().__init__(config)

    async def analyze(self, dna: ContentDNA) -> Dict[str, Any]:
        # 假设 metadata 中有 text 字段供提取
        text = dna.metadata.get("text", "")
        keywords = self.config.get("keywords", {})
        extracted = {}
        for dim, words in keywords.items():
            score = 0.0
            for w in words:
                if w in text:
                    score += 0.2
            extracted[dim] = min(score, 1.0)
        return {"extracted_features": extracted}

    def report(self, result: Dict[str, Any]) -> str:
        feats = result.get("extracted_features", {})
        lines = ["提取的特征："]
        for k, v in feats.items():
            lines.append(f"  {k}: {v:.2f}")
        return "\n".join(lines)