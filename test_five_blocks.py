# test_five_blocks.py
import asyncio
from datetime import datetime, timedelta
from core.genome import ContentDNA, ContentGene
from core.plugin_loader import PluginLoader

async def test():
    loader = PluginLoader()
    loader.discover()
    print("已加载插件:", list(loader.registry.keys()))
    
    # 模拟历史DNA（3周前的快照）
    history_dna = ContentDNA(
        account_id="test_trend",
        extraction_date=datetime.now() - timedelta(days=21),
        style_genes=[ContentGene(id="s1", gene_type="style", value="幽默", weight=0.5, confidence=0.7)],
        topic_genes=[ContentGene(id="t1", gene_type="topic", value="科技", weight=0.6, confidence=0.75)],
        format_genes=[ContentGene(id="f1", gene_type="format", value="图文", weight=0.8, confidence=0.8)],
        emotion_genes=[ContentGene(id="e1", gene_type="emotion", value="信任", weight=0.5, confidence=0.7)],
        sample_size=80
    )
    
    # 当前DNA（发生了明显进化）
    current_dna = ContentDNA(
        account_id="test_trend",
        extraction_date=datetime.now(),
        style_genes=[
            ContentGene(id="s1", gene_type="style", value="幽默", weight=0.8, confidence=0.9),
            ContentGene(id="s2", gene_type="style", value="情感共鸣", weight=0.6, confidence=0.8)
        ],
        topic_genes=[
            ContentGene(id="t1", gene_type="topic", value="科技", weight=0.7, confidence=0.85),
            ContentGene(id="t2", gene_type="topic", value="生活记录", weight=0.5, confidence=0.75)
        ],
        format_genes=[ContentGene(id="f1", gene_type="format", value="短视频", weight=0.9, confidence=0.95)],
        emotion_genes=[
            ContentGene(id="e1", gene_type="emotion", value="喜悦", weight=0.7, confidence=0.9),
            ContentGene(id="e2", gene_type="emotion", value="惊讶", weight=0.5, confidence=0.8)
        ],
        sample_size=200,
        confidence_score=0.95
    )
    
    tracker = loader.get_plugin("TrendTracker")
    result = await tracker.analyze(current_dna, history=[history_dna])
    print(tracker.report(result))

asyncio.run(test())