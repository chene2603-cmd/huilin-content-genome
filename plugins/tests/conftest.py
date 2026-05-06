import pytest
from core.genome import ContentDNA, GeneFeature


@pytest.fixture
def sample_dna():
    dna = ContentDNA(
        content_id="test-001",
        source_platform="test_platform",
        metadata={"created": "2025-01-01"}
    )
    dna.add_gene(GeneFeature(name="emotion", value=0.8, confidence=0.9))
    dna.add_gene(GeneFeature(name="style_match", value=0.4, confidence=0.6))
    return dna