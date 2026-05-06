"""插件加载器 - 自动发现和管理插件"""
import importlib
import pkgutil
from pathlib import Path
from typing import Dict, Type, Optional

from core.plugin_base import BasePlugin


class PluginLoader:
    """插件管理器：自动发现、注册、获取插件"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.registry: Dict[str, Type[BasePlugin]] = {}
        self.instances: Dict[str, BasePlugin] = {}
    
    def discover(self) -> Dict[str, Type[BasePlugin]]:
        """自动扫描plugins目录，注册所有插件"""
        if not self.plugin_dir.exists():
            return {}
        
        for module_info in pkgutil.iter_modules([str(self.plugin_dir)]):
            module = importlib.import_module(f"{self.plugin_dir.name}.{module_info.name}")
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) 
                    and issubclass(attr, BasePlugin) 
                    and attr is not BasePlugin):
                    self.registry[attr_name] = attr
        
        return self.registry
    
    def get_plugin(self, name: str, config_path: Optional[str] = None) -> Optional[BasePlugin]:
        """获取插件实例（带缓存）"""
        if name not in self.instances:
            plugin_class = self.registry.get(name)
            if plugin_class:
                self.instances[name] = plugin_class(config_path)
        return self.instances.get(name)
    
    def list_capabilities(self) -> Dict[str, list]:
        """列出所有插件的能力"""
        capabilities = {}
        for name, plugin_class in self.registry.items():
            plugin = self.get_plugin(name)
            if plugin:
                capabilities[name] = plugin.get_metadata()
        return capabilities