# test_seven_blocks.py
import asyncio
from datetime import datetime, timedelta
from core.genome import ContentDNA, ContentGene
from core.plugin_loader import PluginLoader

async def test():
    loader = PluginLoader()
    loader.discover()
    print("已加载插件:", list(loader.registry.keys()))
    
    # 构建DNA
    dna = ContentDNA(
        account_id="demo_report",
        style_genes=[ContentGene(id="s1", gene_type="style", value="幽默", weight=0.8, confidence=0.9)],
        topic_genes=[ContentGene(id="t1", gene_type="topic", value="科技", weight=0.8, confidence=0.9)],
        format_genes=[ContentGene(id="f1", gene_type="format", value="短视频", weight=0.9, confidence=0.95)],
        emotion_genes=[
            ContentGene(id="e1", gene_type="emotion", value="喜悦", weight=0.7, confidence=0.9),
            ContentGene(id="e2", gene_type="emotion", value="惊讶", weight=0.5, confidence=0.8)
        ],
        performance_traits={"avg_engagement_rate": 0.07, "growth_rate": 0.10},
        sample_size=200
    )
    
    # 收集各积木结果
    health = await loader.get_plugin("FourDimensionAnalyzer").analyze(dna)
    viral = await loader.get_plugin("ViralPredictor").analyze(dna)
    
    history = ContentDNA(
        account_id="demo_report",
        extraction_date=datetime.now() - timedelta(days=14),
        style_genes=[ContentGene(id="s1", gene_type="style", value="幽默", weight=0.5, confidence=0.7)],
        topic_genes=[ContentGene(id="t1", gene_type="topic", value="科技", weight=0.6, confidence=0.75)],
        format_genes=[ContentGene(id="f1", gene_type="format", value="图文", weight=0.8, confidence=0.8)],
        emotion_genes=[ContentGene(id="e1", gene_type="emotion", value="信任", weight=0.5, confidence=0.7)],
        sample_size=100
    )
    trend = await loader.get_plugin("TrendTracker").analyze(dna, history=[history])
    
    strategy = await loader.get_plugin("StrategyGenerator").analyze(
        dna, health=health, viral=viral, trend=trend
    )
    
    # 生成并导出报告
    exporter = loader.get_plugin("ReportExporter")
    full_report = await exporter.analyze(
        dna,
        health=health,
        viral=viral,
        trend=trend,
        strategy=strategy
    )
    
    print(f"报告已导出至：{full_report['export_path']}")
    print(f"文件大小：{full_report['file_size']} 字节")
    print("\n" + "="*50)
    print(full_report["report_text"])

asyncio.run(test())