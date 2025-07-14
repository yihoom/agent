"""
Tests for the DeepSeek AI provider.
"""

import pytest
import os
from unittest.mock import Mock, patch

from file_agent.ai_providers import DeepSeekProvider, AIProviderFactory


class TestDeepSeekProvider:
    """DeepSeek提供商测试类。"""
    
    def setup_method(self):
        """每个测试方法前的设置。"""
        self.api_key = "test_deepseek_api_key"
        self.model = "deepseek-chat"
    
    def test_init_success(self):
        """测试DeepSeek提供商初始化成功。"""
        with patch('openai.OpenAI') as mock_openai:
            provider = DeepSeekProvider(self.api_key, self.model)
            
            assert provider.api_key == self.api_key
            assert provider.model == self.model
            
            # 验证OpenAI客户端使用正确的base_url
            mock_openai.assert_called_once_with(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
    
    def test_init_missing_openai(self):
        """测试缺少openai包时的错误处理。"""
        with patch('builtins.__import__', side_effect=ImportError):
            with pytest.raises(ImportError, match="openai package is required"):
                DeepSeekProvider(self.api_key, self.model)
    
    @pytest.mark.asyncio
    async def test_generate_response_success(self):
        """测试成功生成响应。"""
        with patch('openai.OpenAI') as mock_openai:
            # 模拟API响应
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test response"
            mock_response.usage.prompt_tokens = 10
            mock_response.usage.completion_tokens = 20
            mock_response.usage.total_tokens = 30
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            provider = DeepSeekProvider(self.api_key, self.model)
            result = await provider.generate_response("Test prompt")
            
            assert result["success"] is True
            assert result["response"] == "Test response"
            assert result["model"] == self.model
            assert result["usage"]["total_tokens"] == 30
    
    @pytest.mark.asyncio
    async def test_generate_response_error(self):
        """测试API错误处理。"""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai.return_value = mock_client
            
            provider = DeepSeekProvider(self.api_key, self.model)
            result = await provider.generate_response("Test prompt")
            
            assert result["success"] is False
            assert "API Error" in result["error"]
            assert result["model"] == self.model
    
    def test_get_available_models(self):
        """测试获取可用模型列表。"""
        with patch('openai.OpenAI'):
            provider = DeepSeekProvider(self.api_key, self.model)
            models = provider.get_available_models()
            
            assert "deepseek-chat" in models
            assert "deepseek-coder" in models
            assert len(models) >= 2


class TestAIProviderFactoryWithDeepSeek:
    """测试工厂类对DeepSeek的支持。"""
    
    def test_create_deepseek_provider(self):
        """测试创建DeepSeek提供商。"""
        with patch('openai.OpenAI'):
            provider = AIProviderFactory.create_provider(
                "deepseek", 
                "test_api_key"
            )
            
            assert isinstance(provider, DeepSeekProvider)
            assert provider.api_key == "test_api_key"
            assert provider.model == "deepseek-chat"  # 默认模型
    
    def test_create_deepseek_provider_with_custom_model(self):
        """测试创建DeepSeek提供商并指定模型。"""
        with patch('openai.OpenAI'):
            provider = AIProviderFactory.create_provider(
                "deepseek", 
                "test_api_key", 
                "deepseek-coder"
            )
            
            assert isinstance(provider, DeepSeekProvider)
            assert provider.model == "deepseek-coder"
    
    def test_get_supported_providers_includes_deepseek(self):
        """测试支持的提供商列表包含DeepSeek。"""
        providers = AIProviderFactory.get_supported_providers()
        
        assert "deepseek" in providers
        assert "openai" in providers
        assert "anthropic" in providers
        assert "google" in providers
