#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PERSONALIZED CONTENT INTELLIGENCE PLATFORM (PCI)
DNA Core System v1.0
Author: Yuanbao (Tencent)
Date: 2026-05-06
Description: 内容智能平台的基因代码架构
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from datetime import datetime, timedelta
import asyncio
from functools import lru_cache
import json
from pydantic import BaseModel, Field, validator
import numpy as np
from scipy import stats
from transformers import AutoModel, AutoTokenizer
from dataclasses_json import dataclass_json


# ==================== DNA 核心定义 ====================

class ContentGene(BaseModel):
    """内容基因单元 - 最小可复用的内容特征"""
    id: str = Field(..., description="基因ID")
    gene_type: str = Field(..., description="基因类型: style/topic/format/emotion")
    value: str = Field(..., description="基因值")
    weight: float = Field(0.0, ge=0.0, le=1.0, description="基因权重")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="置信度")
    source: str = Field("", description="基因来源")
    created_at: datetime = Field(default_factory=datetime.now)
    last_used: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class ContentDNA(BaseModel):
    """账号内容DNA - 完整的基因图谱"""
    account_id: str = Field(..., description="账号ID")
    dna_version: str = Field("1.0", description="DNA版本")
    
    # 四大基因组
    style_genes: List[ContentGene] = Field(default_factory=list, description="风格基因")
    topic_genes: List[ContentGene] = Field(default_factory=list, description="话题基因")
    format_genes: List[ContentGene] = Field(default_factory=list, description="形式基因")
    emotion_genes: List[ContentGene] = Field(default_factory=list, description="情感基因")
    
    # 组合特征
    gene_combinations: Dict[str, float] = Field(default_factory=dict, description="基因组合权重")
    
    # 表现特征
    performance_traits: Dict[str, Any] = Field(default_factory=dict, description="表现特征")
    
    # 元数据
    extraction_date: datetime = Field(default_factory=datetime.now)
    confidence_score: float = Field(1.0, ge=0.0, le=1.0)
    sample_size: int = Field(0, description="用于提取的样本数量")
    
    def get_dna_fingerprint(self) -> str:
        """获取DNA指纹"""
        import hashlib
        dna_str = f"{self.account_id}:{self.dna_version}:"
        for gene_list in [self.style_genes, self.topic_genes, 
                         self.format_genes, self.emotion_genes]:
            for gene in sorted(gene_list, key=lambda x: x.id):
                dna_str += f"{gene.gene_type}:{gene.value}:{gene.weight:.2f}:"
        return hashlib.md5(dna_str.encode()).hexdigest()[:16]
    
    def similarity_to(self, other: 'ContentDNA') -> float:
        """计算与另一个DNA的相似度"""
        # 简化实现，实际应更复杂
        total_sim = 0.0
        count = 0
        
        for gene_list_self, gene_list_other in [
            (self.style_genes, other.style_genes),
            (self.topic_genes, other.topic_genes),
            (self.format_genes, other.format_genes),
            (self.emotion_genes, other.emotion_genes)
        ]:
            sim = self._calculate_gene_similarity(gene_list_self, gene_list_other)
            total_sim += sim
            count += 1
        
        return total_sim / count if count > 0 else 0.0
    
    def _calculate_gene_similarity(self, genes1: List[ContentGene], 
                                  genes2: List[ContentGene]) -> float:
        """计算基因列表相似度"""
        if not genes1 and not genes2:
            return 1.0
        
        # 创建基因值到权重的映射
        gene_map1 = {f"{g.gene_type}:{g.value}": g.weight for g in genes1}
        gene_map2 = {f"{g.gene_type}:{g.value}": g.weight for g in genes2}
        
        all_genes = set(gene_map1.keys()) | set(gene_map2.keys())
        if not all_genes:
            return 0.0
        
        # 计算余弦相似度
        vec1 = np.array([gene_map1.get(g, 0.0) for g in all_genes])
        vec2 = np.array([gene_map2.get(g, 0.0) for g in all_genes])
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)


# ==================== DNA 提取引擎 ====================

@dataclass_json
@dataclass
class DNASample:
    """DNA提取样本"""
    content_id: str
    content_type: str  # video/article/image
    platform: str
    metrics: Dict[str, float]  # views/likes/comments等
    features: Dict[str, Any]  # 提取的特征
    text_content: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    

