"""
Tests for the Config class.
"""

import pytest
import tempfile
import os
from pathlib import Path

from file_agent.config import Config


class TestConfig:
    """Config测试类。"""
    
    def setup_method(self):
        """每个测试方法前的设置。"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.yaml"
    
    def teardown_method(self):
        """每个测试方法后的清理。"""
        # 清理环境变量
        env_vars = [
            "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "DEEPSEEK_API_KEY",
            "AI_DEFAULT_PROVIDER", "FILE_MANAGER_DEFAULT_WORKSPACE",
            "DEFAULT_AI_PROVIDER", "DEFAULT_WORKSPACE"
        ]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]
    
    def test_default_config(self):
        """测试默认配置。"""
        config = Config(str(self.config_file))
        
        # 测试默认值
        assert config.get("ai.default_provider") == "openai"
        assert config.get("ai.default_model") == "gpt-3.5-turbo"
        assert config.get("file_manager.backup_enabled") is True
    
    def test_environment_variable_override(self):
        """测试环境变量覆盖。"""
        # 设置环境变量
        os.environ["AI_DEFAULT_PROVIDER"] = "anthropic"
        os.environ["FILE_MANAGER_DEFAULT_WORKSPACE"] = "/custom/workspace"

        config = Config(str(self.config_file))

        # 环境变量应该覆盖默认值
        assert config.get("ai.default_provider") == "anthropic"
        assert config.get("file_manager.default_workspace") == "/custom/workspace"
    
    def test_config_file_loading(self):
        """测试配置文件加载。"""
        # 创建配置文件
        config_content = """
ai:
  default_provider: google
  default_model: gemini-pro
  max_tokens: 2000

file_manager:
  default_workspace: ./custom_workspace
  backup_enabled: false
"""
        self.config_file.write_text(config_content)
        
        config = Config(str(self.config_file))
        
        # 验证配置文件值被加载
        assert config.get("ai.default_provider") == "google"
        assert config.get("ai.default_model") == "gemini-pro"
        assert config.get("ai.max_tokens") == 2000
        assert config.get("file_manager.backup_enabled") is False
    
    def test_set_and_save_config(self):
        """测试设置和保存配置。"""
        config = Config(str(self.config_file))
        
        # 设置新值
        config.set("ai.default_provider", "anthropic")
        config.set("ai.custom_setting", "test_value")
        
        # 保存配置
        config.save_config()
        
        # 重新加载配置验证
        new_config = Config(str(self.config_file))
        assert new_config.get("ai.default_provider") == "anthropic"
        assert new_config.get("ai.custom_setting") == "test_value"
    
    def test_get_ai_config(self):
        """测试获取AI配置。"""
        # 设置环境变量
        os.environ["OPENAI_API_KEY"] = "test_openai_key"
        os.environ["ANTHROPIC_API_KEY"] = "test_anthropic_key"
        os.environ["DEEPSEEK_API_KEY"] = "test_deepseek_key"
        
        config = Config(str(self.config_file))
        ai_config = config.get_ai_config()
        
        assert ai_config["provider"] == "openai"
        assert ai_config["model"] == "gpt-3.5-turbo"
        assert ai_config["api_keys"]["openai"] == "test_openai_key"
        assert ai_config["api_keys"]["anthropic"] == "test_anthropic_key"
        assert ai_config["api_keys"]["deepseek"] == "test_deepseek_key"
    
    def test_get_file_manager_config(self):
        """测试获取文件管理器配置。"""
        config = Config(str(self.config_file))
        fm_config = config.get_file_manager_config()
        
        assert "workspace" in fm_config
        assert "backup_enabled" in fm_config
        assert "backup_dir" in fm_config
        assert "max_file_size_mb" in fm_config
    
    def test_validate_config_valid(self):
        """测试有效配置验证。"""
        # 设置有效的API密钥
        os.environ["OPENAI_API_KEY"] = "test_key"
        
        config = Config(str(self.config_file))
        validation = config.validate_config()
        
        assert validation["valid"] is True
        assert len(validation["issues"]) == 0
    
    def test_validate_config_invalid_provider(self):
        """测试无效提供商配置验证。"""
        config = Config(str(self.config_file))
        config.set("ai.default_provider", "invalid_provider")
        
        validation = config.validate_config()
        
        assert validation["valid"] is False
        assert any("Invalid AI provider" in issue for issue in validation["issues"])
    
    def test_validate_config_missing_api_key(self):
        """测试缺少API密钥的配置验证。"""
        # 保存原始环境变量
        original_env = {}
        api_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "DEEPSEEK_API_KEY"]

        for key in api_keys:
            if key in os.environ:
                original_env[key] = os.environ[key]
                del os.environ[key]

        try:
            config = Config(str(self.config_file))
            validation = config.validate_config()

            assert validation["valid"] is False
            assert any("Missing API key" in issue for issue in validation["issues"])
        finally:
            # 恢复原始环境变量
            for key, value in original_env.items():
                os.environ[key] = value
    
    def test_nested_key_access(self):
        """测试嵌套键访问。"""
        config = Config(str(self.config_file))
        
        # 设置嵌套值
        config.set("deep.nested.key", "nested_value")
        
        # 获取嵌套值
        assert config.get("deep.nested.key") == "nested_value"
        
        # 测试不存在的嵌套键
        assert config.get("deep.nonexistent.key", "default") == "default"
