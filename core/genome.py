from __future__ import annotations
from typing import Dict, Any, Optional
import numpy as np
from pydantic import BaseModel, Field, validator


class GeneFeature(BaseModel):
    name: str = Field(..., description="特征名称")
    value: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(0.5, ge=0.0, le=1.0)

    class Config:
        extra = "forbid"
        validate_assignment = True


class ContentDNA(BaseModel):
    content_id: str = Field(..., regex=r"^[a-zA-Z0-9\-_]+$")
    source_platform: str
    genes: Dict[str, GeneFeature] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator("genes")
    def genes_not_empty(cls, v):
        if not v:
            raise ValueError("基因字典不能为空")
        return v

    def add_gene(self, gene: GeneFeature) -> None:
        self.genes[gene.name] = gene

    def get_gene(self, name: str) -> Optional[GeneFeature]:
        return self.genes.get(name)

    def to_vector(self) -> np.ndarray:
        return np.array([g.value for g in self.genes.values()])

    def summary(self) -> Dict[str, Any]:
        return {
            "content_id": self.content_id,
            "platform": self.source_platform,
            "gene_count": len(self.genes),
            "avg_confidence": np.mean([g.confidence for g in self.genes.values()])
        }

    class Config:
        validate_assignment = True
        frozen = False