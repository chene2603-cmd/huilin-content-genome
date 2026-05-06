# test_six_blocks.py
import asyncio
from datetime import datetime, timedelta
from core.genome import ContentDNA, ContentGene
from core.plugin_loader import PluginLoader

async def test():
    loader = PluginLoader()
    loader.discover()
    print("已加载插件:", list(loader.registry.keys()))
    
    # 创建DNA
    dna = ContentDNA(
        account_id="test_full",
        style_genes=[ContentGene(id="s1", gene_type="style", value="幽默", weight=0.8, confidence=0.9)],
        topic_genes=[
            ContentGene(id="t1", gene_type="topic", value="科技", weight=0.8, confidence=0.9),
            ContentGene(id="t2", gene_type="topic", value="生活记录", weight=0.5, confidence=0.75)
        ],
        format_genes=[ContentGene(id="f1", gene_type="format", value="短视频", weight=0.9, confidence=0.95)],
        emotion_genes=[
            ContentGene(id="e1", gene_type="emotion", value="喜悦", weight=0.7, confidence=0.9),
            ContentGene(id="e2", gene_type="emotion", value="惊讶", weight=0.5, confidence=0.8)
        ],
        performance_traits={"avg_engagement_rate": 0.07, "growth_rate": 0.10},
        sample_size=200
    )
    
    # 1. 四维健康度
    four_d = loader.get_plugin("FourDimensionAnalyzer")
    health_result = await four_d.analyze(dna)
    
    # 2. 爆款预测
    viral = loader.get_plugin("ViralPredictor")
    viral_result = await viral.analyze(dna)
    
    # 3. 趋势追踪（模拟历史）
    history = ContentDNA(
        account_id="test_full",
        extraction_date=datetime.now() - timedelta(days=14),
        style_genes=[ContentGene(id="s1", gene_type="style", value="幽默", weight=0.5, confidence=0.7)],
        topic_genes=[ContentGene(id="t1", gene_type="topic", value="科技", weight=0.6, confidence=0.75)],
        format_genes=[ContentGene(id="f1", gene_type="format", value="图文", weight=0.8, confidence=0.8)],
        emotion_genes=[ContentGene(id="e1", gene_type="emotion", value="信任", weight=0.5, confidence=0.7)],
        sample_size=100
    )
    tracker = loader.get_plugin("TrendTracker")
    trend_result = await tracker.analyze(dna, history=[history])
    
    # 4. 策略生成（综合前三块积木的结果）
    generator = loader.get_plugin("StrategyGenerator")
    strategy_result = await generator.analyze(
        dna,
        health=health_result,
        viral=viral_result,
        trend=trend_result
    )
    print(generator.report(strategy_result))

asyncio.run(test())