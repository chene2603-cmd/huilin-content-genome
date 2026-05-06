# plugins/four_dimension/analyzer.py
"""四维健康度分析器 - 第一块竞争力积木"""
from typing import Dict, Any
from core.plugin_base import BasePlugin
from core.genome import ContentDNA


class FourDimensionAnalyzer(BasePlugin):
    """将内容DNA映射到四维健康度并进行深度分析"""
    
    def __init__(self, config_path: str = ""):
        super().__init__(config_path)
        # 固定的四维映射关系（核心逻辑不可变）
        self.type_mapping = {
            "style": "个人成长",
            "topic": "商业系统",
            "format": "技术产品",
            "emotion": "社会组织"
        }
    
    async def analyze(self, dna: ContentDNA, **kwargs) -> Dict[str, Any]:
        """
        核心分析方法
        输入：ContentDNA对象
        输出：四维健康度分析结果字典
        """
        if not self.validate_dna(dna):
            return {"error": "DNA样本不足", "health_score": 0}
        
        # 1. 计算四个系统的健康分
        system_scores = {}
        for gene_type, system_name in self.type_mapping.items():
            genes = getattr(dna, gene_type + "_genes", [])
            if not genes:
                system_scores[system_name] = 50.0  # 无基因默认50分
                continue
            
            # 基因强度分
            strength_score = sum(g.weight * g.confidence for g in genes) / len(genes) * 100
            # 基因多样性分
            unique_values = len(set(g.value for g in genes))
            diversity_score = min(unique_values / len(genes) * 100, 100)
            
            system_scores[system_name] = round(strength_score * 0.7 + diversity_score * 0.3, 1)
        
        # 2. 计算综合健康指数
        overall_health = round(sum(system_scores.values()) / len(system_scores), 1)
        
        # 3. 生成洞察
        insights = self._generate_insights(system_scores, dna)
        
        return {
            "system_scores": system_scores,
            "overall_health": overall_health,
            "health_level": self._get_health_level(overall_health),
            "insights": insights,
            "dna_fingerprint": dna.get_fingerprint(),
            "analysis_timestamp": dna.extraction_date.isoformat()
        }
    
    def report(self, result: Dict[str, Any]) -> str:
        """生成Markdown格式健康报告"""
        if "error" in result:
            return f"❌ 分析失败：{result['error']}"
        
        report = f"""## 🧬 内容DNA四维健康报告

**DNA指纹**：{result['dna_fingerprint']}
**综合健康指数**：{result['overall_health']}/100 （{result['health_level']}）

### 📊 四维系统得分
| 系统 | 得分 | 等级 |
|------|------|------|
"""
        for system, score in result['system_scores'].items():
            level = self._get_health_level(score)
            report += f"| {system} | {score}/100 | {level} |\n"
        
        report += "\n### 💡 核心洞察\n"
        for insight in result['insights']:
            report += f"- {insight}\n"
        
        return report
    
    def _get_health_level(self, score: float) -> str:
        if score >= 80: return "优秀"
        elif score >= 60: return "健康"
        elif score >= 40: return "关注"
        else: return "需强化"
    
    def _generate_insights(self, system_scores: Dict, dna: ContentDNA) -> list:
        insights = []
        strongest = max(system_scores, key=system_scores.get)
        weakest = min(system_scores, key=system_scores.get)
        gap = system_scores[strongest] - system_scores[weakest]
        
        insights.append(f"最强系统：{strongest}（{system_scores[strongest]}分）")
        if gap > 30:
            insights.append(f"⚠️ 系统间差距较大（{gap:.0f}分），建议优先强化{weakest}")
        if system_scores[weakest] < 60:
            insights.append(f"🔴 {weakest}系统处于薄弱状态，需要重点关注")
        
        return insights