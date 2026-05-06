import pytest
from core.genome import ContentDNA, GeneFeature


class TestGeneFeature:
    def test_valid_gene(self):
        g = GeneFeature(name="x", value=0.5)
        assert g.value == 0.5

    def test_value_out_of_range(self):
        with pytest.raises(Exception):
            GeneFeature(name="x", value=1.5)

    def test_extra_field_forbidden(self):
        with pytest.raises(Exception):
            GeneFeature(name="x", value=0.5, extra_field=1)


class TestContentDNA:
    def test_add_and_get_gene(self):
        dna = ContentDNA(content_id="id1", source_platform="p")
        g = GeneFeature(name="test", value=0.7)
        dna.add_gene(g)
        assert dna.get_gene("test").value == 0.7

    def test_empty_genes_raises(self):
        with pytest.raises(ValueError, match="基因字典不能为空"):
            ContentDNA(content_id="id2", source_platform="p", genes={})

    def test_to_vector(self, sample_dna):
        vec = sample_dna.to_vector()
        assert vec.shape[0] == 2
        assert 0.8 in vec

    def test_summary(self, sample_dna):
        s = sample_dna.summary()
        assert s["content_id"] == "test-001"
        assert s["gene_count"] == 2