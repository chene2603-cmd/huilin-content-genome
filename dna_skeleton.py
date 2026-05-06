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
        