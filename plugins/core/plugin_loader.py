import importlib
import pkgutil
from typing import Dict
from core.plugin_base import BasePlugin


class PluginLoader:
    """
    自动发现并加载 plugins/ 下所有合法插件。
    约定：
      - 每个插件是一个包，目录名用下划线命名。
      - 包内必须有 analyzer.py 并导出继承自 BasePlugin 的类（类名以 Analyzer 结尾）。
      - 插件实例化时不传参数（由自身读取 config.json）。
    加载失败仅记录警告，不影响其他插件。
    """
    def __init__(self, plugins_package: str = "plugins"):
        self.plugins_package = plugins_package
        self._plugins: Dict[str, BasePlugin] = {}
        self._discover()

    def _discover(self) -> None:
        try:
            package = importlib.import_module(self.plugins_package)
        except ModuleNotFoundError:
            print(f"警告: 未找到插件包 '{self.plugins_package}'")
            return

        for _, name, ispkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
            if not ispkg:
                continue
            try:
                plugin_module = importlib.import_module(f"{name}.analyzer")
                for attr in dir(plugin_module):
                    obj = getattr(plugin_module, attr)
                    if (
                        isinstance(obj, type) and
                        issubclass(obj, BasePlugin) and
                        obj is not BasePlugin and
                        attr.endswith("Analyzer")
                    ):
                        try:
                            instance = obj()
                            self._plugins[name.split(".")[-1]] = instance
                        except Exception as e:
                            print(f"警告: 实例化插件 '{name}' 失败: {e}")
                        break
            except Exception as e:
                print(f"警告: 加载插件包 '{name}' 失败: {e}")

    def get_plugin(self, name: str) -> BasePlugin:
        return self._plugins[name]

    def list_plugins(self) -> Dict[str, BasePlugin]:
        return self._plugins.copy()