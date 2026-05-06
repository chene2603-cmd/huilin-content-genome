from core.plugin_loader import PluginLoader


def test_loader_finds_example_plugin():
    loader = PluginLoader()
    plugins = loader.list_plugins()
    assert "example_analyzer" in plugins