class DNAExtractor:
    """DNA提取引擎"""
    
    def __init__(self, model_name: str = "bert-base-chinese"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self._initialized = False
        
    async def initialize(self):
        """初始化模型"""
        if not self._initialized:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self._initialized = True
    
    async def extract_dna_from_samples(self, samples: List[DNASample], 
                                      account_id: str) -> ContentDNA:
        """从样本中提取DNA"""
        if not samples:
            raise ValueError("No samples provided")
        
        await self.initialize()
        
        # 提取各类基因
        style_genes = await self._extract_style_genes(samples)
        topic_genes = await self._extract_topic_genes(samples)
        format_genes = await self._extract_format_genes(samples)
        emotion_genes = await self._extract_emotion_genes(samples)
        
        # 计算组合特征
        gene_combinations = await self._calculate_gene_combinations(
            style_genes, topic_genes, format_genes, emotion_genes, samples
        )
        
        # 计算表现特征
        performance_traits = await self._calculate_performance_traits(samples)
        
        return ContentDNA(
            account_id=account_id,
            style_genes=style_genes,
            topic_genes=topic_genes,
            format_genes=format_genes,
            emotion_genes=emotion_genes,
            gene_combinations=gene_combinations,
            performance_traits=performance_traits,
            sample_size=len(samples),
            confidence_score=self._calculate_confidence(samples)
        )
    
    async def _extract_style_genes(self, samples: List[DNASample]) -> List[ContentGene]:
        """提取风格基因"""
        # 简化的风格提取逻辑
        styles = {
            "幽默搞笑": 0.0,
            "专业教程": 0.0,
            "情感共鸣": 0.0,
            "热点追踪": 0.0,
            "生活记录": 0.0,
            "创意艺术": 0.0
        }
        
        # 这里应该是实际的AI模型分析
        for sample in samples:
            if "幽默" in sample.text_content or "搞笑" in sample.text_content:
                styles["幽默搞笑"] += sample.metrics.get("engagement_rate", 1.0)
            if "教程" in sample.text_content or "教学" in sample.text_content:
                styles["专业教程"] += sample.metrics.get("engagement_rate", 1.0)
        
        # 归一化
        total = sum(styles.values())
        if total > 0:
            styles = {k: v/total for k, v in styles.items()}
        
        genes = []
        for style_name, weight in styles.items():
            if weight > 0.1:  # 只保留显著的风格
                genes.append(ContentGene(
                    id=f"style_{style_name}",
                    gene_type="style",
                    value=style_name,
                    weight=weight,
                    confidence=min(weight * 2, 1.0)
                ))
        
        return sorted(genes, key=lambda x: x.weight, reverse=True)[:5]  # 取前5
    
    async def _extract_topic_genes(self, samples: List[DNASample]) -> List[ContentGene]:
        """提取话题基因"""
        # 简化的关键词提取
        topics = {}
        
        for sample in samples:
            # 这里应该是实际的主题模型
            keywords = self._extract_keywords(sample.text_content or "")
            for keyword in keywords:
                if keyword in topics:
                    topics[keyword] += sample.metrics.get("engagement_rate", 1.0)
                else:
                    topics[keyword] = sample.metrics.get("engagement_rate", 1.0)
        
        # 归一化
        total = sum(topics.values()) if topics else 1
        topics = {k: v/total for k, v in topics.items()}
        
        genes = []
        for topic, weight in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]:
            genes.append(ContentGene(
                id=f"topic_{topic}",
                gene_type="topic",
                value=topic,
                weight=weight,
                confidence=min(weight * 3, 1.0)
            ))
        
        return genes
    
    async def _extract_format_genes(self, samples: List[DNASample]) -> List[ContentGene]:
        """提取形式基因"""
        formats = {}
        
        for sample in samples:
            format_type = sample.features.get("format", "unknown")
            if format_type in formats:
                formats[format_type] += sample.metrics.get("engagement_rate", 1.0)
            else:
                formats[format_type] = sample.metrics.get("engagement_rate", 1.0)
        
        # 归一化
        total = sum(formats.values()) if formats else 1
        formats = {k: v/total for k, v in formats.items()}
        
        genes = []
        for format_type, weight in sorted(formats.items(), key=lambda x: x[1], reverse=True)[:5]:
            genes.append(ContentGene(
                id=f"format_{format_type}",
                gene_type="format",
                value=format_type,
                weight=weight,
                confidence=min(weight * 2, 1.0)
            ))
        
        return genes
    
    async def _extract_emotion_genes(self, samples: List[DNASample]) -> List[ContentGene]:
        """提取情感基因"""
        emotions = {
            "喜悦": 0.0,
            "惊讶": 0.0,
            "期待": 0.0,
            "信任": 0.0,
            "恐惧": 0.0,
            "愤怒": 0.0,
            "悲伤": 0.0
        }
        
        for sample in samples:
            # 这里应该是情感分析模型
            if sample.text_content:
                for emotion in emotions.keys():
                    if emotion in sample.text_content:
                        emotions[emotion] += sample.metrics.get("engagement_rate", 1.0)
        
        # 归一化
        total = sum(emotions.values())
        if total > 0:
            emotions = {k: v/total for k, v in emotions.items()}
        
        genes = []
        for emotion, weight in emotions.items():
            if weight > 0.05:
                genes.append(ContentGene(
                    id=f"emotion_{emotion}",
                    gene_type="emotion",
                    value=emotion,
                    weight=weight,
                    confidence=min(weight * 4, 1.0)
                ))
        
        return sorted(genes, key=lambda x: x.weight, reverse=True)
    
    async def _calculate_gene_combinations(self, 
                                          style_genes: List[ContentGene],
                                          topic_genes: List[ContentGene],
                                          format_genes: List[ContentGene],
                                          emotion_genes: List[ContentGene],
                                          samples: List[DNASample]) -> Dict[str, float]:
        """计算基因组合权重"""
        combinations = {}
        
        # 简化的组合分析
        for sample in samples:
            # 这里应该是复杂的组合分析逻辑
            pass
        
        return combinations
    
    async def _calculate_performance_traits(self, samples: List[DNASample]) -> Dict[str, Any]:
        """计算表现特征"""
        if not samples:
            return {}
        
        metrics = {}
        
        # 计算各种统计指标
        views = [s.metrics.get("views", 0) for s in samples]
        likes = [s.metrics.get("likes", 0) for s in samples]
        comments = [s.metrics.get("comments", 0) for s in samples]
        shares = [s.metrics.get("shares", 0) for s in samples]
        
        metrics["avg_views"] = np.mean(views) if views else 0
        metrics["avg_engagement_rate"] = np.mean([
            (s.metrics.get("likes", 0) + s.metrics.get("comments", 0)) / 
            max(s.metrics.get("views", 1), 1) for s in samples
        ])
        
        # 计算变异系数
        metrics["cv_views"] = np.std(views) / np.mean(views) if np.mean(views) > 0 else 0
        
        # 计算增长趋势
        if len(samples) > 1:
            time_series = sorted([(s.metadata.get("created_at", datetime.now()), 
                                  s.metrics.get("views", 0)) for s in samples], 
                                key=lambda x: x[0])
            views_ts = [v for _, v in time_series]
            metrics["growth_rate"] = self._calculate_growth_rate(views_ts)
        
        return metrics
    
    def _calculate_confidence(self, samples: List[DNASample]) -> float:
        """计算置信度"""
        if not samples:
            return 0.0
        
        # 基于样本数量和质量
        n = len(samples)
        quality_scores = []
        
        for sample in samples:
            # 样本质量评分
            quality = 0.0
            if sample.metrics.get("views", 0) > 1000:
                quality += 0.3
            if sample.metrics.get("engagement_rate", 0) > 0.01:
                quality += 0.3
            if sample.text_content and len(sample.text_content) > 10:
                quality += 0.4
            quality_scores.append(quality)
        
        avg_quality = np.mean(quality_scores) if quality_scores else 0.0
        n_confidence = min(n / 50, 1.0)  # 50个样本达到最大置信度
        
        return 0.3 * n_confidence + 0.7 * avg_quality
    
    def _extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """提取关键词（简化版）"""
        # 这里应该是真正的关键词提取算法
        if not text:
            return []
        
        # 简单的分词和统计
        words = text.split()
        from collections import Counter
        word_counts = Counter(words)
        
        # 过滤停用词
        stop_words = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"}
        keywords = [(word, count) for word, count in word_counts.items() 
                   if word not in stop_words and len(word) > 1]
        
        return [word for word, _ in sorted(keywords, key=lambda x: x[1], reverse=True)[:top_n]]
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """计算增长率"""
        if len(values) < 2:
            return 0.0
        
        try:
            x = np.arange(len(values))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
            return slope / np.mean(values) if np.mean(values) > 0 else 0.0
        except:
            return 0.0


