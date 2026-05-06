# core/dna_models.py
from pydantic import BaseModel, Field
from typing import Dict, List, Any
from datetime import datetime
import hashlib


class ContentGene(BaseModel):
    id: str
    gene_type: str          # style/topic/format/emotion
    value: str
    weight: float = 0.0
    confidence: float = 1.0
    source: str = ""
    created_at: datetime = Field(default_factory=datetime.now)


class ContentDNA(BaseModel):
    account_id: str
    dna_version: str = "1.0"
    style_genes: List[ContentGene] = []
    topic_genes: List[ContentGene] = []
    format_genes: List[ContentGene] = []
    emotion_genes: List[ContentGene] = []
    gene_combinations: Dict[str, float] = {}
    performance_traits: Dict[str, Any] = {}
    extraction_date: datetime = Field(default_factory=datetime.now)
    confidence_score: float = 1.0
    sample_size: int = 0

    def get_dna_fingerprint(self) -> str:
        raw = f"{self.account_id}:{self.dna_version}"
        for genes in [self.style_genes, self.topic_genes,
                      self.format_genes, self.emotion_genes]:
            for g in sorted(genes, key=lambda x: x.id):
                raw += f"{g.gene_type}:{g.value}:{g.weight:.2f}:"
        return hashlib.md5(raw.encode()).hexdigest()[:16]