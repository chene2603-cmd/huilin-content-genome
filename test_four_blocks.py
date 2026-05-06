# test_four_blocks.py
import asyncio
from core.genome import ContentDNA, ContentGene
from core.plugin_loader import PluginLoader

async def test():
    loader = PluginLoader()
    loader.discover()
    print("已加载插件:", list(loader.registry.keys()))
    
    # 原始内容文本
    texts = [
        "笑死我了这个猫咪太搞笑了 #短视频 #抖音 日常vlog",
        "教你30秒学会一个魔术教程，创意艺术设计",
        "重磅！刚刚曝光的新科技，没想到这么厉害",
        "感动到泪目，治愈系美食日常，温暖人心",
        "这个突发新闻让人气愤，凭什么这样对待消费者"
    ]
    
    # 创建空DNA壳子
    dna = ContentDNA(account_id="test_content")
    
    # 提取器
    extractor = loader.get_plugin("ContentExtractor")
    result = await extractor.analyze(dna, texts=texts)
    print(extractor.report(result))
    
    # 接着用其他积木分析这个DNA
    four_d = loader.get_plugin("FourDimensionAnalyzer")
    health_result = await four_d.analyze(dna)
    print(four_d.report(health_result))
    
    viral = loader.get_plugin("ViralPredictor")
    viral_result = await viral.analyze(dna)
    print(viral.report(viral_result))

asyncio.run(test())