# ==================== DNA 数据库 ====================

class DNADatabase:
    """DNA数据库管理"""
    
    def __init__(self, db_path: str = "content_dna.db"):
        self.db_path = db_path
        self._dna_cache = {}  # 内存缓存
        
    async def save_dna(self, dna: ContentDNA) -> bool:
        """保存DNA到数据库"""
        dna_id = f"{dna.account_id}_{dna.extraction_date.strftime('%Y%m%d_%H%M%S')}"
        
        # 序列化DNA
        dna_dict = dna.dict()
        dna_dict["dna_id"] = dna_id
        dna_dict["dna_fingerprint"] = dna.get_dna_fingerprint()
        
        # 这里应该是实际的数据库操作
        self._dna_cache[dna_id] = dna_dict
        
        # 更新账号的最新DNA
        self._dna_cache[f"latest_{dna.account_id}"] = dna_dict
        
        return True
    
    async def load_dna(self, dna_id: str) -> Optional[ContentDNA]:
        """从数据库加载DNA"""
        if dna_id in self._dna_cache:
            dna_dict = self._dna_cache[dna_id]
            return ContentDNA(**dna_dict)
        return None
    
    async def get_latest_dna(self, account_id: str) -> Optional[ContentDNA]:
        """获取账号的最新DNA"""
        latest_key = f"latest_{account_id}"
        if latest_key in self._dna_cache:
            dna_dict = self._dna_cache[latest_key]
            return ContentDNA(**dna_dict)
        return None
    
    async def find_similar_dna(self, dna: ContentDNA, 
                             threshold: float = 0.7) -> List[Tuple[ContentDNA, float]]:
        """查找相似的DNA"""
        similar = []
        
        for dna_id, stored_dna_dict in self._dna_cache.items():
            if not dna_id.startswith("latest_"):
                stored_dna = ContentDNA(**stored_dna_dict)
                if stored_dna.account_id != dna.account_id:  # 排除自己
                    similarity = dna.similarity_to(stored_dna)
                    if similarity >= threshold:
                        similar.append((stored_dna, similarity))
        
        # 按相似度排序
        similar.sort(key=lambda x: x[1], reverse=True)
        return similar[:10]  # 返回前10个最相似的


# ==================== DNA 进化引擎 ====================

