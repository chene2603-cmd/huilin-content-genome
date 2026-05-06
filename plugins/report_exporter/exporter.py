# plugins/report_exporter/exporter.py
"""智能报告导出器 - 第七块积木：整合全部分析结果，生成并导出专业报告"""
import os
from datetime import datetime
from typing import Dict, Any, Optional

from core.plugin_base import BasePlugin
from core.genome import ContentDNA


class ReportExporter(BasePlugin):
    """接收所有积木的分析结果，生成一份统一、专业的 Markdown 报告并导出"""
    
    def __init__(self, config_path: str = "plugins/report_exporter/config.json"):
        super().__init__(config_path)
        self.title = self.config.get("title", "内容DNA报告")
        self.branding = self.config.get("branding", {})
    
    async def analyze(self, dna: ContentDNA, **kwargs) -> Dict[str, Any]:
        """
        输入：dna = 当前DNA
             kwargs = {
                 'health': 四维健康度结果,
                 'viral': 爆款预测结果,
                 'trend': 趋势追踪结果,
                 'strategy': 策略生成结果,
                 'competitor': 竞品分析结果（可选）
             }
        输出：包含完整报告文本及导出信息
        """
        sections = kwargs
        if not sections:
            return {"error": "未提供任何分析数据"}
        
        # 生成完整报告
        report_text = self._build_full_report(dna, sections)
        
        # 导出到文件
        export_path = self._export_to_file(dna, report_text)
        
        return {
            "account_id": dna.account_id,
            "report_title": self.title,
            "generated_at": datetime.now().isoformat(),
            "report_text": report_text,
            "export_path": export_path,
            "file_size": os.path.getsize(export_path) if export_path else 0,
            "sections_included": list(sections.keys())
        }
    
    def report(self, result: Dict[str, Any]) -> str:
        if "error" in result:
            return f"❌ 导出失败：{result['error']}"
        return result["report_text"]
    
    def _build_full_report(self, dna: ContentDNA, sections: Dict[str, Any]) -> str:
        """构建完整报告"""
        report = f"""# {self.title}

**账号ID**：{dna.account_id}
**DNA指纹**：{dna.get_dna_fingerprint()}
**DNA版本**：{dna.dna_version}
**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**样本数量**：{dna.sample_size}
**数据置信度**：{dna.confidence_score*100:.0f}%

---
"""
        # 1. 四维健康度
        if "health" in sections:
            health = sections["health"]
            if "error" not in health:
                report += self._format_health_section(health)
        
        # 2. 爆款预测
        if "viral" in sections:
            viral = sections["viral"]
            if "error" not in viral:
                report += self._format_viral_section(viral)
        
        # 3. 趋势追踪
        if "trend" in sections:
            trend = sections["trend"]
            if "error" not in trend:
                report += self._format_trend_section(trend)
        
        # 4. 策略生成
        if "strategy" in sections:
            strategy = sections["strategy"]
            if "error" not in strategy:
                report += self._format_strategy_section(strategy)
        
        # 5. 竞品分析
        if "competitor" in sections:
            competitor = sections["competitor"]
            if "error" not in competitor:
                report += self._format_competitor_section(competitor)
        
        # 页脚
        report += f"\n---\n*本报告由 {self.branding.get('powered_by', 'huilin-content-genome')} v{self.branding.get('version', '2.0')} 自动生成*\n"
        
        return report
    
    def _format_health_section(self, health: Dict) -> str:
        section = "## 🧬 四维健康度\n\n"
        section += f"**综合健康指数**：{health.get('overall_health', 'N/A')}/100 （{health.get('health_level', 'N/A')}）\n\n"
        section += "| 系统 | 得分 |\n|------|------|\n"
        for system, score in health.get("system_scores", {}).items():
            section += f"| {system} | {score}/100 |\n"
        section += "\n"
        return section
    
    def _format_viral_section(self, viral: Dict) -> str:
        section = "## 🔥 爆款潜力\n\n"
        section += f"**爆款指数**：{viral.get('viral_score', 'N/A')}/100 （{viral.get('viral_level', 'N/A')}）\n\n"
        if "factors" in viral:
            section += "| 因子 | 得分 |\n|------|------|\n"
            for factor, score in viral["factors"].items():
                section += f"| {factor} | {score:.1f}/100 |\n"
            section += "\n"
        if "recommendation" in viral:
            section += f"**优化建议**：{viral['recommendation']}\n\n"
        return section
    
    def _format_trend_section(self, trend: Dict) -> str:
        section = "## 📈 趋势追踪\n\n"
        section += f"**快照数量**：{trend.get('snapshot_count', 'N/A')}\n"
        section += f"**进化速度**：{trend.get('evolution_speed', 'N/A')}\n"
        section += f"**稳定性**：{trend.get('stability_score', 'N/A')}/100\n\n"
        if "alerts" in trend and trend["alerts"]:
            section += "### ⚠️ 预警\n"
            for alert in trend["alerts"]:
                section += f"- {alert}\n"
            section += "\n"
        return section
    
    def _format_strategy_section(self, strategy: Dict) -> str:
        section = "## 🎯 策略建议\n\n"
        if "priority_actions" in strategy:
            section += "### 优先级行动清单\n"
            for i, action in enumerate(strategy["priority_actions"], 1):
                section += f"{i}. [{action['priority']}] {action['action']} — {action['reason']}\n"
            section += "\n"
        return section
    
    def _format_competitor_section(self, competitor: Dict) -> str:
        section = "## 🏆 竞品对比\n\n"
        for r in competitor.get("results", []):
            section += f"**{r['competitor_name']}**\n"
            section += f"- 基因相似度：{r['similarity']*100:.1f}%\n"
            section += f"- 竞争指数：{r['competitive_index']}/100\n\n"
        return section
    
    def _export_to_file(self, dna: ContentDNA, report_text: str) -> str:
        """导出到reports目录"""
        os.makedirs("reports", exist_ok=True)
        filename = f"reports/{dna.account_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_text)
        return filename