"""
Configuration management module for the File Agent.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class Config:
    """配置管理类。"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器。
        
        Args:
            config_file: 配置文件路径（可选）
        """
        # 加载环境变量
        load_dotenv()
        
        self.config_file = config_file or "config.yaml"
        self.config_data = {}
        
        # 默认配置
        self.defaults = {
            "ai": {
                "default_provider": "openai",
                "default_model": "gpt-3.5-turbo",
                "max_tokens": 1000,
                "temperature": 0.7
            },
            "file_manager": {
                "default_workspace": "./workspace",
                "max_file_size_mb": 10,
                "backup_enabled": True,
                "backup_dir": "./backups"
            },
            "logging": {
                "level": "INFO",
                "file": "./logs/agent.log",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
        
        self.load_config()
    
    def load_config(self) -> None:
        """加载配置文件。"""
        try:
            config_path = Path(self.config_file)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    if config_path.suffix.lower() == '.json':
                        self.config_data = json.load(f)
                    else:
                        self.config_data = yaml.safe_load(f) or {}
                logger.info(f"Loaded configuration from {config_path}")
            else:
                logger.info("Configuration file not found, using defaults")
                self.config_data = {}

            # 尝试加载本地配置文件（用于敏感信息）
            local_config_path = Path("config.local.yaml")
            if local_config_path.exists():
                try:
                    with open(local_config_path, 'r', encoding='utf-8') as f:
                        local_config = yaml.safe_load(f) or {}

                    # 合并本地配置，本地配置优先级更高
                    self._merge_config(self.config_data, local_config)
                    logger.info(f"Loaded local configuration from {local_config_path}")
                except Exception as e:
                    logger.warning(f"Failed to load local configuration: {e}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.config_data = {}

    def _merge_config(self, base_config: dict, override_config: dict) -> None:
        """合并配置字典，override_config 的值会覆盖 base_config。"""
        for key, value in override_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value
    
    def save_config(self) -> None:
        """保存配置到文件。"""
        try:
            config_path = Path(self.config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.json':
                    json.dump(self.config_data, f, indent=2, ensure_ascii=False)
                else:
                    yaml.dump(self.config_data, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"Saved configuration to {config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值。
        
        Args:
            key: 配置键（支持点分隔的嵌套键，如 'ai.default_provider'）
            default: 默认值
            
        Returns:
            配置值
        """
        # 首先检查环境变量
        env_key = key.upper().replace('.', '_')
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value
        
        # 然后检查配置文件
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                value = None
                break
        
        if value is not None:
            return value
        
        # 最后检查默认配置
        value = self.defaults
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值。
        
        Args:
            key: 配置键（支持点分隔的嵌套键）
            value: 配置值
        """
        keys = key.split('.')
        config = self.config_data
        
        # 创建嵌套字典结构
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_ai_config(self) -> Dict[str, Any]:
        """获取AI相关配置。"""
        # 获取API密钥，优先级：环境变量 > 本地配置文件 > 配置文件
        api_keys = {}
        providers = ["openai", "anthropic", "google", "deepseek"]

        for provider in providers:
            # 1. 首先检查环境变量
            env_key = f"{provider.upper()}_API_KEY"
            api_key = os.getenv(env_key)

            # 2. 如果环境变量没有或是示例值，检查本地配置文件
            if not api_key or api_key.startswith("your_"):
                api_key = self.get(f"api_keys.{provider}")

            api_keys[provider] = api_key

        return {
            "provider": self.get("ai.default_provider", "openai"),
            "model": self.get("ai.default_model", "gpt-3.5-turbo"),
            "max_tokens": self.get("ai.max_tokens", 1000),
            "temperature": self.get("ai.temperature", 0.7),
            "api_keys": api_keys
        }
    
    def get_file_manager_config(self) -> Dict[str, Any]:
        """获取文件管理器相关配置。"""
        return {
            "workspace": self.get("file_manager.default_workspace", "./workspace"),
            "max_file_size_mb": self.get("file_manager.max_file_size_mb", 10),
            "backup_enabled": self.get("file_manager.backup_enabled", True),
            "backup_dir": self.get("file_manager.backup_dir", "./backups")
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志相关配置。"""
        return {
            "level": self.get("logging.level", "INFO"),
            "file": self.get("logging.file", "./logs/agent.log"),
            "format": self.get("logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        }
    
    def validate_config(self) -> Dict[str, Any]:
        """
        验证配置的有效性。
        
        Returns:
            验证结果字典
        """
        issues = []
        
        # 检查AI配置
        ai_config = self.get_ai_config()
        provider = ai_config["provider"]
        
        if provider not in ["openai", "anthropic", "google", "deepseek"]:
            issues.append(f"Invalid AI provider: {provider}")
        
        api_key = ai_config["api_keys"].get(provider)
        if not api_key or api_key.startswith("your_") or api_key == "your_api_key_here":
            issues.append(f"Missing API key for provider: {provider}")
        
        # 检查文件管理器配置
        fm_config = self.get_file_manager_config()
        workspace = Path(fm_config["workspace"])
        
        try:
            workspace.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create workspace directory: {e}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
