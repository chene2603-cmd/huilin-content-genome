# core/genome.py
from __future__ import annotations
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator
import numpy as np


class GeneFeature(BaseModel):
    """基因特征基类，所有特征维度均继承于此"""
    name: str = Field(..., description="特征名称")
    value: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(0.5, ge=0.0, le=1.0, description="置信度")

    class Config:
        extra = "forbid"  # 防止属性被随意添加


class ContentDNA(BaseModel):
    """
    内容基因组的基础模型 —— 骨架层唯一对外暴露的基因容器。
    该接口一旦发布，必须保持向后兼容。
    """
    content_id: str = Field(..., regex=r"^[a-zA-Z0-9\-_]+$")
    source_platform: str
    genes: Dict[str, GeneFeature] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="非基因的补充信息")

    @validator("genes")
    def check_genes_not_empty(cls, v):
        if not v:
            raise ValueError("基因字典不能为空")
        return v

    def add_gene(self, gene: GeneFeature) -> None:
        """安全添加一个基因特征（非破坏性）"""
        self.genes[gene.name] = gene

    def get_gene(self, name: str) -> Optional[GeneFeature]:
        return self.genes.get(name)

    def to_vector(self) -> np.ndarray:
        """将基因值转换为有序向量，供插件计算使用"""
        return np.array([g.value for g in self.genes.values()])

    def summary(self) -> Dict[str, Any]:
        """返回不可变的摘要信息，不暴露内部实现细节"""
        return {
            "content_id": self.content_id,
            "platform": self.source_platform,
            "gene_count": len(self.genes),
            "avg_confidence": np.mean([g.confidence for g in self.genes.values()])
        }

    class Config:
        validate_assignment = True   # 修改属性时也执行校验
        frozen = False               # 允许插件追加基因，但禁止直接修改核心结构