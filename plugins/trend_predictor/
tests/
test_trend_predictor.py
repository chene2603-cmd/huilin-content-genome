import asyncio
from plugins.trend_predictor import TrendPredictorAnalyzer

def test_predict_normal(sample_dna):
    analyzer = TrendPredictorAnalyzer()
    result = asyncio.run(analyzer.analyze(sample_dna))
    assert "trend_score" in result
    assert isinstance(result["warning"], bool)