# plugins/viral_predictor/predictor.py
"""爆款预测器 - 第二块竞争力积木"""
from typing import Dict, Any
from core.plugin_base import BasePlugin
from core.genome import ContentDNA


class ViralPredictor(BasePlugin):
    """基于DNA基因权重、情感唤起、形式匹配和趋势动量预测内容爆款潜力"""
    
    def __init__(self, config_path: str = "plugins/viral_predictor/config.json"):
        super().__init__(config_path)
        self.weights = self.config.get("weights", {})
        self.thresholds = self.config.get("thresholds", {})
    
    async def analyze(self, dna: ContentDNA, **kwargs) -> Dict[str, Any]:
        if not self.validate_dna(dna):
            return {"error": "DNA样本不足", "viral_score": 0}
        
        # 1. 基因强度得分：所有基因平均权重×置信度
        gene_strength = self._calc_gene_strength(dna)
        
        # 2. 情感唤起度：高唤起情感（惊讶、喜悦）权重高，低唤起（悲伤）权重低
        emotional_score = self._calc_emotional_arousal(dna)
        
        # 3. 形式匹配度：检查是否命中主流高传播形式
        format_score = self._calc_format_match(dna)
        
        # 4. 话题趋势度：基于性能特征中的增长率估算
        topic_score = self._calc_topic_trend(dna)
        
        # 5. 表现动量：历史表现的稳定性与增长趋势
        momentum_score = self._calc_performance_momentum(dna)
        
        viral_score = round(
            gene_strength * self.weights.get("gene_strength", 0.3) +
            emotional_score * self.weights.get("emotional_arousal", 0.25) +
            format_score * self.weights.get("format_match", 0.2) +
            topic_score * self.weights.get("topic_trend", 0.15) +
            momentum_score * self.weights.get("performance_momentum", 0.1),
            1
        )
        
        factors = {
            "gene_strength": gene_strength,
            "emotional_arousal": emotional_score,
            "format_match": format_score,
            "topic_trend": topic_score,
            "performance_momentum": momentum_score
        }
        
        return {
            "viral_score": viral_score,
            "viral_level": self._get_viral_level(viral_score),
            "factors": factors,
            "recommendation": self._generate_recommendation(viral_score, factors, dna)
        }
    
    def report(self, result: Dict[str, Any]) -> str:
        if "error" in result:
            return f"❌ 预测失败：{result['error']}"
        
        report = f"""## 🔥 爆款潜力预测报告

**爆款指数**：{result['viral_score']}/100 （{result['viral_level']}）

### 📈 预测因子分解
| 因子 | 得分 |
|------|------|
"""
        for factor, score in result["factors"].items():
            report += f"| {factor} | {score:.1f}/100 |\n"
        
        report += f"\n### 💡 优化建议\n{result['recommendation']}\n"
        return report
    
    def _calc_gene_strength(self, dna: ContentDNA) -> float:
        """计算整体基因强度"""
        all_genes = (dna.style_genes + dna.topic_genes + 
                    dna.format_genes + dna.emotion_genes)
        if not all_genes:
            return 50.0
        return sum(g.weight * g.confidence for g in all_genes) / len(all_genes) * 100
    
    def _calc_emotional_arousal(self, dna: ContentDNA) -> float:
        """情感唤起度：高传播情感加权"""
        high_arousal = {"惊讶", "喜悦", "愤怒"}
        low_arousal = {"悲伤", "恐惧"}
        
        score = 50.0
        total_weight = 0
        for gene in dna.emotion_genes:
            if gene.value in high_arousal:
                score += gene.weight * 40
            elif gene.value in low_arousal:
                score -= gene.weight * 20
            total_weight += gene.weight
        
        return max(0, min(100, score)) if total_weight > 0 else 50.0
    
    def _calc_format_match(self, dna: ContentDNA) -> float:
        """形式匹配度：短视频、直播等高频形式加分"""
        viral_formats = {"短视频", "直播", "挑战赛", "教程片段"}
        score = 50.0
        for gene in dna.format_genes:
            if gene.value in viral_formats:
                score += gene.weight * 50
        return min(100, score)
    
    def _calc_topic_trend(self, dna: ContentDNA) -> float:
        """话题趋势：基于增长率和变异系数"""
        performance = dna.performance_traits
        growth = performance.get("growth_rate", 0)
        cv = performance.get("cv_views", 1)
        
        trend_score = 50 + growth * 200 - cv * 30
        return max(0, min(100, trend_score))
    
    def _calc_performance_momentum(self, dna: ContentDNA) -> float:
        """表现动量：平均互动率和样本量信心"""
        avg_engagement = dna.performance_traits.get("avg_engagement_rate", 0)
        sample_size = dna.sample_size
        
        engagement_score = min(avg_engagement * 5000, 100)
        sample_bonus = min(sample_size / 50 * 20, 20)  # 样本越多越可信
        return min(100, engagement_score + sample_bonus)
    
    def _get_viral_level(self, score: float) -> str:
        if score >= self.thresholds.get("viral", 80):
            return "🔥 极高爆款潜力"
        elif score >= self.thresholds.get("high", 65):
            return "📈 高爆款潜力"
        elif score >= self.thresholds.get("moderate", 50):
            return "📊 中等爆款潜力"
        else:
            return "❄️ 爆款潜力较低"
    
    def _generate_recommendation(self, viral_score: float, factors: dict, dna: ContentDNA) -> str:
        tips = []
        if factors["emotional_arousal"] < 60:
            tips.append("建议在内容中加入更多高唤起情感元素（惊讶、喜悦或争议性观点）。")
        if factors["format_match"] < 70:
            tips.append("尝试使用短视频或教程片段等高传播形式。")
        if factors["topic_trend"] < 50:
            tips.append("关注当前平台热门话题，将基因与趋势结合。")
        if factors["gene_strength"] < 60:
            tips.append("核心基因表达不足，需强化内容独特性和辨识度。")
        if not tips:
            tips.append("继续保持现有策略，同时监测基因进化。")
        return "\n".join(f"- {t}" for t in tips)