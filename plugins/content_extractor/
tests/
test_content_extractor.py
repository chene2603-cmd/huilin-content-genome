import asyncio
from plugins.content_extractor import ContentExtractorAnalyzer

def test_extract(sample_dna):
    sample_dna.metadata["text"] = "这个视频很搞笑，让人激动"
    analyzer = ContentExtractorAnalyzer()
    result = asyncio.run(analyzer.analyze(sample_dna))
    assert "extracted_features" in result
    assert result["extracted_features"]["emotion"] > 0