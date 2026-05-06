# plugins/content_extractor/extractor.py
"""内容特征提取器 - 第四块积木：从文本中提取基因，构建DNA"""
from typing import Dict, Any, List
from collections import Counter
import re

from core.plugin_base import BasePlugin
from core.genome import ContentDNA, ContentGene


class ContentExtractor(BasePlugin):
    """接收原始文本列表，提取风格、话题、情感、形式基因，填充DNA"""
    
    def __init__(self, config_path: str = "plugins/content_extractor/config.json"):
        super().__init__(config_path)
        self.style_dict = self.config.get("style_keywords", {})
        self.emotion_dict = self.config.get("emotion_keywords", {})
        self.format_dict = self.config.get("format_indicators", {})
    
    async def analyze(self, dna: ContentDNA, **kwargs) -> Dict[str, Any]:
        """
        输入：dna（至少含account_id），kwargs['texts'] = ["文本1", "文本2", ...]
        输出：提取的基因列表及统计
        """
        texts: List[str] = kwargs.get("texts", [])
        if not texts:
            return {"error": "未提供文本数据"}
        
        # 合并所有文本
        full_text = " ".join(texts)
        
        # 提取各类基因
        style_genes = self._extract_category(full_text, self.style_dict, "style")
        emotion_genes = self._extract_category(full_text, self.emotion_dict, "emotion")
        format_genes = self._extract_format(full_text)
        topic_genes = self._extract_topics(texts)  # 话题基于关键词频率
        
        # 构建 DNA（直接更新传入对象或返回数据）
        dna.style_genes = style_genes
        dna.emotion_genes = emotion_genes
        dna.format_genes = format_genes
        dna.topic_genes = topic_genes
        dna.sample_size = len(texts)
        
        return {
            "account_id": dna.account_id,
            "extracted_genes": {
                "style": [g.dict() for g in style_genes],
                "emotion": [g.dict() for g in emotion_genes],
                "format": [g.dict() for g in format_genes],
                "topic": [g.dict() for g in topic_genes]
            },
            "sample_count": len(texts),
            "fingerprint": dna.get_dna_fingerprint()
        }
    
    def report(self, result: Dict[str, Any]) -> str:
        if "error" in result:
            return f"❌ 提取失败：{result['error']}"
        
        report = f"""## 🧬 内容基因提取报告

**账号**：{result['account_id']}
**分析样本数**：{result['sample_count']}
**DNA指纹**：{result['fingerprint']}

### 提取的基因
"""
        for gene_type, genes in result["extracted_genes"].items():
            report += f"\n**{gene_type}**：\n"
            for g in genes[:5]:
                report += f"- {g['value']} (权重: {g['weight']:.2f})\n"
        
        return report
    
    def _extract_category(self, text: str, keyword_map: dict, gene_type: str) -> List[ContentGene]:
        """基于关键词匹配提取类别基因"""
        genes = []
        total_score = 0
        scores = {}
        for category, keywords in keyword_map.items():
            count = sum(text.count(kw) for kw in keywords)
            if count > 0:
                scores[category] = count
                total_score += count
        
        if total_score == 0:
            return genes
        
        for category, count in scores.items():
            weight = count / total_score
            genes.append(ContentGene(
                id=f"{gene_type}_{category}",
                gene_type=gene_type,
                value=category,
                weight=round(weight, 2),
                confidence=min(1.0, count / 5)
            ))
        
        return sorted(genes, key=lambda x: x.weight, reverse=True)[:5]
    
    def _extract_format(self, text: str) -> List[ContentGene]:
        """提取形式基因"""
        genes = []
        total = 0
        scores = {}
        for fmt, indicators in self.format_dict.items():
            count = sum(text.count(ind) for ind in indicators)
            if count > 0:
                scores[fmt] = count
                total += count
        
        if total == 0:
            return [ContentGene(id="format_unknown", gene_type="format", value="未知", weight=1.0)]
        
        for fmt, cnt in scores.items():
            weight = cnt / total
            genes.append(ContentGene(
                id=f"format_{fmt}",
                gene_type="format",
                value=fmt,
                weight=round(weight, 2),
                confidence=0.8
            ))
        return sorted(genes, key=lambda x: x.weight, reverse=True)[:5]
    
    def _extract_topics(self, texts: List[str]) -> List[ContentGene]:
        """简单基于词频的话题提取（可后续替换为TF-IDF/模型）"""
        word_counts = Counter()
        for text in texts:
            # 简单分词：中文按字符对还是按词？这里用假设的短词
            words = re.findall(r'[\u4e00-\u9fff]{2,4}', text)
            word_counts.update(words)
        
        # 过滤停用词
        stopwords = {"一个", "可以", "这个", "我们", "他们", "就是", "因为", "所以", "但是", "如果"}
        topics = [(w, c) for w, c in word_counts.most_common(20) if w not in stopwords]
        
        if not topics:
            return []
        
        max_count = topics[0][1]
        genes = []
        for word, count in topics[:10]:
            weight = count / max_count
            genes.append(ContentGene(
                id=f"topic_{word}",
                gene_type="topic",
                value=word,
                weight=round(weight, 2),
                confidence=min(1.0, count / 10)
            ))
        return genes