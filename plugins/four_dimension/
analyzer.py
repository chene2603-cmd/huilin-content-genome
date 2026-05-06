import json
from pathlib import Path
from core.plugin_base import BasePlugin
from core.genome import ContentDNA
from typing import Dict, Any, List


class FourDimensionAnalyzer(BasePlugin):
    """四维健康度分析：商业/技术/用户/内容"""
    def __init__(self):
        config_path = Path(__file__).parent / "config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        super().__init__(config)

    async def analyze(self, dna: ContentDNA) -> Dict[str, Any]:
        dims = self.config.get("dimensions", {})
        scores = {}
        for dim, gene_list in dims.items():
            vals = []
            for gname in gene_list:
                gene = dna.get_gene(gname)
                if gene:
                    vals.append(gene.value)
            scores[dim] = sum(vals) / len(vals) if vals else 0.0
        overall = sum(scores.values()) / len(scores) if scores else 0.0
        return {"dimension_scores": scores, "overall_health": overall}

    def report(self, result: Dict[str, Any]) -> str:
        lines = ["四维健康度报告："]
        for k, v in result["dimension_scores"].items():
            lines.append(f"  {k}: {v:.2f}")
        lines.append(f"综合健康度: {result['overall_health']:.2f}")
        return "\n".join(lines)