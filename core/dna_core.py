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
            return f"{d