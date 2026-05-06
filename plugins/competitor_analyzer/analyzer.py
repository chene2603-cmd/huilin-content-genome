# plugins/competitor_analyzer/analyzer.py
"""竞品分析器 - 第三块竞争力积木"""
from typing import Dict, Any, List
from core.plugin_base import BasePlugin
from core.genome import ContentDNA


class CompetitorAnalyzer(BasePlugin):
    """对比我方DNA与竞品DNA，输出差距分析、优势维度和竞争建议"""
    
    def __init__(self, config_path: str = "plugins/competitor_analyzer/config.json"):
        super().__init__(config_path)
        self.weights = self.config.get("weights", {})
        self.thresholds = self.config.get("alert_thresholds", {})
        self.dimensions = self.config.get("dimensions", ["style", "topic", "format", "emotion"])
    
    async def analyze(self, dna: ContentDNA, **kwargs) -> Dict[str, Any]:
        """
        核心分析方法
        输入：dna = 我方DNA
             kwargs["competitors"] = List[(name, ContentDNA)] 竞品列表
        """
        competitors: List[tuple] = kwargs.get("competitors", [])
        if not competitors:
            return {"error": "未提供竞品数据"}
        if not self.validate_dna(dna):
            return {"error": "我方DNA样本不足"}
        
        results = []
        for comp_name, comp_dna in competitors:
            # 1. 整体相似度
            similarity = dna.similarity_to(comp_dna)
            
            # 2. 各维度基因强度对比
            dimension_gaps = {}
            for dim in self.dimensions:
                my_genes = getattr(dna, f"{dim}_genes", [])
                comp_genes = getattr(comp_dna, f"{dim}_genes", [])
                
                my_strength = sum(g.weight * g.confidence for g in my_genes) / max(len(my_genes), 1) * 100
                comp_strength = sum(g.weight * g.confidence for g in comp_genes) / max(len(comp_genes), 1) * 100
                
                dimension_gaps[dim] = {
                    "my_score": round(my_strength, 1),
                    "competitor_score": round(comp_strength, 1),
                    "gap": round(my_strength - comp_strength, 1),
                    "status": "优势" if my_strength > comp_strength else ("持平" if my_strength == comp_strength else "劣势")
                }
            
            # 3. 表现差距
            my_engagement = dna.performance_traits.get("avg_engagement_rate", 0)
            comp_engagement = comp_dna.performance_traits.get("avg_engagement_rate", 0)
            performance_gap = (my_engagement - comp_engagement) * 10000  # 转换为基点
            
            # 4. 差异化程度
            differentiation = (1 - similarity) * 100
            
            # 5. 综合竞争指数
            competitive_index = round(
                differentiation * self.weights.get("differentiation", 0.25) +
                (50 - abs(performance_gap) / 2) * self.weights.get("performance_gap", 0.35) +
                (1 - similarity) * 100 * self.weights.get("gene_similarity", 0.4),
                1
            )
            
            results.append({
                "competitor_name": comp_name,
                "similarity": round(similarity, 2),
                "differentiation": round(differentiation, 1),
                "performance_gap_bps": round(performance_gap, 1),
                "dimension_gaps": dimension_gaps,
                "competitive_index": competitive_index,
                "alerts": self._generate_alerts(similarity, dimension_gaps, performance_gap)
            })
        
        # 汇总
        summary = self._generate_summary(results)
        
        return {
            "my_account": dna.account_id,
            "competitor_count": len(results),
            "results": results,
            "summary": summary,
            "timestamp": dna.extraction_date.isoformat()
        }
    
    def report(self, result: Dict[str, Any]) -> str:
        if "error" in result:
            return f"❌ 分析失败：{result['error']}"
        
        report = f"""## 🏆 竞品基因分析报告

**我方账号**：{result['my_account']}
**分析竞品数**：{result['competitor_count']}

### 📊 竞品对比总览
"""
        for r in result["results"]:
            report += f"""
**{r['competitor_name']}**
- 基因相似度：{r['similarity']*100:.1f}%
- 差异化程度：{r['differentiation']:.1f}/100
- 表现差距：{r['performance_gap_bds']:.1f}基点
- 综合竞争指数：{r['competitive_index']}/100
"""
            for dim, data in r["dimension_gaps"].items():
                emoji = "🟢" if data["status"] == "优势" else ("🟡" if data["status"] == "持平" else "🔴")
                report += f"  {emoji} {dim}: 我方{data['my_score']} vs 竞品{data['competitor_score']} ({data['status']})\n"
            
            if r["alerts"]:
                report += "\n⚠️ 预警：\n"
                for alert in r["alerts"]:
                    report += f"  - {alert}\n"
        
        report += f"\n### 💡 竞争策略建议\n{result['summary']['recommendation']}\n"
        return report
    
    def _generate_alerts(self, similarity: float, gaps: Dict, perf_gap: float) -> list:
        alerts = []
        if similarity > self.thresholds.get("high_similarity", 0.8):
            alerts.append(f"基因高度相似（{similarity*100:.0f}%），同质化风险高")
        
        for dim, data in gaps.items():
            if data["gap"] < -self.thresholds.get("performance_deficit", 20):
                alerts.append(f"{dim}维度严重落后竞品（差距{data['gap']:.0f}分）")
        
        if perf_gap < -10:
            alerts.append(f"互动率明显低于竞品（{perf_gap:.0f}基点）")
        
        return alerts
    
    def _generate_summary(self, results: list) -> dict:
        if not results:
            return {"avg_competitive_index": 0, "recommendation": "数据不足"}
        
        avg_index = sum(r["competitive_index"] for r in results) / len(results)
        
        tips = []
        for r in results:
            for dim, data in r["dimension_gaps"].items():
                if data["status"] == "劣势":
                    tips.append(f"强化{dim}维度以缩小与{r['competitor_name']}的差距")
        
        if not tips:
            tips.append("当前基因结构具有明显差异化优势，继续保持")
        
        return {
            "avg_competitive_index": round(avg_index, 1),
            "recommendation": "\n".join(f"- {t}" for t in tips[:3])
        }