class DNAEvolution:
    """DNA进化引擎"""
    
    def __init__(self, mutation_rate: float = 0.1):
        self.mutation_rate = mutation_rate
        
    async def evolve_dna(self, base_dna: ContentDNA, 
                        environment_data: Dict[str, Any]) -> ContentDNA:
        """进化DNA"""
        evolved_genes = {}
        
        # 1. 选择优势基因
        selected_genes = await self._select_advantageous_genes(base_dna, environment_data)
        
        # 2. 基因变异
        mutated_genes = await self._mutate_genes(selected_genes, environment_data)
        
        # 3. 基因重组
        recombined_genes = await self._recombine_genes(mutated_genes, environment_data)
        
        # 创建新的DNA
        new_dna = ContentDNA(
            account_id=base_dna.account_id + "_evolved",
            dna_version=f"{base_dna.dna_version}.evolved",
            style_genes=recombined_genes.get("style", base_dna.style_genes),
            topic_genes=recombined_genes.get("topic", base_dna.topic_genes),
            format_genes=recombined_genes.get("format", base_dna.format_genes),
            emotion_genes=recombined_genes.get("emotion", base_dna.emotion_genes),
            gene_combinations=base_dna.gene_combinations.copy(),
            performance_traits=base_dna.performance_traits.copy(),
            sample_size=base_dna.sample_size,
            confidence_score=base_dna.confidence_score * 0.9  # 进化后置信度稍微降低
        )
        
        return new_dna
    
    async def _select_advantageous_genes(self, dna: ContentDNA, 
                                       environment: Dict[str, Any]) -> Dict[str, List[ContentGene]]:
        """选择优势基因"""
        selected = {}
        
        # 基于环境数据选择优势基因
        platform_trends = environment.get("platform_trends", {})
        competitor_analysis = environment.get("competitor_analysis", {})
        
        for gene_type in ["style", "topic", "format", "emotion"]:
            genes = getattr(dna, f"{gene_type}_genes")
            selected_genes = []
            
            for gene in genes:
                # 计算基因在当前环境中的适应性得分
                adaptability_score = self._calculate_gene_adaptability(gene, environment)
                
                if adaptability_score > 0.5:  # 适应性阈值
                    # 增强优势基因
                    enhanced_gene = ContentGene(
                        id=gene.id + "_enhanced",
                        gene_type=gene.gene_type,
                        value=gene.value,
                        weight=gene.weight * 1.2,  # 增强20%
                        confidence=gene.confidence,
                        source=f"evolved_from_{gene.id}"
                    )
                    selected_genes.append(enhanced_gene)
                else:
                    # 弱化劣势基因
                    weakened_gene = ContentGene(
                        id=gene.id + "_weakened",
                        gene_type=gene.gene_type,
                        value=gene.value,
                        weight=gene.weight * 0.8,  # 减弱20%
                        confidence=gene.confidence * 0.9,
                        source=f"evolved_from_{gene.id}"
                    )
                    selected_genes.append(weakened_gene)
            
            selected[gene_type] = selected_genes
        
        return selected
    
    async def _mutate_genes(self, genes: Dict[str, List[ContentGene]],
                          environment: Dict[str, Any]) -> Dict[str, List[ContentGene]]:
        """基因变异"""
        mutated = {}
        
        for gene_type, gene_list in genes.items():
            mutated_genes = []
            
            for gene in gene_list:
                # 判断是否发生变异
                if np.random.random() < self.mutation_rate:
                    # 发生变异
                    mutated_gene = self._apply_mutation(gene, environment)
                    mutated_genes.append(mutated_gene)
                else:
                    # 保持不变
                    mutated_genes.append(gene)
            
            # 添加新的突变基因
            if np.random.random() < self.mutation_rate * 0.5:
                new_gene = self._generate_new_gene(gene_type, environment)
                mutated_genes.append(new_gene)
            
            mutated[gene_type] = mutated_genes
        
        return mutated
    
    async def _recombine_genes(self, genes: Dict[str, List[ContentGene]],
                             environment: Dict[str, Any]) -> Dict[str, List[ContentGene]]:
        """基因重组"""
        recombined = {}
        
        for gene_type, gene_list in genes.items():
            if len(gene_list) < 2:
                recombined[gene_type] = gene_list
                continue
            
            # 随机选择两个父代基因进行重组
            parent1, parent2 = np.random.choice(gene_list, 2, replace=False)
            
            # 单点交叉重组
            child1, child2 = self._crossover_genes(parent1, parent2)
            
            # 选择更好的后代
            child1_score = self._calculate_gene_score(child1, environment)
            child2_score = self._calculate_gene_score(child2, environment)
            
            best_child = child1 if child1_score > child2_score else child2
            
            # 替换原来的基因
            other_genes = [g for g in gene_list if g.id not in [parent1.id, parent2.id]]
            recombined_genes = other_genes + [best_child]
            
            # 按权重排序
            recombined_genes.sort(key=lambda x: x.weight, reverse=True)
            recombined[gene_type] = recombined_genes[:10]  # 保持前10个
        
        return recombined
    
    def _calculate_gene_adaptability(self, gene: ContentGene, 
                                   environment: Dict[str, Any]) -> float:
        """计算基因适应性得分"""
        score = gene.weight * gene.confidence
        
        # 考虑环境因素
        trends = environment.get("trends", {})
        if gene.value in trends:
            trend_strength = trends[gene.value]
            score *= (1 + trend_strength)
        
        # 考虑竞争因素
        competitors = environment.get("competitors", {})
        if gene.value in competitors:
            competition = competitors[gene.value]
            score *= (1 - competition * 0.5)  # 竞争越激烈，得分越低
        
        return min(score, 1.0)
    
    def _calculate_gene_score(self, gene: ContentGene, environment: Dict[str, Any]) -> float:
        """计算基因得分"""
        base_score = gene.weight * gene.confidence
        adaptability = self._calculate_gene_adaptability(gene, environment)
        return base_score * adaptability
    
    def _apply_mutation(self, gene: ContentGene, environment: Dict[str, Any]) -> ContentGene:
        """应用基因变异"""
        mutation_type = np.random.choice(["weight", "value", "both"])
        
        if mutation_type == "weight":
            # 权重变异
            weight_change = np.random.normal(0, 0.2)  # 正态分布变异
            new_weight = max(0.0, min(1.0, gene.weight + weight_change))
            
            return ContentGene(
                id=f"{gene.id}_mutated",
                gene_type=gene.gene_type,
                value=gene.value,
                weight=new_weight,
                confidence=gene.confidence * 0.95,  # 变异后置信度降低
                source=f"mutated_from_{gene.id}"
            )
        
        elif mutation_type == "value":
            # 值变异（简化的语义变异）
            value_variants = {
                "幽默搞笑": ["幽默", "搞笑", "喜剧", "欢乐"],
                "专业教程": ["教学", "指南", "教程", "科普"],
                "情感共鸣": ["情感", "感人", "温暖", "治愈"],
                "热点追踪": ["热点", "热门", "趋势", "爆款"]
            }
            
            if gene.value in value_variants:
                new_value = np.random.choice(value_variants[gene.value])
            else:
                new_value = gene.value + "_variant"
            
            return ContentGene(
                id=f"{gene.id}_mutated",
                gene_type=gene.gene_type,
                value=new_value,
                weight=gene.weight * 0.8,  # 值变异权重降低
                confidence=gene.confidence * 0.8,
                source=f"mutated_from_{gene.id}"
            )
        
        else:  # both
            # 综合变异
            weight_change = np.random.normal(0, 0.3)
            new_weight = max(0.0, min(1.0, gene.weight + weight_change))
            
            return ContentGene(
                id=f"{gene.id}_mutated",
                gene_type=gene.gene_type,
                value=gene.value + "_evolved",
                weight=new_weight,
                confidence=gene.confidence * 0.7,
                source=f"mutated_from_{gene.id}"
            )
    
    def _generate_new_gene(self, gene_type: str, environment: Dict[str, Any]) -> ContentGene:
        """生成新的基因"""
        # 基于环境趋势生成新基因
        trends = environment.get("trends", {})
        
        if trends:
            # 选择当前趋势但不在现有基因中的
            available_trends = [t for t in trends.keys() 
                              if t not in environment.get("existing_genes", [])]
            if available_trends:
                new_value = np.random.choice(available_trends)
                trend_strength = trends[new_value]
            else:
                new_value = f"new_{gene_type}_{np.random.randint(1000)}"
                trend_strength = 0.5
        else:
            new_value = f"new_{gene_type}_{np.random.randint(1000)}"
            trend_strength = 0.5
        
        return ContentGene(
            id=f"{gene_type}_new_{int(datetime.now().timestamp())}",
            gene_type=gene_type,
            value=new_value,
            weight=0.3 + trend_strength * 0.4,  # 基于趋势强度
            confidence=0.3,  # 新基因置信度较低
            source="mutation_new"
        )
    
    def _crossover_genes(self, gene1: ContentGene, gene2: ContentGene) -> Tuple[ContentGene, ContentGene]:
        """基因交叉"""
        # 单点交叉
        alpha = np.random.random()  # 交叉系数
        
        # 子代1
        child1_weight = alpha * gene1.weight + (1 - alpha) * gene2.weight
        child1_confidence = (gene1.confidence + gene2.confidence) / 2
        
        child1 = ContentGene(
            id=f"child1_{gene1.id}_{gene2.id}",
            gene_type=gene1.gene_type,
            value=gene1.value if alpha > 0.5 else gene2.value,
            weight=child1_weight,
            confidence=child1_confidence,
            source=f"crossover_{gene1.id}_{gene2.id}"
        )
        
        # 子代2
        child2_weight = (1 - alpha) * gene1.weight + alpha * gene2.weight
        child2_confidence = (gene1.confidence + gene2.confidence) / 2
        
        child2 = ContentGene(
            id=f"child2_{gene1.id}_{gene2.id}",
            gene_type=gene1.gene_type,
            value=gene2.value if alpha > 0.5 else gene1.value,
            weight=child2_weight,
            confidence=child2_confidence,
            source=f"crossover_{gene1.id}_{gene2.id}"
        )
        
        return child1, child2


