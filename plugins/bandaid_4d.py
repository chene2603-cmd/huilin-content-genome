#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DNA四维分析补丁 v2.1
为内容DNA平台添加四维健康度分析功能
集成点：ContentDNA类增强
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import hashlib
import os
from dataclasses import field
from pydantic import Field


class DNA四维分析补丁:
    """DNA四维分析增强 - 集成补丁"""
    
    def __init__(self, config_path: str = "dna_4d_config.json"):
        self.config = self._load_config(config_path)
        self.analysis_history = []
        self.max_history = 50
        
        # 四维分析类型映射
        self.type_mapping = {
            "style": "个人成长",      # 风格基因 -> 个人成长系统
            "topic": "商业系统",      # 话题基因 -> 商业系统
            "format": "技术产品",     # 形式基因 -> 技术产品
            "emotion": "社会组织"     # 情感基因 -> 社会组织
        }
        
        # 反向映射
        self.reverse_mapping = {v: k for k, v in self.type_mapping.items()}
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        default_config = {
            "维度得分规则": {
                "商业系统": {
                    "产品": {"关键词": ["用户", "体验", "NPS", "迭代", "需求", "痛点"], "基础分": 30},
                    "运营": {"关键词": ["留存", "活跃", "转化", "成本", "ROI", "复购"], "基础分": 30},
                    "技术": {"关键词": ["架构", "扩展", "可用", "安全", "并发", "延迟"], "基础分": 30},
                    "市场": {"关键词": ["份额", "增长", "品牌", "渠道", "渗透", "声量"], "基础分": 30}
                },
                "技术产品": {
                    "功能": {"关键词": ["完成度", "覆盖", "场景", "闭环", "效率"], "基础分": 30},
                    "体验": {"关键词": ["流畅", "美观", "易用", "无障碍", "NPS"], "基础分": 30},
                    "架构": {"关键词": ["解耦", "可扩展", "容错", "性能", "一致性"], "基础分": 30},
                    "生态": {"关键词": ["API", "插件", "社区", "开发者", "文档"], "基础分": 30}
                },
                "个人成长": {
                    "输入": {"关键词": ["阅读", "课程", "实践", "导师", "信息源"], "基础分": 30},
                    "处理": {"关键词": ["笔记", "思考", "模型", "复盘", "写作"], "基础分": 30},
                    "输出": {"关键词": ["作品", "分享", "教学", "项目", "演讲"], "基础分": 30},
                    "反馈": {"关键词": ["数据", "评论", "测试", "迭代", "反思"], "基础分": 30}
                },
                "社会组织": {
                    "结构": {"关键词": ["层级", "角色", "决策", "信息流", "自治"], "基础分": 30},
                    "文化": {"关键词": ["信任", "透明", "使命", "价值观", "归属"], "基础分": 30},
                    "流程": {"关键词": ["SOP", "自动化", "敏捷", "回顾", "效率"], "基础分": 30},
                    "目标": {"关键词": ["OKR", "对齐", "北极星", "衡量", "节奏"], "基础分": 30}
                }
            },
            "权重配置": {
                "基因强度权重": 0.6,
                "基因多样性权重": 0.2,
                "趋势稳定性权重": 0.1,
                "平台适应性权重": 0.1
            }
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    # 深度合并配置
                    return self._deep_merge(default_config, user_config)
            except Exception as e:
                print(f"⚠️ 加载配置文件失败，使用默认配置: {e}")
        
        return default_config
    
    def _deep_merge(self, base: Dict, overlay: Dict) -> Dict:
        """深度合并字典"""
        result = base.copy()
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def analyze_content_dna(self, dna: 'ContentDNA') -> Dict[str, Any]:
        """分析内容DNA的四维健康度"""
        
        # 转换内容DNA为四维分析格式
        four_dim_data = self._convert_dna_to_4d(dna)
        
        # 执行四维分析
        analysis_result = self._perform_4d_analysis(four_dim_data, dna)
        
        # 计算健康指数
        health_score = self._calculate_health_score(analysis_result, dna)
        
        # 生成洞察和建议
        insights = self._generate_insights(analysis_result, dna)
        recommendations = self._generate_recommendations(analysis_result, dna)
        
        # 构建结果
        result = {
            "analysis_id": self._generate_analysis_id(dna),
            "timestamp": datetime.now().isoformat(),
            "dna_fingerprint": dna.get_dna_fingerprint(),
            "account_id": dna.account_id,
            "four_dim_analysis": analysis_result,
            "health_metrics": health_score,
            "insights": insights,
            "recommendations": recommendations,
            "trend_data": self._get_trend_data(dna)
        }
        
        # 保存到历史
        self._save_to_history(result)
        
        return result
    
    def _convert_dna_to_4d(self, dna: 'ContentDNA') -> Dict[str, Any]:
        """将内容DNA转换为四维分析数据"""
        four_dim_data = {}
        
        # 处理每个基因类型
        for gene_type in ["style", "topic", "format", "emotion"]:
            genes = getattr(dna, f"{gene_type}_genes", [])
            four_dim_type = self.type_mapping.get(gene_type, "通用系统")
            
            if four_dim_type not in four_dim_data:
                four_dim_data[four_dim_type] = {}
            
            # 计算该类型基因的强度
            if genes:
                avg_strength = sum(g.weight * g.confidence for g in genes) / len(genes)
                top_genes = sorted(genes, key=lambda x: x.weight, reverse=True)[:3]
                
                four_dim_data[four_dim_type][gene_type] = {
                    "strength": avg_strength * 100,  # 转换为0-100分
                    "top_genes": [{"value": g.value, "weight": g.weight} for g in top_genes],
                    "gene_count": len(genes),
                    "confidence_avg": sum(g.confidence for g in genes) / len(genes)
                }
        
        return four_dim_data
    
    def _perform_4d_analysis(self, four_dim_data: Dict, dna: 'ContentDNA') -> Dict[str, Any]:
        """执行四维分析"""
        analysis_result = {}
        
        for system_type, gene_data in four_dim_data.items():
            # 获取该系统的维度
            dimensions = self._get_dimensions_for_system(system_type)
            system_result = {}
            
            for dimension in dimensions:
                # 计算每个维度的得分
                score = self._calculate_dimension_score(dimension, gene_data, dna)
                
                system_result[dimension] = {
                    "score": score,
                    "level": self._get_score_level(score),
                    "hit_keywords": self._find_hit_keywords(dimension, gene_data, system_type),
                    "strength_percentage": f"{score}%",
                    "interpretation": self._interpret_dimension_score(dimension, score, gene_data)
                }
            
            # 计算系统健康度
            system_health = self._calculate_system_health(system_result)
            
            analysis_result[system_type] = {
                "dimensions": system_result,
                "system_health": system_health,
                "gene_summary": {
                    "total_genes": sum(data.get("gene_count", 0) for data in gene_data.values()),
                    "avg_confidence": sum(data.get("confidence_avg", 0) for data in gene_data.values()) / max(len(gene_data), 1)
                }
            }
        
        return analysis_result
    
    def _calculate_dimension_score(self, dimension: str, gene_data: Dict, dna: 'ContentDNA') -> float:
        """计算维度得分"""
        rules = self.config["维度得分规则"]
        
        # 获取系统类型
        system_type = None
        for sys_type, dims in rules.items():
            if dimension in dims:
                system_type = sys_type
                break
        
        if not system_type:
            return 50.0  # 默认分
        
        # 基础分
        base_score = rules[system_type][dimension]["基础分"]
        
        # 根据基因数据调整分数
        gene_contribution = 0
        for gene_type, data in gene_data.items():
            strength = data.get("strength", 0)
            gene_contribution += strength * 0.2  # 基因强度贡献
        
        # 关键词匹配
        keywords = rules[system_type][dimension]["关键词"]
        keyword_hits = 0
        
        # 检查DNA的基因值中是否包含关键词
        for gene_type in ["style", "topic", "format", "emotion"]:
            genes = getattr(dna, f"{gene_type}_genes", [])
            for gene in genes:
                for keyword in keywords:
                    if keyword in gene.value:
                        keyword_hits += 1
                        break
        
        keyword_contribution = min(keyword_hits * 5, 20)  # 最多20分
        
        # 计算最终得分
        final_score = base_score + gene_contribution + keyword_contribution
        
        # 确保在0-100范围内
        return max(0, min(100, final_score))
    
    def _calculate_health_score(self, analysis_result: Dict, dna: 'ContentDNA') -> Dict[str, Any]:
        """计算健康指数"""
        health_metrics = {
            "scores": {},
            "trends": {},
            "alerts": []
        }
        
        weights = self.config["权重配置"]
        
        # 1. 基因强度健康度
        gene_strength_score = self._calculate_gene_strength_score(dna)
        health_metrics["scores"]["gene_strength"] = gene_strength_score
        
        # 2. 基因多样性健康度
        gene_diversity_score = self._calculate_gene_diversity_score(dna)
        health_metrics["scores"]["gene_diversity"] = gene_diversity_score
        
        # 3. 趋势稳定性
        trend_stability_score = self._calculate_trend_stability_score(dna)
        health_metrics["scores"]["trend_stability"] = trend_stability_score
        
        # 4. 平台适应性
        platform_adaptability_score = self._calculate_platform_adaptability_score(dna)
        health_metrics["scores"]["platform_adaptability"] = platform_adaptability_score
        
        # 计算综合健康指数
        weighted_sum = (
            gene_strength_score * weights["基因强度权重"] +
            gene_diversity_score * weights["基因多样性权重"] +
            trend_stability_score * weights["趋势稳定性权重"] +
            platform_adaptability_score * weights["平台适应性权重"]
        )
        
        health_metrics["overall_health_index"] = round(weighted_sum, 2)
        health_metrics["health_level"] = self._get_health_level(weighted_sum)
        
        # 生成健康警报
        if gene_strength_score < 60:
            health_metrics["alerts"].append("基因强度不足，需要强化核心基因")
        if gene_diversity_score < 50:
            health_metrics["alerts"].append("基因多样性不足，存在过度依赖风险")
        if trend_stability_score < 40:
            health_metrics["alerts"].append("趋势稳定性差，表现波动大")
        
        return health_metrics
    
    def _calculate_gene_strength_score(self, dna: 'ContentDNA') -> float:
        """计算基因强度得分"""
        strength_scores = []
        
        for gene_type in ["style", "topic", "format", "emotion"]:
            genes = getattr(dna, f"{gene_type}_genes", [])
            if genes:
                avg_strength = sum(g.weight * g.confidence for g in genes) / len(genes)
                strength_scores.append(avg_strength * 100)
        
        if not strength_scores:
            return 0.0
        
        return sum(strength_scores) / len(strength_scores)
    
    def _calculate_gene_diversity_score(self, dna: 'ContentDNA') -> float:
        """计算基因多样性得分"""
        unique_values = set()
        total_genes = 0
        
        for gene_type in ["style", "topic", "format", "emotion"]:
            genes = getattr(dna, f"{gene_type}_genes", [])
            unique_values.update([g.value for g in genes])
            total_genes += len(genes)
        
        if total_genes == 0:
            return 0.0
        
        # 多样性得分 = 唯一值比例 * 100
        diversity_ratio = len(unique_values) / total_genes
        return diversity_ratio * 100
    
    def _calculate_trend_stability_score(self, dna: 'ContentDNA') -> float:
        """计算趋势稳定性得分"""
        # 这里需要历史数据，简化实现
        performance = dna.performance_traits
        
        if "cv_views" in performance:
            cv = performance["cv_views"]
            if cv == 0:
                return 100.0
            # 变异系数越小，稳定性越高
            stability = max(0, 100 - cv * 100)
            return stability
        
        return 70.0  # 默认分
    
    def _calculate_platform_adaptability_score(self, dna: 'ContentDNA') -> float:
        """计算平台适应性得分"""
        # 简化实现，实际应根据基因的平台适应性计算
        score = 0.0
        count = 0
        
        for gene_type in ["style", "topic", "format", "emotion"]:
            genes = getattr(dna, f"{gene_type}_genes", [])
            for gene in genes[:3]:  # 只考虑前3个主要基因
                # 检查基因值是否包含平台相关关键词
                platform_keywords = ["短视频", "长视频", "直播", "图文", "多平台"]
                for keyword in platform_keywords:
                    if keyword in gene.value:
                        score += gene.weight * 20
                        count += 1
                        break
        
        if count == 0:
            return 60.0  # 默认分
        
        return score / count
    
    def _generate_insights(self, analysis_result: Dict, dna: 'ContentDNA') -> List[Dict[str, Any]]:
        """生成洞察"""
        insights = []
        
        # 1. 基因强度洞察
        strength_scores = []
        for gene_type in ["style", "topic", "format", "emotion"]:
            genes = getattr(dna, f"{gene_type}_genes", [])
            if genes:
                avg_strength = sum(g.weight * g.confidence for g in genes) / len(genes)
                strength_scores.append((gene_type, avg_strength))
        
        if strength_scores:
            strongest = max(strength_scores, key=lambda x: x[1])
            weakest = min(strength_scores, key=lambda x: x[1])
            
            insights.append({
                "type": "基因强度",
                "content": f"最强基因维度：{strongest[0]}({strongest[1]*100:.1f}分)，最弱：{weakest[0]}({weakest[1]*100:.1f}分)",
                "severity": "warning" if weakest[1] < 0.3 else "info"
            })
        
        # 2. 四维平衡洞察
        dimension_scores = []
        for system_type, system_data in analysis_result.items():
            for dim_name, dim_data in system_data["dimensions"].items():
                dimension_scores.append((f"{system_type}-{dim_name}", dim_data["score"]))
        
        if dimension_scores:
            score_values = [score for _, score in dimension_scores]
            max_gap = max(score_values) - min(score_values)
            
            if max_gap > 30:
                insights.append({
                    "type": "四维平衡",
                    "content": f"维度间差距过大({max_gap:.1f}分)，需要优化平衡性",
                    "severity": "error"
                })
        
        # 3. 趋势洞察
        trends = self._get_trend_data(dna)
        if trends and "growth_rate" in trends:
            growth = trends["growth_rate"]
            if growth > 0.1:
                insights.append({
                    "type": "增长趋势",
                    "content": f"保持强劲增长趋势(增长率：{growth*100:.1f}%)",
                    "severity": "success"
                })
            elif growth < -0.1:
                insights.append({
                    "type": "衰退预警",
                    "content": f"出现衰退趋势(增长率：{growth*100:.1f}%)",
                    "severity": "error"
                })
        
        return insights
    
    def _generate_recommendations(self, analysis_result: Dict, dna: 'ContentDNA') -> List[Dict[str, Any]]:
        """生成推荐"""
        recommendations = []
        
        # 基于基因强度的推荐
        for gene_type in ["style", "topic", "format", "emotion"]:
            genes = getattr(dna, f"{gene_type}_genes", [])
            if genes:
                avg_weight = sum(g.weight for g in genes) / len(genes)
                if avg_weight < 0.3:
                    recommendations.append({
                        "priority": "high",
                        "area": f"{gene_type}_genes",
                        "action": f"强化{gene_type}基因，当前平均权重{avg_weight:.2f}",
                        "reason": "基因权重过低，影响内容表现"
                    })
        
        # 基于四维分析的推荐
        for system_type, system_data in analysis_result.items():
            for dim_name, dim_data in system_data["dimensions"].items():
                if dim_data["score"] < 60:
                    recommendations.append({
                        "priority": "medium",
                        "area": f"{system_type}.{dim_name}",
                        "action": f"提升{system_type}系统的{dim_name}维度",
                        "reason": f"当前得分{dim_data['score']}分，低于健康阈值"
                    })
        
        # 去重和排序
        seen = set()
        unique_recs = []
        for rec in recommendations:
            key = (rec["area"], rec["action"])
            if key not in seen:
                seen.add(key)
                unique_recs.append(rec)
        
        # 按优先级排序
        priority_order = {"high": 0, "medium": 1, "low": 2}
        unique_recs.sort(key=lambda x: priority_order[x["priority"]])
        
        return unique_recs
    
    def _get_trend_data(self, dna: 'ContentDNA') -> Optional[Dict[str, Any]]:
        """获取趋势数据"""
        # 从performance_traits中提取趋势数据
        trends = {}
        performance = dna.performance_traits
        
        if "growth_rate" in performance:
            trends["growth_rate"] = performance["growth_rate"]
        
        if "cv_views" in performance:
            trends["stability"] = 1 - performance["cv_views"]
        
        return trends if trends else None
    
    def _save_to_history(self, result: Dict):
        """保存到历史记录"""
        self.analysis_history.append(result)
        if len(self.analysis_history) > self.max_history:
            self.analysis_history.pop(0)
        
        # 自动保存到文件
        self._auto_save_history()
    
    def _auto_save_history(self):
        """自动保存历史记录"""
        try:
            with open("dna_4d_history.json", "w", encoding="utf-8") as f:
                json.dump({
                    "history": self.analysis_history,
                    "last_updated": datetime.now().isoformat(),
                    "total_analyses": len(self.analysis_history)
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存历史记录失败: {e}")
    
    def _generate_analysis_id(self, dna: 'ContentDNA') -> str:
        """生成分析ID"""
        raw = f"{dna.account_id}_{dna.get_dna_fingerprint()}_{datetime.now().isoformat()}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]
    
    def _get_dimensions_for_system(self, system_type: str) -> List[str]:
        """获取系统的维度"""
        rules = self.config["维度得分规则"]
        if system_type in rules:
            return list(rules[system_type].keys())
        return ["维度A", "维度B", "维度C", "维度D"]
    
    def _get_score_level(self, score: float) -> str:
        """获取分数等级"""
        if score >= 80:
            return "优秀"
        elif score >= 60:
            return "良好"
        elif score >= 40:
            return "一般"
        else:
            return "薄弱"
    
    def _find_hit_keywords(self, dimension: str, gene_data: Dict, system_type: str) -> List[str]:
        """查找命中的关键词"""
        rules = self.config["维度得分规则"]
        if system_type in rules and dimension in rules[system_type]:
            keywords = rules[system_type][dimension]["关键词"]
            
            hit_keywords = []
            for gene_type, data in gene_data.items():
                for gene_info in data.get("top_genes", []):
                    gene_value = gene_info["value"]
                    for keyword in keywords:
                        if keyword in gene_value and keyword not in hit_keywords:
                            hit_keywords.append(keyword)
            
            return hit_keywords[:5]  # 最多返回5个
        
        return []
    
    def _interpret_dimension_score(self, dimension: str, score: float, gene_data: Dict) -> str:
        """解释维度得分"""
        if score >= 80:
            return f"{dimension}维度表现优秀，基因组合健康"
        elif score >= 60:
            return f"{dimension}维度表现良好，有提升空间"
        elif score >= 40:
            return f"{dimension}维度表现一般，需要关注"
        else:
            return f"{dimension}维度表现薄弱，急需优化"
    
    def _calculate_system_health(self, system_result: Dict) -> Dict[str, Any]:
        """计算系统健康度"""
        scores = [dim["score"] for dim in system_result.values()]
        
        if not scores:
            return {
                "avg_score": 0,
                "max_gap": 0,
                "health_index": 0,
                "balance": "未知"
            }
        
        avg_score = sum(scores) / len(scores)
        max_gap = max(scores) - min(scores) if scores else 0
        
        # 健康指数 = 平均分 - 最大差距 * 0.2
        health_index = avg_score - max_gap * 0.2
        
        if max_gap < 20:
            balance = "均衡"
        elif max_gap < 40:
            balance = "基本均衡"
        else:
            balance = "失衡"
        
        return {
            "avg_score": round(avg_score, 1),
            "max_gap": round(max_gap, 1),
            "health_index": round(max(0, health_index), 1),
            "balance": balance
        }
    
    def _get_health_level(self, score: float) -> str:
        """获取健康等级"""
        if score >= 80:
            return "非常健康"
        elif score >= 60:
            return "健康"
        elif score >= 40:
            return "亚健康"
        else:
            return "不健康"


# ==================== 补丁应用 ====================

def apply_dna_4d_patch_to_dna_class():
    """将DNA四维分析补丁应用到ContentDNA类"""
    
    # 1. 在ContentDNA类中添加四维分析字段
    original_ContentDNA = None  # 这应该从原始模块导入
    
    # 这里我们创建一个增强的ContentDNA类
    class EnhancedContentDNA(original_ContentDNA if original_ContentDNA else object):
        """增强的ContentDNA类，包含四维分析功能"""
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._4d_analyzer = DNA四维分析补丁()
            self._4d_analysis_result = None
            self._last_4d_analysis_time = None
        
        def perform_4d_analysis(self) -> Dict[str, Any]:
            """执行四维分析"""
            if (self._4d_analysis_result is None or 
                self._last_4d_analysis_time is None or
                (datetime.now() - self._last_4d_analysis_time).days > 1):
                
                self._4d_analysis_result = self._4d_analyzer.analyze_content_dna(self)
                self._last_4d_analysis_time = datetime.now()
            
            return self._4d_analysis_result
        
        def get_health_report(self, format: str = "dict") -> Any:
            """获取健康报告"""
            analysis = self.perform_4d_analysis()
            
            if format == "markdown":
                return self._generate_health_markdown(analysis)
            elif format == "json":
                return json.dumps(analysis, ensure_ascii=False, indent=2)
            else:
                return analysis
        
        def _generate_health_markdown(self, analysis: Dict) -> str:
            """生成Markdown格式的健康报告"""
            lines = []
            
            lines.append("# 🧬 内容DNA健康分析报告")
            lines.append("")
            lines.append(f"**账号**: {analysis['account_id']}")
            lines.append(f"**DNA指纹**: {analysis['dna_fingerprint']}")
            lines.append(f"**分析时间**: {analysis['timestamp']}")
            lines.append("")
            
            # 健康指数
            health = analysis['health_metrics']
            lines.append("## 📈 健康指数总览")
            lines.append(f"**综合健康指数**: {health['overall_health_index']}/100")
            lines.append(f"**健康等级**: {health['health_level']}")
            lines.append("")
            
            # 分项得分
            lines.append("### 🎯 分项得分")
            for metric, score in health['scores'].items():
                lines.append(f"- **{metric}**: {score:.1f}/100")
            lines.append("")
            
            # 四维分析
            lines.append("## 🧩 四维分析")
            for system_type, system_data in analysis['four_dim_analysis'].items():
                lines.append(f"### {system_type}")
                lines.append(f"系统健康度: {system_data['system_health']['health_index']}/100")
                lines.append("")
                
                for dim_name, dim_data in system_data['dimensions'].items():
                    bar = "█" * (int(dim_data['score']) // 10) + "░" * (10 - int(dim_data['score']) // 10)
                    lines.append(f"- **{dim_name}**: {bar} {dim_data['score']}/100 ({dim_data['level']})")
                    if dim_data['hit_keywords']:
                        lines.append(f"  命中关键词: {', '.join(dim_data['hit_keywords'])}")
                lines.append("")
            
            # 洞察
            lines.append("## 💡 核心洞察")
            for insight in analysis['insights']:
                severity_icon = {
                    'error': '❌',
                    'warning': '⚠️',
                    'info': 'ℹ️',
                    'success': '✅'
                }.get(insight.get('severity', 'info'), 'ℹ️')
                
                lines.append(f"{severity_icon} **{insight['type']}**: {insight['content']}")
            lines.append("")
            
            # 建议
            lines.append("## ✅ 优化建议")
            priority_icons = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }
            
            for rec in analysis['recommendations']:
                icon = priority_icons.get(rec['priority'], '⚪')
                lines.append(f"{icon} **{rec['area']}**: {rec['action']}")
                lines.append(f"  原因: {rec['reason']}")
            lines.append("")
            
            # 警报
            if health['alerts']:
                lines.append("## 🚨 健康警报")
                for alert in health['alerts']:
                    lines.append(f"⚠️ {alert}")
                lines.append("")
            
            lines.append("---")
            lines.append(f"*由DNA四维分析引擎 v2.1生成*")
            lines.append(f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
            
            return "\n".join(lines)
        
        def save_health_report(self, filepath: str = None) -> str:
            """保存健康报告"""
            if filepath is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = f"health_report_{self.account_id}_{timestamp}.md"
            
            report = self.get_health_report(format="markdown")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report)
            
            return filepath
    
    return EnhancedContentDNA


# ==================== API集成补丁 ====================

def patch_dna_application_api():
    """为DNAApplication类添加健康分析API"""
    
    original_DNAApplication = None  # 这应该从原始模块导入
    
    class EnhancedDNAApplication(original_DNAApplication if original_DNAApplication else object):
        """增强的DNAApplication类"""
        
        async def analyze_account_health(self, account_id: str) -> Dict[str, Any]:
            """分析账号健康度"""
            dna = await self.dna_db.get_latest_dna(account_id)
            if not dna:
                return {"error": f"账号 {account_id} 未找到DNA"}
            
            # 确保DNA对象是增强版本
            if not hasattr(dna, 'perform_4d_analysis'):
                # 动态增强
                EnhancedDNA = apply_dna_4d_patch_to_dna_class()
                dna = EnhancedDNA(**dna.dict())
            
            health_analysis = dna.perform_4d_analysis()
            
            return {
                "account_id": account_id,
                "dna_fingerprint": dna.get_dna_fingerprint(),
                "health_analysis": health_analysis,
                "report_url": f"/api/v1/health/report/{account_id}"
            }
        
        async def generate_health_report(self, account_id: str, format: str = "markdown") -> Any:
            """生成健康报告"""
            dna = await self.dna_db.get_latest_dna(account_id)
            if not dna:
                return {"error": f"账号 {account_id} 未找到DNA"}
            
            # 确保DNA对象是增强版本
            if not hasattr(dna, 'get_health_report'):
                EnhancedDNA = apply_dna_4d_patch_to_dna_class()
                dna = EnhancedDNA(**dna.dict())
            
            return dna.get_health_report(format=format)
        
        async def batch_health_check(self, account_ids: List[str]) -> Dict[str, Any]:
            """批量健康检查"""
            results = {}
            
            for account_id in account_ids:
                try:
                    health = await self.analyze_account_health(account_id)
                    results[account_id] = health
                except Exception as e:
                    results[account_id] = {"error": str(e)}
            
            # 生成汇总报告
            summary = self._generate_health_summary(results)
            
            return {
                "batch_id": f"batch_{int(datetime.now().timestamp())}",
                "timestamp": datetime.now().isoformat(),
                "total_accounts": len(account_ids),
                "successful": sum(1 for r in results.values() if "error" not in r),
                "failed": sum(1 for r in results.values() if "error" in r),
                "results": results,
                "summary": summary
            }
        
        def _generate_health_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
            """生成健康汇总"""
            successful_results = {k: v for k, v in results.items() if "error" not in v}
            
            if not successful_results:
                return {"error": "没有成功的健康分析"}
            
            health_scores = []
            alerts_count = 0
            recommendations_count = 0
            
            for account_data in successful_results.values():
                if "health_analysis" in account_data:
                    health = account_data["health_analysis"]["health_metrics"]
                    health_scores.append(health["overall_health_index"])
                    alerts_count += len(health.get("alerts", []))
                    
                    recs = account_data["health_analysis"].get("recommendations", [])
                    recommendations_count += len(recs)
            
            avg_health = sum(health_scores) / len(health_scores) if health_scores else 0
            
            return {
                "average_health_score": round(avg_health, 2),
                "health_distribution": {
                    "excellent": sum(1 for s in health_scores if s >= 80),
                    "good": sum(1 for s in health_scores if 60 <= s < 80),
                    "fair": sum(1 for s in health_scores if 40 <= s < 60),
                    "poor": sum(1 for s in health_scores if s < 40)
                },
                "total_alerts": alerts_count,
                "total_recommendations": recommendations_count,
                "highest_health": max(health_scores) if health_scores else 0,
                "lowest_health": min(health_scores) if health_scores else 0
            }
    
    return EnhancedDNAApplication


# ==================== Web API补丁 ====================

def patch_web_api():
    """为Web API添加健康分析端点"""
    
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    from urllib.parse import parse_qs, urlparse
    
    original_ContentDNAPlatform = None  # 这应该从原始模块导入
    
    class EnhancedContentDNAPlatform(original_ContentDNAPlatform if original_ContentDNAPlatform else object):
        """增强的内容DNA平台"""
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._4d_analyzer = DNA四维分析补丁()
        
        def add_health_endpoints(self, handler_class):
            """为HTTP处理器添加健康分析端点"""
            
            class HealthEnhancedHandler(handler_class):
                """增强的HTTP处理器"""
                
                def do_GET(self):
                    parsed = urlparse(self.path)
                    
                    # 健康分析端点
                    if parsed.path.startswith("/api/v1/health/"):
                        self._handle_health_endpoints(parsed)
                    else:
                        super().do_GET()
                
                def do_POST(self):
                    parsed = urlparse(self.path)
                    
                    if parsed.path == "/api/v1/health/batch":
                        self._handle_batch_health()
                    else:
                        super().do_POST()
                
                def _handle_health_endpoints(self, parsed):
                    """处理健康分析端点"""
                    path_parts = parsed.path.strip("/").split("/")
                    
                    if len(path_parts) >= 4 and path_parts[3] == "analyze":
                        # /api/v1/health/analyze?account_id=xxx
                        params = parse_qs(parsed.query)
                        account_id = params.get("account_id", [""])[0]
                        
                        if not account_id:
                            self._json_response({"error": "缺少account_id参数"}, 400)
                            return
                        
                        # 异步执行健康分析
                        import asyncio
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        try:
                            result = loop.run_until_complete(
                                self.platform.dna_app.analyze_account_health(account_id)
                            )
                            self._json_response(result)
                        except Exception as e:
                            self._json_response({"error": str(e)}, 500)
                        finally:
                            loop.close()
                    
                    elif len(path_parts) >= 4 and path_parts[3] == "report":
                        # /api/v1/health/report/{account_id}
                        if len(path_parts) >= 5:
                            account_id = path_parts[4]
                            params = parse_qs(parsed.query)
                            fmt = params.get("format", ["markdown"])[0]
                            
                            # 异步生成报告
                            import asyncio
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            
                            try:
                                result = loop.run_until_complete(
                                    self.platform.dna_app.generate_health_report(account_id, fmt)
                                )
                                
                                if fmt == "markdown":
                                    self.send_response(200)
                                    self.send_header("Content-Type", "text/markdown; charset=utf-8")
                                    self.send_header("Content-Disposition", 
                                                   f'attachment; filename="health_report_{account_id}.md"')
                                    self.end_headers()
                                    self.wfile.write(result.encode("utf-8"))
                                else:
                                    self._json_response(result)
                            except Exception as e:
                                self._json_response({"error": str(e)}, 500)
                            finally:
                                loop.close()
                    
                    else:
                        self.send_error(404)
                
                def _handle_batch_health(self):
                    """处理批量健康分析"""
                    try:
                        length = int(self.headers.get("Content-Length", 0))
                        body = self.rfile.read(length).decode("utf-8")
                        data = json.loads(body)
                        account_ids = data.get("account_ids", [])
                    except Exception as e:
                        self._json_response({"error": f"JSON解析错误: {e}"}, 400)
                        return
                    
                    if not account_ids:
                        self._json_response({"error": "缺少account_ids参数"}, 400)
                        return
                    
                    # 异步执行批量分析
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        result = loop.run_until_complete(
                            self.platform.dna_app.batch_health_check(account_ids)
                        )
                        self._json_response(result)
                    except Exception as e:
                        self._json_response({"error": str(e)}, 500)
                    finally:
                        loop.close()
                
                def _json_response(self, data, status_code=200):
                    """返回JSON响应"""
                    self.send_response(status_code)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
            
            return HealthEnhancedHandler
    
    return EnhancedContentDNAPlatform


# ==================== 主补丁应用 ====================

def apply_all_patches():
    """应用所有补丁"""
    
    print("=" * 60)
    print("🧬 DNA四维分析补丁 v2.1")
    print("📊 为内容DNA平台添加健康度分析功能")
    print("=" * 60)
    
    # 1. 应用核心补丁
    EnhancedContentDNA = apply_dna_4d_patch_to_dna_class()
    EnhancedDNAApplication = patch_dna_application_api()
    EnhancedContentDNAPlatform = patch_web_api()
    
    # 2. 创建配置检查
    print("🔍 检查配置文件...")
    analyzer = DNA四维分析补丁()
    print(f"✅ 加载配置成功，包含 {len(analyzer.config.get('维度得分规则', {}))} 个系统类型")
    
    # 3. 显示使用说明
    print("\n📋 补丁功能说明:")
    print("1. 内容DNA健康度分析")
    print("2. 四维平衡度评估")
    print("3. 自动Markdown报告生成")
    print("4. Web API端点扩展")
    print("5. 批量健康检查")
    
    print("\n🚀 使用方法:")
    print("1. 导入补丁: from dna_4d_patch import apply_all_patches")
    print("2. 应用补丁: EnhancedDNA = apply_all_patches()")
    print("3. 使用增强功能: dna.perform_4d_analysis()")
    
    return {
        "EnhancedContentDNA": EnhancedContentDNA,
        "EnhancedDNAApplication": EnhancedDNAApplication,
        "EnhancedContentDNAPlatform": EnhancedContentDNAPlatform,
        "DNA四维分析补丁": DNA四维分析补丁
    }


# ==================== 演示示例 ====================

async def demo_usage():
    """演示补丁使用方法"""
    
    # 应用补丁
    patches = apply_all_patches()
    
    # 创建示例DNA
    dna_data = {
        "account_id": "shein_official",
        "dna_version": "1.0",
        "style_genes": [
            {"id": "style_1", "gene_type": "style", "value": "时尚潮流", "weight": 0.8, "confidence": 0.9},
            {"id": "style_2", "gene_type": "style", "value": "快速时尚", "weight": 0.7, "confidence": 0.8}
        ],
        "topic_genes": [
            {"id": "topic_1", "gene_type": "topic", "value": "女装", "weight": 0.9, "confidence": 0.95},
            {"id": "topic_2", "gene_type": "topic", "value": "配饰", "weight": 0.6, "confidence": 0.7}
        ],
        "format_genes": [
            {"id": "format_1", "gene_type": "format", "value": "短视频", "weight": 0.85, "confidence": 0.9},
            {"id": "format_2", "gene_type": "format", "value": "直播", "weight": 0.5, "confidence": 0.6}
        ],
        "emotion_genes": [
            {"id": "emotion_1", "gene_type": "emotion", "value": "喜悦", "weight": 0.7, "confidence": 0.8},
            {"id": "emotion_2", "gene_type": "emotion", "value": "期待", "weight": 0.6, "confidence": 0.7}
        ],
        "performance_traits": {
            "avg_views": 1000000,
            "avg_engagement_rate": 0.12,
            "cv_views": 0.3,
            "growth_rate": 0.15
        }
    }
    
    # 创建增强的DNA对象
    from pydantic import BaseModel
    from typing import List, Dict, Any, Optional
    
    class ContentGene(BaseModel):
        id: str
        gene_type: str
        value: str
        weight: float
        confidence: float
    
    class ContentDNA(BaseModel):
        account_id: str
        dna_version: str
        style_genes: List[ContentGene]
        topic_genes: List[ContentGene]
        format_genes: List[ContentGene]
        emotion_genes: List[ContentGene]
        performance_traits: Dict[str, Any]
        
        def get_dna_fingerprint(self) -> str:
            import hashlib
            dna_str = f"{self.account_id}:{self.dna_version}"
            return hashlib.md5(dna_str.encode()).hexdigest()[:16]
        
        def dict(self):
            return {
                "account_id": self.account_id,
                "dna_version": self.dna_version,
                "style_genes": [g.dict() for g in self.style_genes],
                "topic_genes": [g.dict() for g in self.topic_genes],
                "format_genes": [g.dict() for g in self.format_genes],
                "emotion_genes": [g.dict() for g in self.emotion_genes],
                "performance_traits": self.performance_traits
            }
    
    # 创建原始DNA
    dna = ContentDNA(**dna_data)
    
    # 创建增强DNA
    EnhancedDNA = patches["EnhancedContentDNA"]
    
    # 这里需要将EnhancedDNA设为ContentDNA的子类
    class PatchedContentDNA(EnhancedDNA, ContentDNA):
        pass
    
    enhanced_dna = PatchedContentDNA(**dna_data)
    
    # 执行四维分析
    print("\n🧪 执行四维分析...")
    result = enhanced_dna.perform_4d_analysis()
    
    print(f"✅ 分析完成，健康指数: {result['health_metrics']['overall_health_index']}")
    print(f"📈 基因强度: {result['health_metrics']['scores']['gene_strength']:.1f}")
    
    # 生成报告
    print("\n📄 生成健康报告...")
    report = enhanced_dna.get_health_report(format="markdown")
    
    # 保存报告
    report_path = enhanced_dna.save_health_report()
    print(f"✅ 报告已保存: {report_path}")
    
    return enhanced_dna, result


if __name__ == "__main__":
    import asyncio
    
    print("🧬 DNA四维分析补丁演示")
    print("=" * 50)
    
    # 运行演示
    asyncio.run(demo_usage())
    
    print("\n✅ 补丁演示完成！")
    print("\n📋 集成说明:")
    print("1. 将本文件保存为 dna_4d_patch.py")
    print("2. 在主程序中导入: from dna_4d_patch import apply_all_patches")
    print("3. 应用补丁: EnhancedDNA = apply_all_patches()['EnhancedContentDNA']")
    print("4. 使用增强功能: dna.perform_4d_analysis()")
