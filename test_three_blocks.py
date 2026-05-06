# test_three_blocks.py
import asyncio
from core.genome import ContentDNA, ContentGene
from core.plugin_loader import PluginLoader

async def test():
    loader = PluginLoader()
    loader.discover()
    print("已加载插件:", list(loader.registry.keys()))
    
    # 我方DNA
    my_dna = ContentDNA(
        account_id="my_account",
        style_genes=[ContentGene(id="s1", gene_type="style", value="幽默", weight=0.7, confidence=0.85)],
        topic_genes=[ContentGene(id="t1", gene_type="topic", value="科技", weight=0.8, confidence=0.9)],
        format_genes=[ContentGene(id="f1", gene_type="format", value="短视频", weight=0.9, confidence=0.95)],
        emotion_genes=[ContentGene(id="e1", gene_type="emotion", value="惊讶", weight=0.6, confidence=0.8)],
        performance_traits={"avg_engagement_rate": 0.08, "growth_rate": 0.12},
        sample_size=200
    )
    
    # 竞品A
    competitor_a = ContentDNA(
        account_id="competitor_a",
        style_genes=[ContentGene(id="a1", gene_type="style", value="专业教程", weight=0.9, confidence=0.95)],
        topic_genes=[ContentGene(id="a2", gene_type="topic", value="科技", weight=0.85, confidence=0.9)],
        format_genes=[ContentGene(id="a3", gene_type="format", value="长视频", weight=0.7, confidence=0.8)],
        emotion_genes=[ContentGene(id="a4", gene_type="emotion", value="信任", weight=0.8, confidence=0.9)],
        performance_traits={"avg_engagement_rate": 0.10, "growth_rate": 0.08},
        sample_size=500
    )
    
    # 竞品B
    competitor_b = ContentDNA(
        account_id="competitor_b",
        style_genes=[ContentGene(id="b1", gene_type="style", value="情感共鸣", weight=0.75, confidence=0.85)],
        topic_genes=[ContentGene(id="b2", gene_type="topic", value="生活记录", weight=0.7, confidence=0.8)],
        format_genes=[ContentGene(id="b3", gene_type="format", value="短视频", weight=0.85, confidence=0.9)],
        emotion_genes=[ContentGene(id="b4", gene_type="emotion", value="喜悦", weight=0.75, confidence=0.85)],
        performance_traits={"avg_engagement_rate": 0.09, "growth_rate": 0.15},
        sample_size=300
    )
    
    competitors = [("竞品A", competitor_a), ("竞品B", competitor_b)]
    
    # 竞品分析
    analyzer = loader.get_plugin("CompetitorAnalyzer")
    result = await analyzer.analyze(my_dna, competitors=competitors)
    print(analyzer.report(result))

asyncio.run(test())