"""核心基因模型 - 可进化、可对比、可版本化"""
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib


class ContentGene(BaseModel):
    id: str
    gene_type: str  # style, topic, format, emotion
    value: str
    weight: float = 0.0
    confidence: float = 1.0
    source: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    evolution_history: List[Dict[str, Any]] = []  # 进化历史

    def mutate(self, weight_delta: float, reason: str = "") -> "ContentGene":
        """基因变异：产生新基因"""
        new_gene = self.copy()
        new_gene.weight = max(0.0, min(1.0, self.weight + weight_delta))
        new_gene.evolution_history.append({
            "timestamp": datetime.now().isoformat(),
            "previous_weight": self.weight,
            "new_weight": new_gene.weight,
            "reason": reason
        })
        return new_gene


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
    parent_dna_fingerprint: Optional[str] = None  # 父DNA指纹

    def get_fingerprint(self) -> str:
        """生成DNA唯一指纹"""
        raw = f"{self.account_id}:{self.dna_version}"
        for genes in [self.style_genes, self.topic_genes, 
                      self.format_genes, self.emotion_genes]:
            for g in sorted(genes, key=lambda x: x.id):
                raw += f"{g.gene_type}:{g.value}:{g.weight:.2f}:"
        return hashlib.md5(raw.encode()).hexdigest()[:16]

    def similarity_to(self, other: "ContentDNA") -> float:
        """计算与另一个DNA的相似度（余弦相似度）"""
        from numpy import dot, array
        from numpy.linalg import norm
        
        def get_vector(dna):
            vec = []
            for genes in [dna.style_genes, dna.topic_genes, 
                          dna.format_genes, dna.emotion_genes]:
                vec.extend([g.weight * g.confidence for g in genes])
            return array(vec)
        
        v1, v2 = get_vector(self), get_vector(other)
        return dot(v1, v2) / (norm(v1) * norm(v2)) if norm(v1) and norm(v2) else 0.0

    def evolve(self, environment_data: Dict[str, Any]) -> "ContentDNA":
        """根据环境数据进化DNA"""
        evolved = self.copy()
        evolved.dna_version = f"{self.dna_version}.evolved"
        evolved.parent_dna_fingerprint = self.get_fingerprint()
        
        # 根据环境调整基因权重
        for gene_type in ["style", "topic", "format", "emotion"]:
            genes = getattr(evolved, f"{gene_type}_genes")
            evolved_genes = []
            for gene in genes:
                # 环境适应性调整
                adaptation_factor = environment_data.get(f"{gene_type}_trend", 0.0)
                evolved_genes.append(gene.mutate(adaptation_factor * 0.1, "环境适应"))
            setattr(evolved, f"{gene_type}_genes", evolved_genes)
        
        return evolved