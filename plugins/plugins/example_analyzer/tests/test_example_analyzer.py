import asyncio
from plugins.example_analyzer import ExampleAnalyzer


def test_analyze(sample_dna):
    analyzer = ExampleAnalyzer()
    result = asyncio.run(analyzer.analyze(sample_dna))
    assert "score" in result
    assert "is_hot" in result

def test_report(sample_dna):
    analyzer = ExampleAnalyzer()
    result = asyncio.run(analyzer.analyze(sample_dna))
    report = analyzer.report(result)
    assert "🔥" in report or "📉" in report