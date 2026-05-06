# test_two_blocks.py
import asyncio
from core.genome import ContentDNA, ContentGene
from core.plugin_loader import PluginLoader

async def test():
    loader = PluginLoader()
    loader.discover()
    
    print("已加载插件:", list(loader.registry.keys()))
    
    dna = ContentDNA(
        account_id="test_viral",
        style_genes=[ContentGene(id="s1", gene_type="style", value="幽默", weight=0.8, confidence=0.9)],
        topic_genes=[ContentGene(id="t1", gene_type="topic", value="科技", weight=0.9, confidence=0.95)],
        format_genes=[ContentGene(id="f1", gene_type="format", value="短视频", weight=0.9, confidence=0.95)],
        emotion_genes=[ContentGene(id="e1", gene_type="emotion", value="惊讶", weight=0.8, confidence=0.9)],
        performance_traits={
            "growth_rate": 0.15,
            "avg_engagement_rate": 0.08,
            "cv_views": 0.3
        },
        sample_size=200
    )
    
    # 第一块积木
    four_d = loader.get_plugin("FourDimensionAnalyzer")
    result_4d = await four_d.analyze(dna)
    print(four_d.report(result_4d))
    
    # 第二块积木
    viral = loader.get_plugin("ViralPredictor")
    result_viral = await viral.analyze(dna)
    print(viral.report(result_viral))

asyncio.run(test())