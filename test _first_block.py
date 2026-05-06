# test_first_block.py
import asyncio
from core.genome import ContentDNA, ContentGene
from core.plugin_loader import PluginLoader

async def test():
    loader = PluginLoader()
    loader.discover()
    
    # 创建测试DNA
    dna = ContentDNA(
        account_id="test_user",
        style_genes=[ContentGene(id="s1", gene_type="style", value="幽默", weight=0.8, confidence=0.9)],
        topic_genes=[ContentGene(id="t1", gene_type="topic", value="科技", weight=0.9, confidence=0.95)],
        format_genes=[ContentGene(id="f1", gene_type="format", value="短视频", weight=0.7, confidence=0.8)],
        emotion_genes=[ContentGene(id="e1", gene_type="emotion", value="惊讶", weight=0.5, confidence=0.7)],
        sample_size=100
    )
    
    # 获取四维分析器
    analyzer = loader.get_plugin("FourDimensionAnalyzer")
    result = await analyzer.analyze(dna)
    print(analyzer.report(result))

asyncio.run(test())