import asyncio
from plugins.four_dimension import FourDimensionAnalyzer

def test_four_dimension(sample_dna):
    # 添加测试用基因
    from core.genome import GeneFeature
    sample_dna.add_gene(GeneFeature(name="market_fit", value=0.9))
    sample_dna.add_gene(GeneFeature(name="emotion", value=0.8))
    analyzer = FourDimensionAnalyzer()
    result = asyncio.run(analyzer.analyze(sample_dna))
    assert "overall_health" in result