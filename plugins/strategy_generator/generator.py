# plugins/strategy_generator/generator.py
"""内容策略生成器 - 第六块积木：综合所有分析结果，输出可执行策略"""
from typing import Dict, Any, List
from core.plugin_base import BasePlugin
from core.genome import ContentDNA


class StrategyGenerator(BasePlugin):
    """接收DNA及各插件分析结果，生成内容策略简报"""
    
    def __init__(self, config_path: str = "plugins/strategy_generator/config.json"):
        super().__init__(config_path)
        self.dimensions = self.config.get("strategy_dimensions", [])
    
    async def analyze(self, dna: ContentDNA, **kwargs) -> Dict[str, Any]:
        """
        输入：dna = 当前DNA
             kwargs['health'] = 四维健康度分析结果（可选）
             kwargs['viral'] = 爆款预测结果（可选）
             kwargs['competitor'] = 竞品分析结果（可选）
             kwargs['trend'] = 趋势追踪结果（可选）
        输出：策略建议
        """
        health = kwargs.get("health", {})
        viral = kwargs.get("viral", {})
        competitor = kwargs.get("competitor", {})
        trend = kwargs.get("trend", {})
        
        strategies = {}
        
        # 1. 风格方向建议
        strategies["风格方向"] = self._generate_style_strategy(dna, health, trend)
        
        # 2. 话题矩阵建议
        strategies["话题矩阵"] = self._generate_topic_strategy(dna, health, viral)
        
        # 3. 形式优化建议
        strategies["形式优化"] = self._generate_format_strategy(dna, viral, competitor)
        
        # 4. 情感调性建议
        strategies["情感调性"] = self._generate_emotion_strategy(dna, viral, health)
        
        # 5. 整合优先级
        priority_actions = self._extract_priorities(strategies, health, viral, trend)
        
        # 6. 生成执行计划
        execution_plan = self._generate_execution_plan(priority_actions)
        
        return {
            "account_id": dna.account_id,
            "strategy_version": dna.dna_version,
            "strategies": strategies,
            "priority_actions": priority_actions,
            "execution_plan": execution_plan,
            "confidence": self._calc_strategy_confidence(dna, health, trend),
            "generated_at": dna.extraction_date.isoformat()
        }
    
    def report(self, result: Dict[str, Any]) -> str:
        if "error" in result:
            return f"❌ 生成失败：{result['error']}"
        
        report = f"""## 🎯 内容策略简报

**账号**：{result['account_id']}
**策略版本**：{result['strategy_version']}
**置信度**：{result['confidence']*100:.0f}%

---
"""
        for dim, strategy in result["strategies"].items():
            report += f"""
### {dim}
- **当前状态**：{strategy.get('current_state', 'N/A')}
- **优化方向**：{strategy.get('direction', 'N/A')}
- **具体建议**：{strategy.get('suggestion', 'N/A')}
"""
        
        report += "\n---\n### 🔴 优先级行动清单\n"
        for i, action in enumerate(result["priority_actions"], 1):
            report += f"{i}. [{action['priority']}] {action['action']} — {action['reason']}\n"
        
        report += f"\n### 📅 执行计划\n{result['execution_plan']}\n"
        return report
    
    def _generate_style_strategy(self, dna: ContentDNA, health: Dict, trend: Dict) -> Dict:
        """生成风格策略"""
        genes = dna.style_genes
        if not genes:
            return {"current_state": "未检测到风格基因", "direction": "需建立基础风格", "suggestion": "先确定1-2个核心风格深耕"}
        
        strongest = max(genes, key=lambda g: g.weight)
        
        # 从趋势看是否正在风格转型
        if trend:
            weight_trend = trend.get("weight_trends", {}).get("style", {})
            if weight_trend.get("direction") == "下降":
                return {
                    "current_state": f"核心风格：{strongest.value}（正在弱化）",
                    "direction": "风格转型期，需找到新方向",
                    "suggestion": f"在保持{strongest.value}的同时，测试1个新风格，观察数据反馈"
                }
        
        # 从健康度看是否风格单一
        if health:
            system_scores = health.get("system_scores", {})
            if system_scores.get("个人成长", 100) < 60:
                return {
                    "current_state": f"核心风格：{strongest.value}",
                    "direction": "强化风格辨识度",
                    "suggestion": "增加个人特色元素，提升风格记忆点"
                }
        
        return {
            "current_state": f"核心风格：{strongest.value}（权重{strongest.weight:.2f}）",
            "direction": "持续强化核心风格",
            "suggestion": f"围绕{strongest.value}创作系列内容，建立风格认知"
        }
    
    def _generate_topic_strategy(self, dna: ContentDNA, health: Dict, viral: Dict) -> Dict:
        """生成话题策略"""
        genes = dna.topic_genes
        if not genes:
            return {"current_state": "未检测到话题基因", "direction": "需建立话题定位", "suggestion": "选择1-2个垂直领域深耕"}
        
        top_topics = sorted(genes, key=lambda g: g.weight, reverse=True)[:3]
        topics_str = "、".join(g.value for g in top_topics)
        
        suggestion = f"主力话题：{topics_str}"
        if viral:
            viral_score = viral.get("viral_score", 50)
            if viral_score < 50:
                suggestion += "。建议关注平台热门话题，将核心话题与趋势结合"
        
        return {
            "current_state": f"话题矩阵：{topics_str}",
            "direction": "拓展话题关联性",
            "suggestion": suggestion
        }
    
    def _generate_format_strategy(self, dna: ContentDNA, viral: Dict, competitor: Dict) -> Dict:
        """生成形式策略"""
        genes = dna.format_genes
        if not genes:
            return {"current_state": "未指定形式", "direction": "需确定主形式", "suggestion": "短视频是当前主流高效率形式，建议优先测试"}
        
        main_format = max(genes, key=lambda g: g.weight)
        
        suggestion = f"主力形式：{main_format.value}"
        if viral:
            factors = viral.get("factors", {})
            if factors.get("format_match", 100) < 60:
                suggestion += "。尝试增加短视频或直播类内容"
        
        if competitor:
            for comp_result in competitor.get("results", []):
                for dim, data in comp_result.get("dimension_gaps", {}).items():
                    if dim == "format" and data["status"] == "劣势":
                        suggestion += f"。竞品{comp_result['competitor_name']}在形式上领先，建议研究其形式策略"
        
        return {
            "current_state": f"主要形式：{main_format.value}",
            "direction": "优化形式组合",
            "suggestion": suggestion
        }
    
    def _generate_emotion_strategy(self, dna: ContentDNA, viral: Dict, health: Dict) -> Dict:
        """生成情感策略"""
        genes = dna.emotion_genes
        if not genes:
            return {"current_state": "情感表达不足", "direction": "需注入情感元素", "suggestion": "内容中增加情感锚点（惊讶、喜悦等高唤起情感）"}
        
        top_emotions = sorted(genes, key=lambda g: g.weight, reverse=True)[:2]
        emotions_str = "、".join(g.value for g in top_emotions)
        
        suggestion = f"主要情感调性：{emotions_str}"
        if viral:
            factors = viral.get("factors", {})
            if factors.get("emotional_arousal", 100) < 50:
                suggestion += "。增加高唤起情感（惊讶、喜悦）的运用"
        
        return {
            "current_state": f"情感调性：{emotions_str}",
            "direction": "强化情感共鸣",
            "suggestion": suggestion
        }
    
    def _extract_priorities(self, strategies: Dict, health: Dict, viral: Dict, trend: Dict) -> List[Dict]:
        """提取优先级行动清单"""
        priorities = []
        
        # 健康度预警
        if health:
            overall = health.get("overall_health", 100)
            if overall < 60:
                priorities.append({"priority": "🔴 高", "action": "提升内容基因健康度", "reason": f"当前健康指数{overall}/100，需系统性优化"})
        
        # 爆款潜力低
        if viral:
            score = viral.get("viral_score", 100)
            if score < 50:
                priorities.append({"priority": "🔴 高", "action": "优化爆款要素组合", "reason": f"爆款潜力{score}/100，重点提升情感唤起和形式匹配"})
        
        # 趋势下降
        if trend:
            for dim, data in trend.get("weight_trends", {}).items():
                if data.get("direction") == "下降":
                    priorities.append({"priority": "🟡 中", "action": f"关注{dim}基因弱化趋势", "reason": f"{dim}权重持续下降，需评估是否需要策略调整"})
        
        # 多样性不足
        if health:
            scores = health.get("system_scores", {})
            for system, score in scores.items():
                if score < 40:
                    priorities.append({"priority": "🟡 中", "action": f"强化{system}维度", "reason": f"得分{score}/100，处于薄弱状态"})
        
        if not priorities:
            priorities.append({"priority": "🟢 低", "action": "保持当前策略", "reason": "各项指标健康，持续监测"})
        
        return priorities[:5]
    
    def _generate_execution_plan(self, priorities: List[Dict]) -> str:
        """生成执行计划"""
        plan = "**本周执行计划**：\n"
        for i, p in enumerate(priorities[:3], 1):
            plan += f"{i}. {p['action']}\n"
        plan += "\n**两周优化目标**：将优先级最高的行动项完成并观察数据变化。"
        return plan
    
    def _calc_strategy_confidence(self, dna: ContentDNA, health: Dict, trend: Dict) -> float:
        """计算策略置信度"""
        base = dna.confidence_score
        if health:
            base = (base + (health.get("overall_health", 100) / 100)) / 2
        if trend:
            stability = trend.get("stability_score", 100) / 100
            base = (base + stability) / 2
        return round(base, 2)