# ==================== DNA 应用引擎 ====================

class DNAApplication:
    """DNA应用引擎"""
    
    def __init__(self, dna_database: DNADatabase):
        self.dna_db = dna_database
        self.evolution_engine = DNAEvolution()
        
    async def analyze_account(self, account_id: str, 
                            samples: List[DNASample]) -> ContentDNA:
        """分析账号并生成DNA"""
        extractor = DNAExtractor()
        dna = await extractor.extract_dna_from_samples(samples, account_id)
        
        # 保存到数据库
        await self.dna_db.save_dna(dna)
        
        return dna
    
    async def generate_content(self, dna: ContentDNA, 
                             content_type: str = "video",
                             target_platform: str = "tiktok") -> Dict[str, Any]:
        """基于DNA生成内容"""
        
        # 1. 选择最优基因组合
        optimal_combination = await self._select_optimal_combination(dna, content_type, target_platform)
        
        # 2. 生成内容框架
        content_framework = await self._generate_framework(optimal_combination, content_type)
        
        # 3. 填充具体内容
        detailed_content = await self._fill_content_details(content_framework, dna)
        
        # 4. 优化建议
        optimization_suggestions = await self._generate_optimizations(detailed_content, target_platform)
        
        return {
            "content_framework": content_framework,
            "detailed_content": detailed_content,
            "optimization_suggestions": optimization_suggestions,
            "viral_score": await self._predict_viral_score(detailed_content, dna),
            "confidence": dna.confidence_score
        }
    
    async def evolve_content_strategy(self, account_id: str,
                                    environment_data: Dict[str, Any]) -> ContentDNA:
        """进化内容策略"""
        # 获取当前DNA
        current_dna = await self.dna_db.get_latest_dna(account_id)
        if not current_dna:
            raise ValueError(f"No DNA found for account {account_id}")
        
        # 进化DNA
        evolved_dna = await self.evolution_engine.evolve_dna(current_dna, environment_data)
        
        # 保存进化后的DNA
        evolved_dna.account_id = account_id
        await self.dna_db.save_dna(evolved_dna)
        
        return evolved_dna
    
    async def find_competitor_insights(self, account_id: str, 
                                     similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """寻找竞争者洞察"""
        current_dna = await self.dna_db.get_latest_dna(account_id)
        if not current_dna:
            return []
        
        # 查找相似DNA
        similar_dnas = await self.dna_db.find_similar_dna(current_dna, similarity_threshold)
        
        insights = []
        for competitor_dna, similarity in similar_dnas:
            insight = {
                "competitor_account": competitor_dna.account_id,
                "similarity_score": similarity,
                "strengths": [],
                "weaknesses": [],
                "opportunities": []
            }
            
            # 分析优势基因
            for gene_type in ["style", "topic", "format", "emotion"]:
                current_genes = getattr(current_dna, f"{gene_type}_genes")
                competitor_genes = getattr(competitor_dna, f"{gene_type}_genes")
                
                # 找到竞争者有而我们没有的优势基因
                for c_gene in competitor_genes[:3]:  # 只看前三
                    if c_gene.weight > 0.3:  # 显著基因
                        # 检查我们是否有类似基因
                        has_similar = False
                        for my_gene in current_genes:
                            if my_gene.value == c_gene.value or similarity > 0.8:
                                has_similar = True
                                break
                        
                        if not has_similar:
                            insight["opportunities"].append({
                                "gene_type": gene_type,
                                "gene_value": c_gene.value,
                                "gene_weight": c_gene.weight,
                                "suggestion": f"考虑增加{c_gene.value}类型的内容"
                            })
            
            insights.append(insight)
        
        return insights
    
    async def _select_optimal_combination(self, dna: ContentDNA,
                                        content_type: str,
                                        target_platform: str) -> Dict[str, Any]:
        """选择最优基因组合"""
        combination = {}
        
        # 选择每个类型的前2个基因
        for gene_type in ["style", "topic", "format", "emotion"]:
            genes = getattr(dna, f"{gene_type}_genes")
            if genes:
                # 根据平台偏好调整权重
                adjusted_genes = []
                for gene in genes[:2]:  # 取前2个
                    adjusted_weight = self._adjust_for_platform(gene, target_platform)
                    if adjusted_weight > 0.1:  # 过滤掉权重太低的
                        adjusted_gene = ContentGene(
                            id=gene.id,
                            gene_type=gene.gene_type,
                            value=gene.value,
                            weight=adjusted_weight,
                            confidence=gene.confidence,
                            source=gene.source
                        )
                        adjusted_genes.append(adjusted_gene)
                
                combination[gene_type] = adjusted_genes
        
        return combination
    
    async def _generate_framework(self, combination: Dict[str, Any],
                                content_type: str) -> Dict[str, Any]:
        """生成内容框架"""
        framework = {
            "title_structure": "",
            "content_structure": [],
            "key_elements": [],
            "duration_suggestions": {}
        }
        
        # 基于基因组合生成框架
        styles = [g.value for g in combination.get("style", [])]
        topics = [g.value for g in combination.get("topic", [])]
        formats = [g.value for g in combination.get("format", [])]
        emotions = [g.value for g in combination.get("emotion", [])]
        
        # 生成标题结构
        if "幽默搞笑" in styles:
            framework["title_structure"] = "悬念+反转+惊喜"
        elif "专业教程" in styles:
            framework["title_structure"] = "痛点+解决方案+结果"
        elif "情感共鸣" in styles:
            framework["title_structure"] = "故事+情感+启示"
        else:
            framework["title_structure"] = "话题+价值+行动号召"
        
        # 生成内容结构
        if content_type == "video":
            framework["content_structure"] = [
                {"part": "开头", "duration": "3-5s", "purpose": "吸引注意力"},
                {"part": "引入", "duration": "5-10s", "purpose": "建立期待"},
                {"part": "主体", "duration": "30-45s", "purpose": "核心内容"},
                {"part": "高潮", "duration": "5-10s", "purpose": "情绪高点"},
                {"part": "结尾", "duration": "3-5s", "purpose": "行动号召"}
            ]
        elif content_type == "article":
            framework["content_structure"] = [
                {"part": "标题", "purpose": "吸引点击"},
                {"part": "引言", "purpose": "建立共鸣"},
                {"part": "正文", "purpose": "核心信息"},
                {"part": "案例", "purpose": "增强说服"},
                {"part": "总结", "purpose": "强化记忆"},
                {"part": "行动", "purpose": "促进转化"}
            ]
        
        # 关键元素
        for gene_type, genes in combination.items():
            for gene in genes[:2]:
                framework["key_elements"].append({
                    "type": gene_type,
                    "element": gene.value,
                    "importance": gene.weight
                })
        
        return framework
    
    async def _fill_content_details(self, framework: Dict[str, Any],
                                  dna: ContentDNA) -> Dict[str, Any]:
        """填充具体内容"""
        # 这里简化实现，实际应该使用AI模型生成
        details = {
            "title_examples": [],
            "content_outline": "",
            "hashtag_suggestions": [],
            "call_to_action": []
        }
        
        # 生成标题示例
        title_structures = {
            "悬念+反转+惊喜": [
                f"我以为{dna.topic_genes[0].value}很简单，结果...",
                f"千万不要尝试{dna.topic_genes[0].value}，除非...",
                f"{dna.topic_genes[0].value}的真相，第3个让我震惊了！"
            ],
            "痛点+解决方案+结果": [
                f"还在为{dna.topic_genes[0].value}烦恼？这个方法太管用了！",
                f"{dna.topic_genes[0].value}的完整指南，新手也能学会",
                f"3步解决{dna.topic_genes[0].value}问题，简单有效"
            ]
        }
        
        structure = framework.get("title_structure", "话题+价值+行动号召")
        if structure in title_structures:
            details["title_examples"] = title_structures[structure]
        
        # 生成内容大纲
        topic = dna.topic_genes[0].value if dna.topic_genes else "内容"
        style = dna.style_genes[0].value if dna.style_genes else "分享"
        
        details["content_outline"] = f"""
1. 开头：用{dna.emotion_genes[0].value if dna.emotion_genes else '吸引人'}的方式引入{topic}
2. 主体：分享3个关于{topic}的{style}技巧
3. 案例：展示实际应用效果
4. 总结：强调关键要点
5. 互动：邀请观众分享自己的经验
"""
        
        # 话题标签建议
        details["hashtag_suggestions"] = [
            f"#{topic}",
            f"#{style}",
            f"#{dna.format_genes[0].value if dna.format_genes else '分享'}",
            "#知识分享",
            "#干货"
        ]
        
        # 行动号召
        details["call_to_action"] = [
            "关注我，获取更多干货",
            "点赞收藏，下次不迷路",
            "评论区分享你的想法"
        ]
        
        return details
    
    async def _generate_optimizations(self, content: Dict[str, Any],
                                    target_platform: str) -> List[str]:
        """生成优化建议"""
        optimizations = []
        
        platform_optimizations = {
            "tiktok": [
                "前3秒要有爆点",
                "使用热门音乐",
                "字幕要清晰醒目",
                "节奏要快，减少空镜"
            ],
            "youtube": [
                "开头要有预告",
                "时间可以稍长，但内容要充实",
                "章节标记很重要",
                "结尾要有其他视频推荐"
            ],
            "bilibili": [
                "加入弹幕互动点",
                "可以更有梗更玩梗",
                "社区文化要了解",
                "可以加入一些二次元元素"
            ],
            "xiaohongshu": [
                "图片要精美",
                "文案要有亲和力",
                "标签要精准",
                "可以加入个人体验分享"
            ]
        }
        
        optimizations.extend(platform_optimizations.get(target_platform, []))
        
        # 基于内容类型的优化
        if "video" in content.get("content_type", ""):
            optimizations.extend([
                "画面要稳定，减少抖动",
                "光线要充足",
                "声音要清晰"
            ])
        
        return optimizations
    
    async def _predict_viral_score(self, content: Dict[str, Any],
                                 dna: ContentDNA) -> float:
        """预测爆款分数"""
        score = 0.0
        
        # 基于DNA的预测
        if dna.performance_traits.get("avg_engagement_rate", 0) > 0.05:
            score += 0.3
        
        if dna.confidence_score > 0.8:
            score += 0.2
        
        # 基于内容的预测
        title_examples = content.get("title_examples", [])
        if len(title_examples) > 0:
            # 分析标题质量
            for title in title_examples:
                if "！" in title or "？" in title or "..." in title:
                    score += 0.1
                if len(title) >= 5 and len(title) <= 20:
                    score += 0.1
        
        # 基于框架的预测
        framework = content.get("content_framework", {})
        if len(framework.get("key_elements", [])) >= 3:
            score += 0.2
        
        return min(score, 1.0)
    
    def _adjust_for_platform(self, gene: ContentGene, platform: str) -> float:
        """根据平台调整基因权重"""
        platform_preferences = {
            "tiktok": {
                "style": {"幽默搞笑": 1.2, "热点追踪": 1.1, "专业教程": 0.8},
                "format": {"短视频": 1.3, "直播": 1.1, "长视频": 0.7},
                "emotion": {"喜悦": 1.2, "惊讶": 1.3, "悲伤": 0.6}
            },
            "youtube": {
                "style": {"专业教程": 1.3, "深度解析": 1.2, "幽默搞笑": 0.9},
                "format": {"长视频": 1.4, "短视频": 0.8, "直播": 1.0},
                "emotion": {"信任": 1.2, "期待": 1.1, "愤怒": 0.7}
            },
            "bilibili": {
                "style": {"二次元": 1.4, "游戏": 1.3, "知识科普": 1.1},
                "format": {"中视频": 1.3, "直播": 1.2, "短视频": 1.0},
                "emotion": {"喜悦": 1.2, "期待": 1.1, "信任": 1.0}
            },
            "xiaohongshu": {
                "style": {"生活记录": 1.3, "购物分享": 1.4, "旅游": 1.2},
                "format": {"图文": 1.3, "短视频": 1.1, "直播": 0.9},
                "emotion": {"信任": 1.3, "喜悦": 1.2, "期待": 1.1}
            }
        }
        
        prefs = platform_preferences.get(platform, {})
        gene_prefs = prefs.get(gene.gene_type, {})
        
        multiplier = gene_prefs.get(gene.value, 1.0)
        return gene.weight * multiplier


# ==================== 主应用入口 ====================

class ContentDNAPlatform:
    """内容DNA平台主类"""
    
    def __init__(self):
        self.dna_db = DNADatabase()
        self.dna_app = DNAApplication(self.dna_db)
        
    async def run_full_analysis(self, account_id: str, 
                               samples: List[DNASample]) -> Dict[str, Any]:
        """运行完整分析流程"""
        print(f"🚀 开始分析账号: {account_id}")
        print(f"📊 分析样本数: {len(samples)}")
        
        # 1. 提取DNA
        print("🧬 提取内容DNA中...")
        dna = await self.dna_app.analyze_account(account_id, samples)
        
        print(f"✅ DNA提取完成!")
        print(f"   DNA指纹: {dna.get_dna_fingerprint()}")
        print(f"   置信度: {dna.confidence_score:.2%}")
        
        # 2. 生成内容建议
        print("\n🎨 生成内容建议中...")
        content_plan = await self.dna_app.generate_content(
            dna, 
            content_type="video",
            target_platform="tiktok"
        )
        
        print(f"✅ 生成{len(content_plan['title_examples'])}个标题建议")
        print(f"   爆款预测分数: {content_plan['viral_score']:.1%}")
        
        # 3. 寻找竞争者洞察
        print("\n🔍 分析竞争者中...")
        competitor_insights = await self.dna_app.find_competitor_insights(
            account_id, 
            similarity_threshold=0.7
        )
        
        print(f"✅ 找到{len(competitor_insights)}个相似账号")
        
        # 4. 环境数据（模拟）
        environment_data = {
            "platform_trends": {
                "幽默搞笑": 0.8,
                "专业教程": 0.6,
                "情感共鸣": 0.7
            },
            "competitor_analysis": {
                "similar_accounts": [insight["competitor_account"] for insight in competitor_insights]
            }
        }
        
        # 5. 进化建议
        print("\n🔄 生成进化建议中...")
        evolved_dna = await self.dna_app.evolve_content_strategy(
            account_id,
            environment_data
        )
        
        print(f"✅ DNA进化完成!")
        print(f"   进化版本: {evolved_dna.dna_version}")
        
        return {
            "account_id": account_id,
            "dna": dna,
            "content_plan": content_plan,
            "competitor_insights": competitor_insights,
            "evolved_dna": evolved_dna,
            "analysis_time": datetime.now().isoformat()
        }
    
    async def batch_analyze_accounts(self, accounts_data: Dict[str, List[DNASample]]):
        """批量分析账号"""
        results = {}
        
        for account_id, samples in accounts_data.items():
            try:
                result = await self.run_full_analysis(account_id, samples)
                results[account_id] = result
                print(f"\n{'='*50}")
                print(f"✅ 账号 {account_id} 分析完成!")
                print(f"{'='*50}\n")
            except Exception as e:
                print(f"❌ 账号 {account_id} 分析失败: {str(e)}")
                results[account_id] = {"error": str(e)}
        
        return results


# ==================== 使用示例 ====================

async def main():
    """主函数示例"""
    # 创建平台实例
    platform = ContentDNAPlatform()
    
    # 模拟样本数据
    samples = [
        DNASample(
            content_id="video_001",
            content_type="video",
            platform="tiktok",
            metrics={
                "views": 100000,
                "likes": 10000,
                "comments": 500,
                "shares": 2000,
                "engagement_rate": 0.127
            },
            features={
                "format": "短视频",
                "duration": 45,
                "hashtags": ["时尚", "穿搭", "购物"]
            },
            text_content="这个夏天的连衣裙真的太美了！买了5件都超级喜欢，特别是第3件，绝了！",
            metadata={
                "created_at": datetime.now() - timedelta(days=7),
                "category": "时尚"
            }
        ),
        DNASample(
            content_id="video_002",
            content_type="video", 
            platform="tiktok",
            metrics={
                "views": 150000,
                "likes": 18000,
                "comments": 800,
                "shares": 3000,
                "engagement_rate": 0.145
            },
            features={
                "format": "短视频",
                "duration": 38,
                "hashtags": ["开箱", "购物分享", "好物推荐"]
            },
            text_content="开箱我最新的购物战利品，这件外套真的太值了！",
            metadata={
                "created_at": datetime.now() - timedelta(days=5),
                "category": "购物"
            }
        ),
        # 可以添加更多样本...
    ]
    
    # 运行分析
    result = await platform.run_full_analysis("shein_official", samples)
    
    # 输出结果摘要
    print("\n" + "="*60)
    print("📋 分析结果摘要")
    print("="*60)
    
    dna = result["dna"]
    print(f"\n🧬 账号DNA指纹: {dna.get_dna_fingerprint()}")
    print(f"🕐 分析时间: {result['analysis_time']}")
    
    print("\n🎯 主要基因:")
    for gene_type in ["style", "topic", "format", "emotion"]:
        genes = getattr(dna, f"{gene_type}_genes")
        if genes:
            print(f"  {gene_type.upper()}: {', '.join([f'{g.value}({g.weight:.1%})' for g in genes[:3]])}")
    
    print("\n📈 表现特征:")
    for trait, value in dna.performance_traits.items():
        if isinstance(value, float):
            print(f"  {trait}: {value:.2%}")
        else:
            print(f"  {trait}: {value}")
    
    print("\n💡 内容建议:")
    content_plan = result["content_plan"]
    print(f"  标题示例: {content_plan['title_examples'][0]}")
    print(f"  爆款预测: {content_plan['viral_score']:.1%}")
    
    print("\n🔍 竞争者洞察:")
    insights = result["competitor_insights"]
    if insights:
        for insight in insights[:2]:  # 显示前2个
            print(f"  相似账号: {insight['competitor_account']} (相似度: {insight['similarity_score']:.1%})")
            if insight['opportunities']:
                opp = insight['opportunities'][0]
                print(f"    机会点: {opp['suggestion']}")
    
    print("\n🔄 DNA进化:")
    evolved = result["evolved_dna"]
    print(f"  新DNA版本: {evolved.dna_version}")
    print(f"  进化方向: 适应最新趋势")
    
    return result


# ==================== 单元测试 ====================

class TestContentDNA:
    """单元测试"""
    
    @staticmethod
    async def test_dna_extraction():
        """测试DNA提取"""
        print("🧪 测试DNA提取...")
        
        extractor = DNAExtractor()
        samples = [
            DNASample(
                content_id="test_001",
                content_type="video",
                platform="tiktok",
                metrics={"views": 1000, "likes": 100, "engagement_rate": 0.1},
                features={"format": "短视频"},
                text_content="测试内容1"
            )
        ]
        
        dna = await extractor.extract_dna_from_samples(samples, "test_account")
        
        assert dna.account_id == "test_account"
        assert len(dna.style_genes) > 0
        assert dna.sample_size == 1
        
        print("✅ DNA提取测试通过")
        return dna
    
    @staticmethod
    async def test_dna_similarity():
        """测试DNA相似度"""
        print("🧪 测试DNA相似度...")
        
        dna1 = ContentDNA(
            account_id="account1",
            style_genes=[ContentGene(id="s1", gene_type="style", value="幽默搞笑", weight=0.8)],
            topic_genes=[ContentGene(id="t1", gene_type="topic", value="时尚", weight=0.9)],
            format_genes=[ContentGene(id="f1", gene_type="format", value="短视频", weight=0.7)],
            emotion_genes=[ContentGene(id="e1", gene_type="emotion", value="喜悦", weight=0.6)]
        )
        
        dna2 = ContentDNA(
            account_id="account2",
            style_genes=[ContentGene(id="s1", gene_type="style", value="幽默搞笑", weight=0.7)],
            topic_genes=[ContentGene(id="t1", gene_type="topic", value="时尚", weight=0.8)],
            format_genes=[ContentGene(id="f1", gene_type="format", value="短视频", weight=0.6)],
            emotion_genes=[ContentGene(id="e1", gene_type="emotion", value="喜悦", weight=0.5)]
        )
        
        similarity = dna1.similarity_to(dna2)
        assert 0 <= similarity <= 1
        
        print(f"✅ DNA相似度测试通过: {similarity:.1%}")
        return similarity
    
    @staticmethod
    async def test_content_generation():
        """测试内容生成"""
        print("🧪 测试内容生成...")
        
        dna = ContentDNA(
            account_id="test_account",
            style_genes=[ContentGene(id="s1", gene_type="style", value="专业教程", weight=0.9)],
            topic_genes=[ContentGene(id="t1", gene_type="topic", value="编程", weight=0.8)],
            format_genes=[ContentGene(id="f1", gene_type="format", value="教程", weight=0.7)],
            emotion_genes=[ContentGene(id="e1", gene_type="emotion", value="信任", weight=0.6)]
        )
        
        dna_db = DNADatabase()
        dna_app = DNAApplication(dna_db)
        
        content = await dna_app.generate_content(dna, "video", "youtube")
        
        assert "content_framework" in content
        assert "title_examples" in content.get("detailed_content", {})
        assert "viral_score" in content
        
        print("✅ 内容生成测试通过")
        return content


# ==================== 命令行接口 ====================

async def cli():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="内容DNA平台")
    parser.add_argument("command", choices=["analyze", "generate", "evolve", "test"])
    parser.add_argument("--account", help="账号ID")
    parser.add_argument("--samples", type=int, default=10, help="样本数量")
    parser.add_argument("--platform", default="tiktok", help="目标平台")
    
    args = parser.parse_args()
    
    platform = ContentDNAPlatform()
    
    if args.command == "analyze":
        if not args.account:
            print("❌ 请提供账号ID: --account <account_id>")
            return
        
        # 这里应该是从数据库或API获取实际样本
        samples = [DNASample(
            content_id=f"sample_{i}",
            content_type="video",
            platform=args.platform,
            metrics={
                "views": np.random.randint(1000, 100000),
                "likes": np.random.randint(100, 10000),
                "engagement_rate": np.random.random() * 0.2
            },
            features={"format": "短视频"},
            text_content=f"测试样本内容 {i}",
            metadata={"created_at": datetime.now() - timedelta(days=i)}
        ) for i in range(args.samples)]
        
        result = await platform.run_full_analysis(args.account, samples)
        
        # 保存结果
        import json
        with open(f"dna_result_{args.account}.json", "w", encoding="utf-8") as f:
            json.dump(result, f, default=str, ensure_ascii=False, indent=2)
        
        print(f"\n💾 结果已保存到: dna_result_{args.account}.json")
    
    elif args.command == "generate":
        if not args.account:
            print("❌ 请提供账号ID: --account <account_id>")
            return
        
        dna = await platform.dna_db.get_latest_dna(args.account)
        if not dna:
            print(f"❌ 找不到账号 {args.account} 的DNA，请先运行 analyze")
            return
        
        content = await platform.dna_app.generate_content(dna, "video", args.platform)
        
        print("\n🎨 生成的内容建议:")
        print(f"爆款分数: {content['viral_score']:.1%}")
        print("\n标题示例:")
        for i, title in enumerate(content['detailed_content']['title_examples'], 1):
            print(f"  {i}. {title}")
        
        print("\n内容大纲:")
        print(content['detailed_content']['content_outline'])
    
    elif args.command == "evolve":
        if not args.account:
            print("❌ 请提供账号ID: --account <account_id>")
            return
        
        environment_data = {
            "platform_trends": {
                "幽默搞笑": 0.8,
                "专业教程": 0.6,
                "情感共鸣": 0.7
            },
            "competitor_analysis": {
                "main_competitors": ["fashion_guru", "style_expert"]
            }
        }
        
        evolved_dna = await platform.dna_app.evolve_content_strategy(
            args.account, environment_data
        )
        
        print(f"\n🔄 DNA进化完成!")
        print(f"新DNA版本: {evolved_dna.dna_version}")
        print(f"DNA指纹: {evolved_dna.get_dna_fingerprint()}")
    
    elif args.command == "test":
        print("🧪 运行单元测试...")
        
        # 运行所有测试
        dna = await TestContentDNA.test_dna_extraction()
        similarity = await TestContentDNA.test_dna_similarity()
        content = await TestContentDNA.test_content_generation()
        
        print("\n✅ 所有测试通过!")


# ==================== 启动应用 ====================

if __name__ == "__main__":
    import asyncio
    
    # 检查命令行参数
    import sys
    if len(sys.argv) > 1:
        asyncio.run(cli())
    else:
        # 如果没有参数，运行示例
        print("🚀 启动内容DNA平台示例...")
        result = asyncio.run(main())
        
        print("\n" + "="*60)
        print("🎉 示例运行完成！")
        print("="*60)
        print("\n使用以下命令进行更多操作:")
        print("  python content_dna.py analyze --account your_account")
        print("  python content_dna.py generate --account your_account")
        print("  python content_dna.py evolve --account your_account")
        print("  python content_dna.py test")
