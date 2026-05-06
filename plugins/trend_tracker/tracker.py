# plugins/trend_tracker/tracker.py
"""DNA趋势追踪器 - 第五块积木：追踪基因进化轨迹，输出趋势预警"""
from typing import Dict, Any, List
from datetime import datetime

from core.plugin_base import BasePlugin
from core.genome import ContentDNA


class TrendTracker(BasePlugin):
    """对比多个时间点的DNA快照，分析进化方向、速度和稳定性"""
    
    def __init__(self, config_path: str = "plugins/trend_tracker/config.json"):
        super().__init__(config_path)
        self.dimensions = self.config.get("tracking_dimensions", [])
        self.thresholds = self.config.get("alert_thresholds", {})
    
    async def analyze(self, dna: ContentDNA, **kwargs) -> Dict[str, Any]:
        """
        输入：dna = 最新DNA
             kwargs['history'] = [ContentDNA, ...] 按时间升序的历史DNA列表
        """
        history: List[ContentDNA] = kwargs.get("history", [])
        if not history:
            return {"error": "未提供历史DNA数据，至少需要一个历史快照"}
        
        # 把当前DNA加入历史末尾
        all_snapshots = history + [dna]
        
        # 1. 各维度权重变化
        weight_trends = self._track_weight_changes(all_snapshots)
        
        # 2. 基因多样性变化
        diversity_trend = self._track_diversity(all_snapshots)
        
        # 3. 置信度变化
        confidence_trend = self._track_confidence(all_snapshots)
        
        # 4. 进化速度（相邻快照间平均变化量）
        evolution_speed = self._calc_evolution_speed(weight_trends)
        
        # 5. 稳定性评分
        stability = self._calc_stability(weight_trends, diversity_trend)
        
        # 6. 生成预警
        alerts = self._generate_trend_alerts(weight_trends, diversity_trend, confidence_trend)
        
        # 7. 预测下一个方向
        prediction = self._predict_next_direction(weight_trends)
        
        return {
            "snapshot_count": len(all_snapshots),
            "time_range": {
                "start": all_snapshots[0].extraction_date.isoformat(),
                "end": all_snapshots[-1].extraction_date.isoformat()
            },
            "weight_trends": weight_trends,
            "diversity_trend": diversity_trend,
            "confidence_trend": confidence_trend,
            "evolution_speed": evolution_speed,
            "stability_score": stability,
            "alerts": alerts,
            "prediction": prediction
        }
    
    def report(self, result: Dict[str, Any]) -> str:
        if "error" in result:
            return f"❌ 追踪失败：{result['error']}"
        
        report = f"""## 📈 DNA趋势追踪报告

**快照数量**：{result['snapshot_count']}
**时间跨度**：{result['time_range']['start']} → {result['time_range']['end']}

### 📊 基因权重趋势
"""
        for dim, trend_data in result["weight_trends"].items():
            direction = "↑" if trend_data["direction"] == "上升" else ("↓" if trend_data["direction"] == "下降" else "→")
            report += f"- **{dim}**：{direction} {trend_data['direction']}（变化量：{trend_data['change']:+.2f}）\n"
        
        report += f"""
### 🧬 多样性趋势
- 当前多样性：{result['diversity_trend']['current']:.2f}
- 变化方向：{result['diversity_trend']['direction']}

### 🎯 进化指标
- 进化速度：{result['evolution_speed']:.3f}/周期
- 稳定性评分：{result['stability_score']}/100

### 🔮 趋势预测
{result['prediction']['summary']}
"""
        if result["alerts"]:
            report += "\n### ⚠️ 趋势预警\n"
            for alert in result["alerts"]:
                report += f"- {alert}\n"
        
        return report
    
    def _track_weight_changes(self, snapshots: List[ContentDNA]) -> Dict[str, Any]:
        """追踪各维度权重变化"""
        trends = {}
        for dim in self.dimensions:
            weights = []
            for snap in snapshots:
                genes = getattr(snap, f"{dim}_genes", [])
                if genes:
                    avg = sum(g.weight for g in genes) / len(genes)
                else:
                    avg = 0
                weights.append(avg)
            
            if len(weights) >= 2:
                change = weights[-1] - weights[0]
                if change > 0.05:
                    direction = "上升"
                elif change < -0.05:
                    direction = "下降"
                else:
                    direction = "稳定"
            else:
                change = 0
                direction = "数据不足"
            
            trends[dim] = {
                "values": [round(w, 3) for w in weights],
                "change": round(change, 3),
                "direction": direction
            }
        return trends
    
    def _track_diversity(self, snapshots: List[ContentDNA]) -> Dict:
        """追踪基因多样性变化"""
        diversities = []
        for snap in snapshots:
            unique = set()
            total = 0
            for dim in self.dimensions:
                genes = getattr(snap, f"{dim}_genes", [])
                unique.update(g.value for g in genes)
                total += len(genes)
            div = len(unique) / max(total, 1)
            diversities.append(round(div, 3))
        
        if len(diversities) >= 2:
            change = diversities[-1] - diversities[0]
            direction = "上升" if change > 0 else ("下降" if change < 0 else "稳定")
        else:
            direction = "数据不足"
        
        return {"values": diversities, "current": diversities[-1], "direction": direction}
    
    def _track_confidence(self, snapshots: List[ContentDNA]) -> Dict:
        """追踪置信度变化"""
        confidences = [round(snap.confidence_score, 3) for snap in snapshots]
        direction = "上升" if confidences[-1] > confidences[0] else ("下降" if confidences[-1] < confidences[0] else "稳定")
        return {"values": confidences, "current": confidences[-1], "direction": direction}
    
    def _calc_evolution_speed(self, weight_trends: Dict) -> float:
        """计算进化速度"""
        changes = [abs(data["change"]) for data in weight_trends.values()]
        return round(sum(changes) / len(changes), 3) if changes else 0
    
    def _calc_stability(self, weight_trends: Dict, diversity: Dict) -> float:
        """稳定性评分：变化越小越稳定"""
        speed = self._calc_evolution_speed(weight_trends)
        div_penalty = 10 if diversity["direction"] == "下降" else 0
        return round(max(0, 100 - speed * 200 - div_penalty), 1)
    
    def _generate_trend_alerts(self, weight_trends, diversity, confidence) -> list:
        """生成趋势预警"""
        alerts = []
        for dim, data in weight_trends.items():
            if abs(data["change"]) > self.thresholds.get("weight_change", 0.3):
                alerts.append(f"{dim}基因权重剧烈变化（{data['change']:+.2f}），建议检查原因")
        if diversity["direction"] == "下降":
            alerts.append("基因多样性持续下降，存在同质化风险")
        if confidence["direction"] == "下降":
            alerts.append("整体置信度下降，数据质量可能退化")
        return alerts
    
    def _predict_next_direction(self, weight_trends: Dict) -> Dict:
        """基于线性外推预测下一个方向"""
        predictions = {}
        for dim, data in weight_trends.items():
            if len(data["values"]) >= 3:
                last_change = data["values"][-1] - data["values"][-2]
                predictions[dim] = "继续上升" if last_change > 0 else ("继续下降" if last_change < 0 else "保持稳定")
            else:
                predictions[dim] = "数据不足"
        
        rising = sum(1 for v in predictions.values() if "上升" in v)
        falling = sum(1 for v in predictions.values() if "下降" in v)
        
        if rising > falling:
            summary = "整体基因权重呈上升趋势，内容影响力有望增强。"
        elif falling > rising:
            summary = "整体基因权重呈下降趋势，需关注内容策略调整。"
        else:
            summary = "基因结构趋于稳定，保持当前策略。"
        
        return {"dimensions": predictions, "summary": summary}